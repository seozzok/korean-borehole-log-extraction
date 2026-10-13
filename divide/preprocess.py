
import os

import cv2
import numpy as np

import PIL as plt
from PIL import Image

import fitz
import io
import re

from operator import itemgetter
import itertools
from itertools import groupby

import time
import random
from pprint import pprint


# def get_textchunk(page):

#     textinfo = page.get_texttrace() # tuple

#     text_chunk = []

#     for span in textinfo:
#         print(span['dir'])
#         if span['type'] != 0: continue
#         # print('*' * 100)

#         linewidth = span['linewidth']
#         spacewidth = span['spacewidth']
#         fontsize = span['size']

#         # if ii > 10: break
#         chrs = span['chars']
#         # print(chrs)

#         chnk_dict = {}
#         chnk_char = []
#         for ii, c in enumerate(chrs):
            
            
#             if len(chrs) == 1:
#                 char1 = c[0]
#                 x11 = c[-1][0]
#                 y11 = c[-1][1]
#                 x12 = c[-1][2]
#                 y12 = c[-1][3]

#                 chnk_text = chr(char1)
#                 chnk_bbox = (x11, y11, x12, y12)

#                 chnk_dict['bbox'] = chnk_bbox
#                 chnk_dict['text'] = chnk_text
#                 chnk_dict['char'] = [[chr(char1), (x11, y11, x12, y12)]]

#                 text_chunk += [chnk_dict]
#                 continue
                


#             if ii == 0:
#                 char1 = c[0]
#                 x11 = c[-1][0]
#                 y11 = c[-1][1]
#                 x12 = c[-1][2]
#                 y12 = c[-1][3]
#                 chnk_char += [[chr(char1), (x11, y11, x12, y12)]]
#                 continue

#             char2 = c[0]
#             x21 = c[-1][0]
#             y21 = c[-1][1]
#             x22 = c[-1][2]
#             y22 = c[-1][3]

#             # 가로 텍스트
#             if char1 == ' ':
#                 if (abs(x21 - x11) <= spacewidth*2) and (abs(y21 - y11) <= linewidth*1.1):
#                     # 같은 라인
#                     # print('1')
#                     chnk_char += [[chr(char2), (x21, y21, x22, y22)]]
#                     char1 = c[0]
#                     x11 = c[-1][0]
#                     y11 = c[-1][1]
#                     x12 = c[-1][2]
#                     y12 = c[-1][3]

#                     if ii == len(chrs)-1:
#                         chnk_text = [t[0] for t in chnk_char]
#                         chnk_text = ''.join(chnk_text)
#                         chnk_x1 = min([t[1][0] for t in chnk_char])
#                         chnk_y1 = min([t[1][1] for t in chnk_char])
#                         chnk_x2 = max([t[1][2] for t in chnk_char])
#                         chnk_y2 = max([t[1][3] for t in chnk_char])
#                         chnk_bbox = (chnk_x1, chnk_y1, chnk_x2, chnk_y2)

#                         chnk_dict['bbox'] = chnk_bbox
#                         chnk_dict['text'] = chnk_text
#                         chnk_dict['char'] = chnk_char

#                         text_chunk += [chnk_dict]


#             else:
#                 if (abs(x21 - x11) < fontsize*1.5)  and (abs(y21 - y11) <= linewidth*1.1):
#                     # print('2')
#                     chnk_char += [[chr(char2), (x21, y21, x22, y22)]]
#                     char1 = c[0]
#                     x11 = c[-1][0]
#                     y11 = c[-1][1]
#                     x12 = c[-1][2]
#                     y12 = c[-1][3]

#                     if ii == len(chrs)-1:
#                         chnk_text = [t[0] for t in chnk_char]
#                         chnk_text = ''.join(chnk_text)
#                         chnk_x1 = min([t[1][0] for t in chnk_char])
#                         chnk_y1 = min([t[1][1] for t in chnk_char])
#                         chnk_x2 = max([t[1][2] for t in chnk_char])
#                         chnk_y2 = max([t[1][3] for t in chnk_char])
#                         chnk_bbox = (chnk_x1, chnk_y1, chnk_x2, chnk_y2)

#                         chnk_dict['bbox'] = chnk_bbox
#                         chnk_dict['text'] = chnk_text
#                         chnk_dict['char'] = chnk_char

#                         text_chunk += [chnk_dict]

#                     continue

#             # 세로 텍스트
#             if abs(y21 - y12) < linewidth*1.1:
#                 # print('3')
#                 chnk_char += [[chr(char2), (x21, y21, x22, y22)]]
#                 char1 = c[0]
#                 x11 = c[-1][0]
#                 y11 = c[-1][1]
#                 x12 = c[-1][2]
#                 y12 = c[-1][3]

#                 if ii == len(chrs)-1:
#                     chnk_text = [t[0] for t in chnk_char]
#                     chnk_text = ''.join(chnk_text)
#                     chnk_x1 = min([t[1][0] for t in chnk_char])
#                     chnk_y1 = min([t[1][1] for t in chnk_char])
#                     chnk_x2 = max([t[1][2] for t in chnk_char])
#                     chnk_y2 = max([t[1][3] for t in chnk_char])
#                     chnk_bbox = (chnk_x1, chnk_y1, chnk_x2, chnk_y2)

#                     chnk_dict['bbox'] = chnk_bbox
#                     chnk_dict['text'] = chnk_text
#                     chnk_dict['char'] = chnk_char

#                     text_chunk += [chnk_dict]

#                 continue


#             # 같은 라인이 아니면
#             # 이 전 텍스트까지 하나의 chunk로 묶기
#             chnk_text = [t[0] for t in chnk_char]
#             chnk_text = ''.join(chnk_text)
#             chnk_x1 = min([t[1][0] for t in chnk_char])
#             chnk_y1 = min([t[1][1] for t in chnk_char])
#             chnk_x2 = max([t[1][2] for t in chnk_char])
#             chnk_y2 = max([t[1][3] for t in chnk_char])
#             chnk_bbox = (chnk_x1, chnk_y1, chnk_x2, chnk_y2)

#             chnk_dict['bbox'] = chnk_bbox
#             chnk_dict['text'] = chnk_text
#             chnk_dict['char'] = chnk_char

#             text_chunk += [chnk_dict]
#             # print(chnk_char)

#             # chunk 새롭게 리셋
#             chnk_dict = {}
#             chnk_char = []

#             # before값 재정의
#             char1 = char2
#             x11, y11, x12, y12 = x21, y21, x22, y22
#             chnk_char += [[chr(char1), (x11, y11, x12, y12)]]


#             # 이 때, 마지막 c 일 경우
#             if ii == len(chrs)-1:
#                 chnk_text = chr(char1)
#                 # chnk_x1 = chnk_char[1][0]
#                 # chnk_y1 = chnk_char[1][1]
#                 # chnk_x2 = chnk_char[1][2]
#                 # chnk_y2 = chnk_char[1][3]
#                 chnk_bbox = (x11, y11, x12, y12)

#                 chnk_dict['bbox'] = chnk_bbox
#                 chnk_dict['text'] = chnk_text
#                 chnk_dict['char'] = chnk_char

#                 text_chunk += [chnk_dict]
#                 # print(chnk_char)
                
#     # 
#     # pprint(text_chunk)
#     # pprint([t['text'] for t in text_chunk])

#         # pprint(span)
            

#     return text_chunk

    




def fix_duplicated(origin_array, char_array):
    '''모듈 상 중복되어 읽히는 오류를 해결

    span 단위로 중복될수도,
    character 단위로 중복될수도 있음

    input: <np.array>
    output: <list>


    ''' 
    

    # 위치별로 정렬했을 때, 본래 리스트에서의 index
    # sorted_index 하지말자 --> 순서가 오히려 뒤죽박죽된다.
    # sorted_index = list(np.argsort(np.array(origin_array, dtype=[('x', '<f2'), ('y', '<f2')]), order=('y','x'))) # dtype=[('x', '<i4'), ('y', '<i4')])
    sorted_index = list(range(len(origin_array)))

    ref_index = sorted_index[:]
    for id in range(len(ref_index)-1):
        current_id = ref_index[id+1]
        before_id = sorted_index[sorted_index.index(current_id)-1]

        if char_array[current_id] != char_array[before_id]:
            continue
        
        dist = np.sqrt((origin_array[current_id][0] - origin_array[before_id][0])**2 + \
                       (origin_array[current_id][1] - origin_array[before_id][1])**2)


        if (dist < 2):
            sorted_index.remove(current_id)


    sorted_index.sort()
    origin_array = np.array(origin_array)[np.array(sorted_index)]
    char_array = np.array(char_array)[np.array(sorted_index)]

    
    return sorted_index, list(origin_array), list(char_array)
    



def get_textstruct(page, lines=None):
    if not lines:
        blocks = page.get_text("rawdict")['blocks']
        lines = [l for b in blocks if b['type']==0 for l in b['lines']]

    if not lines:
        return []
    

    spans = [s for l in lines for s in l['spans']]
    spans_origin = [s['origin'] for l in lines for s in l['spans']]
    spans_chars = [s['chars'] for l in lines for s in l['spans']]
    spans_chars = [[c['c'] for c in s] for s in spans_chars]
    spans_chars = [''.join(c) for c in spans_chars]
    
    

    sorted_index_span, spans_origin, spans_chars = fix_duplicated(spans_origin, spans_chars)


    chars_span = [(i, c) for i, s in enumerate(spans) for c in s['chars']]
    chars = [c[1] for c in chars_span if c[0] in sorted_index_span]
    chars_span = [c for c in chars_span if c[0] in sorted_index_span]

    chars_c = [c['c'] for c in chars]
    chars_o = [c['origin'] for c in chars]

    sorted_index = list(range(len(chars_o)))
    ref_index = sorted_index[:]
    for ii, c1 in enumerate(chars_c):
        for jj, c2 in enumerate(chars_c[ii+1:], start=ii+1):
            # print(jj)
            if c1 != c2:
                continue
            else:
                dist = np.sqrt((chars_o[ii][0] - chars_o[jj][0])**2 + \
                    (chars_o[ii][1] - chars_o[jj][1])**2)
                
                if dist < 2:
                    try:
                        sorted_index.remove(jj)
                    except: continue

    sorted_index.sort()
    chars_span = np.array(chars_span)[np.array(sorted_index)]
    
    text_struct = []
    tmp_span = []
    span_no_before = 0
    for i in range(len(chars_span)):
        c = list(chars_span).pop(i)

        span_no = c[0]
        char = c[1]

        if (span_no_before != span_no):
            text_struct += [tmp_span]
            tmp_span = []

        tmp_span += [(*char['bbox'], char['c'])]
        span_no_before = span_no

        if (span_no == sorted_index_span[-1]) and (i == len(chars_span)-1):
            text_struct += [tmp_span]

    

    for i, s in enumerate(text_struct):
        s = sorted(s, key=lambda x: (x[1], x[0]))

        bbox_x0 = min([c[0] for c in s])
        bbox_y0 = min([c[1] for c in s])
        bbox_x1 = max([c[2] for c in s])
        bbox_y1 = max([c[3] for c in s])

        span_text = ''.join([c[4] for c in s])

        span_info = {}
        span_info['bbox'] = (bbox_x0, bbox_y0, bbox_x1, bbox_y1)
        span_info['text'] = span_text
        span_info['char'] = s

        text_struct[i] = span_info # <list>


    return text_struct


# 같은 라인 묶기
# boxes가 들어왔을 때,
# y로 겹치면 같은 라인
# def get_lines_chuck(boxes):
#     return
