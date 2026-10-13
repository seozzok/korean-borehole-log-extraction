
from pprint import pprint

import fitz
import numpy as np
import torch
import torch.nn as nn
import torchvision
import torchvision.models as models
from torchvision.transforms import transforms
from efficientnet_pytorch import EfficientNet
from PIL import Image
import os
import random

import time

import tkinter

from divide.resources.CONFIG import *
from divide.preprocess import get_textstruct
from divide.rule_based import classify_page
from divide.utils import *

from collections import defaultdict


def pdf2img(page):
        pix = page.get_pixmap(dpi=PDF_DPI)
        mode = "RGBA" if pix.alpha else "RGB"
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        return img




class Divider:
    def __init__(self, pdf_path, controller_main_path=None):
        
        
        self.controller_main_path = controller_main_path if controller_main_path else os.path.dirname(os.path.abspath(__file__))
        self.pdf_path = pdf_path
        self.doc = fitz.open(pdf_path)

        # CNN 분류
        self.classes = classes
        self.topk = top_k
        self.model = model

        self.device = device

        # self.model_path = best_model_path  # str
        self.model_path = best_model_path
        if not os.path.exists(self.model_path):
            raise FileNotFoundError('Trained CNN weights not found: %s (weights are not distributed; '
                                    'see README)' % self.model_path)
        self.model = model
        self.model.load_state_dict(torch.load(self.model_path, map_location=self.device))
        self.model.to(self.device)
        self.model.eval()

        # import torchsummary
        # print(self.model)
        # print(torchsummary.summary(model, (3, 354, 250)))


        # data
        self.images = []
        self.page_tlines = [] # -> 이후 과정에 사용될 예정
        self.page_extractable = []
        self.page_text_whole = []

        # print('initialization done')

        # 처리 과정 controller에 전송
        try:
            self.preprocess_process = tkinter.DoubleVar()
            self.divide_process = tkinter.IntVar()
        except:
            self.preprocess_process = self
            self.divide_process = self

    def set(*args):
        pass

    def preprocess(self):

        self.preprocess_process.set(0)
        # print('preprocess start')

        # 이미지 전처리: pdf -> 이미지 변환
        for i in range(len(self.doc)):
            page = self.doc[i]

            page_image = pdf2img(page)
            self.images += [page_image] # Image

            # time.sleep(0.2)
            self.preprocess_process.set((i+1)/len(self.doc)/2)


        # print('image-preprocess done')
        # self.preprocess_process = 1

        # 텍스트 전처리: pdf 텍스트 저장
        for i in range(len(self.doc)):
            page = self.doc[i]

            # 텍스트 저장
            blocks = page.get_text("rawdict")['blocks']
            lines = [l for b in blocks if b['type']==0 for l in b['lines']]
            self.page_tlines += [lines]

            # is_extractable & text_whole
            if not lines:
                self.page_extractable += [0]
                self.page_text_whole += ['']
            else:
                spans = [s for l in lines for s in l['spans']]
                chars = [c for s in spans for c in s['chars']]
                chars = [c['c'] for c in chars]
                text_whole = ''.join(chars).replace(' ', '').replace('\t', '').replace('\n', '').upper()

                ####### 추출이 가능한 지 따지는 알고리즘
                ####### 고도화 필요
                if text_whole.isdigit(): # 페이지 숫자만 포함된 경우
                    self.page_extractable += [0]
                    self.page_text_whole += ['']
                else:
                    self.page_extractable += [1]
                    self.page_text_whole += [text_whole]

            self.preprocess_process.set(0.5 + (i+1)/len(self.doc)/2)



        # self.preprocess_process = 2
            # time.sleep(0.2)

        # print('text-preprocess done')

        # time.sleep(2)
        # self.preprocess_process = 0



    def divide(self, tests_displayed, tests_activated):

        pages_divided = []
        self.page_cnn_predict = []
        ## CNN + 규칙기반


        for page_no, page_image in enumerate(self.images):

            # CNN devide (classification)
            if page_image.size[0] > page_image.size[1]:
                _page_image = page_image.rotate(90, expand=True)
            else:
                _page_image = page_image

            tensor_image = transform(_page_image).unsqueeze(0).to(self.device)
            with torch.no_grad():
                    
                output = model(tensor_image)
                probabilities = nn.functional.softmax(output, dim=1)
                top_k_prob, top_k_classes = torch.topk(probabilities, top_k, dim=1)
                top_k_prob, top_k_classes = top_k_prob[0], top_k_classes[0]

            top_k_classes = top_k_classes.cpu().numpy()
            top_k_prob = top_k_prob.cpu().numpy()

            self.page_cnn_predict += [dict(zip([classes[idx] for idx in top_k_classes], top_k_prob))]



            # 규칙기반 보완 (CNN top-1 >= 0.99 이면 CNN 라벨, 아니면 top-k 텍스트 변형 탐색)
            # 텍스트가 읽히지 않는 페이지는 page_text_whole = '' 이므로 top-1 라벨이 된다
            text_whole = self.page_text_whole[page_no] if self.page_extractable[page_no] else ''
            page_label, _routed = classify_page(text_whole, top_k_classes, top_k_prob)
            pages_divided += [page_label]

            # 한 페이지 완료할 때마다
            # APP 데이터 전송
            self.divide_process.set(page_no+1)



        
        # 원본 <dict>
        # {'시추주상도': [page_id]}
        self.divided_dict = assort_by_test(pages_divided)
        print(self.divided_dict)

        # ui <dict>
        # {'시추주상도': {'active': 1, 'extractable': 1, 'pages': [1, 2, 3]}}
        self.test_info_formatted = ui_postprocess(self.page_extractable, self.divided_dict, tests_displayed, tests_activated)

        # return test_info_formatted
