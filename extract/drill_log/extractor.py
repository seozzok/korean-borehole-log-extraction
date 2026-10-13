
import threading
import tkinter
import time

import numpy as np
import cv2


from extract.drill_log.page_segmentation import *
from extract.drill_log.data_extraction import *
from extract.drill_log.info_extraction import get_raw_info
from extract.drill_log.utils import *

from pprint import pprint

def get_rawText(text_struct):
    return [s['text'] for s in text_struct]


class Extractor(threading.Thread):
    def __init__(self, pagesizeList, imageList, textList):
        super().__init__()

        self.pagesizeList = pagesizeList
        self.imageList = imageList
        self.textList = textList

        self.whole_page = len(self.imageList)

        self.tab = ['LOCA', 'WSTD', 'SAMP', 'CORE', 'CDIA', 'GEOL', 'DISC', 'WETH', 'FRAC', 'ISPT']
        self.name = '시추주상도'
        self.data = {}
        self.raw_text = []
        try:
            self.process = tkinter.DoubleVar()
        except:
            self.process = self
        self.success = [1 for i in range(len(self.pagesizeList))]

    def set(*args):
        pass


    def run(self):

        dataset = {}

        datas = {}
        LOCA = [] 
        WSTD = []
        SAMP = [] 
        CORE = []
        CDIA = []
        GEOL = []
        DISC = []
        WETH = []
        FRAC = []
        ISPT = []

        datas['LOCA'] = LOCA
        datas['WSTD'] = WSTD
        datas['SAMP'] = SAMP
        datas['CORE'] = CORE
        datas['CDIA'] = CDIA
        datas['GEOL'] = GEOL
        datas['DISC'] = DISC
        datas['WETH'] = WETH
        datas['FRAC'] = FRAC
        datas['ISPT'] = ISPT


        bhList = []
        self.process.set(0)
        for page, (pagesize, image, text) in enumerate(zip(self.pagesizeList, self.imageList, self.textList)):
            # 페이지마다 처리

            # for t in text:
            #     print(t['text'])
            self.raw_text.extend([get_rawText(text)])
            # print(self.raw_text)

            try:

                gray_image = np.array(image)
                if gray_image.shape[-1] == 3:
                # color img
                    gray_image = cv2.cvtColor(gray_image, cv2.COLOR_BGR2GRAY)


                # secDict: {(key-bbox x1, y1, x2, y2): [value-bbox x1, y1, x2, y2]}
                secDictInfo, secDictData, hlines_data = main_segmentation(gray_image)

                raw_info_dict = get_raw_info(pagesize, gray_image, text, secDictInfo)
                raw_data_dict = get_raw_data(pagesize, gray_image, text, secDictData)

                # for key, item in raw_data_dict.items():
                #     print(key, ': ', item['key'])


                raw_data_dict = key_matching(raw_data_dict)
                # for key, item in raw_data_dict.items():
                #     print(key, ': ', [x[4] for x in item['val_text']])
                # print(raw_data_dict)

                

                if not raw_data_dict or ('layer_description' not in raw_data_dict.keys()) or ('N' not in raw_data_dict.keys()) or ('layer_thickness' not in raw_data_dict.keys()):
                    # 정상적인 시추주상도 페이지라고 생각하지 않음
                    self.success[page] = 0
                    self.process.set((page+1)/self.whole_page)

                    time.sleep(0.2)
                    continue


                # 일반사항 후처리
                info_dict = text_postprocessing_info(raw_info_dict)
                # 데이터사항 후처리 (텍스트만)
                raw_data_dict = text_postprocessing_data(raw_data_dict)


                data_dict = data_postprocessing(pagesize, gray_image, raw_data_dict, hlines_data)
                # print(data_dict)

                borehole = info_dict['borehole'] if info_dict['borehole'] else borehole
                
                # # # 기존에 존재하는지 확인
                data_in_dataset = dataset.get(borehole, {}) # dataset: 전체 dict

                if not data_in_dataset: # 기존에 존재하지 않을 때
                    # 새로운 borehole이 나타났으므로,
                    # 이 전 애들 formatting 필요
                    if (bhList):
                        borehole_before = bhList[-1]

                        dataset_processed = final_postprocessing(dataset[borehole_before])

                        datas = formatting(dataset_processed, datas)

                        # dataset[borehole] = dataset_processed

                    bhList += [borehole]
                    # 일반사항
                    boreholeDict = info_dict
                    
                    # 데이터사항
                    data_dict = merge_page(data_dict, is_continuation=0, previous_data_dict=None)
                    for k, v in data_dict.items():
                        boreholeDict[k] = v

                    dataset[borehole] = boreholeDict
                    # continue

                    


                else: # 기존에 존재할 때
                    # 데이터사항만 추가
                    # print(data_dict)
                    originList = dataset[borehole]

                    data_dict = merge_page(data_dict, is_continuation=1, previous_data_dict=originList)



                    for k, v in data_dict.items():
                        # originList[k] = data_dict[k]
                    #     originList = data_in_dataset.get(k, [])

                    # #     data_dict = merge_page(originList, is_continuation=1, previous_data_dict=originList)

                    #     new = originList[:]
                    #     new += v

                        data_in_dataset[k] = v

                    dataset[borehole] = data_in_dataset
                    # self.success = 0
                    # self.process.set((page+1)/self.whole_page)

                    # time.sleep(0.2)
                    # continue


                if page == len(self.pagesizeList)-1: # 맨 마지막 페이지 일 때

                    dataset = final_postprocessing(dataset[borehole])

                    datas = formatting(dataset, datas)


            except Exception as e:
                print(e)
                self.success[page] = 0           



            self.process.set((page+1)/self.whole_page)

            time.sleep(0.2)





        self.data = datas # dict

