
import os

import cv2
import numpy as np
import fitz

import PIL as plt
from PIL import Image

import time
import random
from pprint import pprint
# from page_segmentation import *

from extract.drill_log.page_segmentation import *

# from preprocess import get_textstruct
# from text_postprocess import post_processing_info


key_name_variations = {
        'borehole': ['공번', 'HOLENo', 'HOLE No', '시추번호', '시추공번', '조사공번'],
        'date': ['날짜', 'DATE', '조사기간', '조사일', '시추일'],
        'coordinates': ['좌표', '위치', 'LOCATION', '調査場所', '조사장소', 'COORIDINATES', '시추좌표', '시추공좌표', '조사좌표', '조사위치'],
        'coordinates_x': ['X좌표'],
        'coordinates_y': ['Y좌표'], # 위치
        'elevation': ['지반표고', 'ELEVATION', 'ELEV', '標 高', '지 반 고', '시추표고', '표고', '현지반고', '지반고'],
        'watertable': ['지하수위', 'GroundWater', '地下孔內水位', 'GROUNDWATER', '수 심', '공내수위', '공내지하수심도'],
        'holedia': ['공경', '시추공경', '시추구경'],
    }


def get_raw_info(pagesize, img, text_struct, keyval_dict):
    '''
    keyval bbox dict로 부터,
    key 영역에 속하는 text와,
    value 영역에 속하는 text를 추출

    keyval_dict: {(key-bbox): (val-bbox)}
    
    return {(key text): (value text)}'''

    # 위치 재조정 ratio
    pdf_width = pagesize[0]
    pdf_height = pagesize[1]

    img_height, img_width = img.shape
    x_ratio = pdf_width / img_width
    y_ratio = pdf_height / img_height


    # 페이지 내 텍스트 박스를 모두 확인
    # key, value section에 넘어가거나 불필요한 텍스트가 걸쳐져 있을 경우를 제외하기 위함
    text_center = [((s['bbox'][0]+s['bbox'][2])/2, (s['bbox'][1]+s['bbox'][3])/2) for s in text_struct]


    keyval_text_dict = {}

    for k_bbox, v_bbox in keyval_dict.items():
        k_bbox = [p*x_ratio if i%2==0 else p*y_ratio for i, p in enumerate(k_bbox)]
        v_bbox = [p*x_ratio if i%2==0 else p*y_ratio for i, p in enumerate(v_bbox)]
        key_x1, key_y1, key_x2, key_y2 = k_bbox[0], k_bbox[1], k_bbox[0]+k_bbox[2], k_bbox[1]+k_bbox[3]
        val_x1, val_y1, val_x2, val_y2 = v_bbox[0], v_bbox[1], v_bbox[0]+v_bbox[2], v_bbox[1]+k_bbox[3]

        # key_tmp = []
        val_tmp = []
        keytext_tmp = []
        valtext_tmp = []

        for i, s in enumerate(text_center):

            if (val_x1 < s[0] < val_x2) and (val_y1 < s[1] < val_y2):
                # key section에 속하면
                val_tmp += [text_struct[i]]
                valtext_tmp += [text_struct[i]['text']]
                # continue

                # key section에 속하지 않으면
                # value 확인
            if (key_x1 < s[0] < key_x2) and (key_y1 < s[1] < key_y2):
                # key_tmp += [text_struct[i]]
                keytext_tmp += [text_struct[i]['text']]
                # else:
                #     continue

        val_tmp = sorted(val_tmp, key=lambda x: (int(x['bbox'][1]), int(x['bbox'][0])))
        # print([v['text'] for v in val_tmp])
        key_text = ''.join(keytext_tmp).replace(' ', '')
        val_text = ' '.join([v['text'] for v in val_tmp])

        if not key_text:
            key_text = val_text

        keyval_text_dict[key_text] = val_text

    # return keyval_text_dict



    # 매칭
    keyval_text_dict_coded = {}
    for k, v in keyval_text_dict.items():

        for key_coded, variations in key_name_variations.items():
            for variation in variations:
                if variation.replace(' ', '') in k.replace(' ', ''):
                    if key_coded == 'coordinates':
                        if '과업위치' in k:
                            continue
                    keyval_text_dict_coded[key_coded] = v
                    break


    return keyval_text_dict_coded    
        




