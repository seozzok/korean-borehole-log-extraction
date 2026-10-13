

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

from extract.drill_log.page_segmentation import *
from extract.drill_log.utils import *


key_name_variations = {
    'scalebar': ['Scale', 'Scle', '표척', '標尺', '척도', ], # '심도'
    'layer_thickness': ['층후', '두께', '層厚'],
    'N_depth': ['채취심도', '채취깊이',], # '심도', '시료형태및심도', '시료'
    'N': ['N치', 'SPT-N', '관입량', 'BLOWS', '타격회수','N/', 'N값', 'N', '표준관입시험'],
    'layer_description': ['지층설명', 'Description', '기술', '현장관찰기록', '觀察', '관찰', '기사'],
    'layer_name': ['지층명', '土質名', '토질명', '지반명'],
    'sample_name': ['시료번호', '試料番號', '샘플번호', ], # '채취방법', '시료형태및심도', '시료'
    'layer_USCS': ['통일분류', 'USCS', '통U일S분C류S', 'CS', '통U일C분S류C', '통SU일분C류S', 'SU'],
    'TCR_RQD': ['(TCR%)(RQD%)', 'TCR(%)RQD(%)', 'T.C.R/R.Q.D', '코아회수율', 'TCR/RQD', '코아'],
    'TCR': ['TCR(%)', 'TCR', 'RCT', 'CTR'],
    'RQD': ['RQD(%)', 'RQD', 'DQR', 'QRD'],
    'weathered': ['D'],
    'joint_max': ['최대'],
    'joint_min': ['최소'],
    'joint_avg': ['평균'],
}

check_variations = {
    'samp_or_Nd': ['시료', '시료형태및심도'], # 시료번호 vs N-depth # '시료형태및심도'
    'depth_or_Nd': ['심도', '深度'],
    'samp_or_method': ['채취방법', '방법'],
}



def get_raw_data(pagesize, img, text_struct, keyval_dict):
    '''
    keyval bbox dict로 부터,
    key 영역에 속하는 text와,
    value 영역에 속하는 text를 추출

    text_struct: [ {'bbox': (x1, y1, x2, y2),
                'text': (text),
                'char': [(x1, y1, x2, y2, 'char'), (...)]} ]
    keyval_dict: {(key-bbox): (val-bbox)}
    
    return {(key text): {'val_text': (value text), 'val_bbox': ()}'''

    # 위치 재조정 ratio
    pdf_width = pagesize[0]
    pdf_height = pagesize[1]

    img_height, img_width = img.shape
    x_ratio = pdf_width / img_width
    y_ratio = pdf_height / img_height

    # keyval_dict ratio 적용
    for k_bbox, v_bbox in keyval_dict.copy().items():
        keyval_dict.pop(k_bbox)
        k_bbox = [p*x_ratio if i%2==0 else p*y_ratio for i, p in enumerate(k_bbox)]
        v_bbox = [p*x_ratio if i%2==0 else p*y_ratio for i, p in enumerate(v_bbox)]

        keyval_dict[tuple(k_bbox)] = v_bbox

    chars = [c for s in text_struct for c in s['char']]
    texts = [s['text'] for s in text_struct]
    text_bbox = [s['bbox'] for s in text_struct]
    char_center = [((c[0]+c[2])/2, (c[1]+c[3])/2) for c in chars]
    text_center = [((c[0]+c[2])/2, (c[1]+c[3])/2) for c in text_bbox]
    

    key_xsorted = sorted(keyval_dict.keys(), key=lambda x: x[0]) # x 오름차순으로 정렬된 key bbox
    colinfo_dict = dict(zip([v+1 for v in range(len(keyval_dict))], [{'key':[], 'value':[]} for v in range(len(keyval_dict))]))
    for col_no, key in enumerate(key_xsorted, start=1):
        colinfo_dict[col_no]['v_bbox'] = keyval_dict[key]
    # ksection, vsection y기준
    dataSec_startY = key_xsorted[0][1]
    dataSec_endY = keyval_dict[key_xsorted[0]][3]

    # 텍스트 기준으로 탐색
    for text_dict in text_struct:
        text = text_dict['text']
        bbox = text_dict['bbox']
        chars = text_dict['char']
        # print(text, bbox)

        left_outside_text = []
        right_outside_text = []
        in_section_text = []

        if ((bbox[1]+bbox[3])/2 < dataSec_startY) or (dataSec_endY+10 < (bbox[1]+bbox[3])/2): # data 부분이 아님
            continue
        
        for col_no, k_bbox in enumerate(key_xsorted, start=1):
            v_bbox = keyval_dict[k_bbox]

            col_dict = colinfo_dict.get(col_no)

            col_key = col_dict.get('key', [])
            col_value = col_dict.get('value', [])            

            key_x1, key_y1, key_x2, key_y2 = k_bbox
            val_x1, val_y1, val_x2, val_y2 = v_bbox

            if not (key_x1-1 <= (bbox[0]+bbox[2])/2 <= key_x2):
                continue

            if (key_y1 <= (bbox[1]+bbox[3])/2 <= key_y2-2): # key
                # print(col_no, text)
                # key임
                # char이 속하는지도 따지자
                for c in chars:
                    c = list(c)
                    if (c[0]+c[2])/2 <= val_x1-1:
                        left_outside_text += [c]
                    elif (val_x1-1 < (c[0]+c[2])/2 < val_x2):
                        # section에 속하면
                        in_section_text += [c]
                    elif val_x2 <= (c[0]+c[2])/2:
                        right_outside_text += [c]
                    
                if len(left_outside_text)>1 or len(right_outside_text)>1:
                    # 튀어나온 글자가 양 쪽으로 하나를 넘을 때
                    col_key += get_textchunk(in_section_text)
                    # col_key = get_textchunk(col_key)

                    if (left_outside_text) and (col_no != 1):

                        # 여러 column 걸쳐있을 때 있음
                        for cn in range(1, col_no):
                            left_val_x1 = colinfo_dict[cn]['v_bbox'][0]
                            left_val_x2 = colinfo_dict[cn]['v_bbox'][2]

                            for cc in left_outside_text:
                                if left_val_x1 <= (cc[0]+cc[2])/2 <= left_val_x2:
                                    colinfo_dict[cn]['key'] += [cc]
                            colinfo_dict[cn]['key'] = get_textchunk(colinfo_dict[cn]['key'])


                    if (right_outside_text) and (col_no != len(keyval_dict)):

                        # 여러 column 걸쳐있을 때 있음
                        for cn in range(col_no+1, len(colinfo_dict)+1):
                            right_val_x1 = colinfo_dict[cn]['v_bbox'][0]
                            right_val_x2 = colinfo_dict[cn]['v_bbox'][2]

                            for cc in right_outside_text:
                                if right_val_x1 <= (cc[0]+cc[2])/2 <= right_val_x2:
                                    colinfo_dict[cn]['key'] += [cc]
                            colinfo_dict[cn]['key'] = get_textchunk(colinfo_dict[cn]['key'])

                else:
                    col_key += [[*bbox, text]]
                
                # break

            if (val_y1-10 <= (bbox[1]+bbox[3])/2 <= val_y2+10): # value

                # value임
                # char이 속하는지도 따지자
                for c in chars:
                    c = list(c)
                    if (c[0]+c[2])/2 <= val_x1-1:
                        left_outside_text += [c]
                    elif (val_x1-1 < (c[0]+c[2])/2 < val_x2):
                        # section에 속하면
                        in_section_text += [c]
                    elif val_x2 <= (c[0]+c[2])/2:
                        right_outside_text += [c]
                # print(in_section_text)    
                if len(left_outside_text)>1 or len(right_outside_text)>1:
                    # 튀어나온 글자가 양 쪽으로 하나를 넘을 때
                    col_value += get_textchunk(in_section_text)
                    # col_value = get_textchunk(col_value)

                    if (left_outside_text) and (col_no != 1):
                        
                        # 여러 column 걸쳐있을 때 있음
                        for cn in range(1, col_no):
                            left_val_x1 = colinfo_dict[cn]['v_bbox'][0]-1
                            left_val_x2 = colinfo_dict[cn]['v_bbox'][2]

                            for cc in left_outside_text:
                                if left_val_x1 <= (cc[0]+cc[2])/2 <= left_val_x2:
                                    colinfo_dict[cn]['value'] += [cc]

                            colinfo_dict[cn]['value'] = get_textchunk(colinfo_dict[cn]['value'])

                    if (right_outside_text) and (col_no != len(keyval_dict)):

                        # 여러 column 걸쳐있을 때 있음
                        for cn in range(col_no+1, len(colinfo_dict)+1):
                            right_val_x1 = colinfo_dict[cn]['v_bbox'][0]-1
                            right_val_x2 = colinfo_dict[cn]['v_bbox'][2]

                            for cc in right_outside_text:
                                if right_val_x1 <= (cc[0]+cc[2])/2 <= right_val_x2:
                                    colinfo_dict[cn]['value'] += [cc]

                            colinfo_dict[cn]['value'] = get_textchunk(colinfo_dict[cn]['value'])

                else:
                    col_value += [[*bbox, text]]
 
                break

            col_key = sorted(col_key, key=lambda x: (x[1], x[0]))
            col_value = sorted(col_value, key=lambda x: (x[1], x[0]))
            
            col_dict['key'] = col_key
            col_dict['value'] = col_value
            

            colinfo_dict[col_no] = col_dict
            break

    # key인 경우, text만
    for col_no, col_dict in colinfo_dict.items():
        # col_key = sorted(col_dict['key'], key=lambda x: (x[1], x[0]))
        col_key = [t[4] for t in col_dict['key']]
        keys = ''.join(col_key).replace(' ', '').upper()
        colinfo_dict[col_no]['key'] = keys

        # value 위치 sort
        values = sorted(col_dict['value'], key=lambda x: (x[1], x[0]))
        colinfo_dict[col_no]['value'] = values
    # print(colinfo_dict)
    return colinfo_dict


def key_matching(colinfo_dict):

    key_matched_by_keycode = dict(zip(key_name_variations.keys(), [[] for i in range(len(key_name_variations))])) 
    # {key_code: [col_no, ..]}

    for col_no, col_info in colinfo_dict.items():
        key = col_info['key']
        key_code = []

        if key == 'D':
            key_code = ['weathered']

            key_matched_by_keycode['weathered'] = [col_no]
            # key_code =[]
        
        else:
            for key_coded, variations in key_name_variations.items():
                if key_coded == 'weathered': continue
                elif key_coded == 'TCR':
                    if 'Q' in key:
                        continue
                elif key_coded == 'RQD':
                    if 'T' in key:
                        continue
                for variation in variations:
                    if variation.upper() in key:
                        # key_code += [key_coded]

                        key_matched = key_matched_by_keycode.get(key_coded, [])
                        key_matched += [col_no]
                        key_matched_by_keycode[key_coded] = key_matched
                        break
        col_info['key_code'] = key_code

        # colinfo_dict[col_no] = col_info

        # print(key, col_info['key_code'])

    # print(key_matched_by_keycode)
    key_matched_sorted = sorted(key_matched_by_keycode, key=lambda x: len(key_matched_by_keycode[x]))

    matched_already = []
    for key_code in key_matched_sorted:
        cols = key_matched_by_keycode[key_code] # [1, 2, 3]

        cols = list(set(cols) - set(matched_already)) # [1, 2, 3]

        col_texts = [colinfo_dict[col]['key'] for col in cols]

        if len(cols)== 0:
            continue

        elif len(cols) == 1:
            if key_code == 'N':
                col_text = colinfo_dict[col_no]['key']
                if '1020' in col_text:
                    key_matched_by_keycode[key_code] = []
                    continue
                
            key_matched_by_keycode[key_code] = cols
            matched_already += cols

            
        else:

            if key_code == 'N':

                for col_no in cols[:]:
                    col_text = colinfo_dict[col_no]['key']

                    if ('N치' in col_text) and ('1020' not in col_text):
                        cols = [col_no]
                        key_matched_by_keycode[key_code] = cols
                        matched_already += cols
                        break

                    elif ('관입량' in col_text) and ('1020' not in col_text):
                        cols = [col_no]
                        key_matched_by_keycode[key_code] = cols
                        matched_already += cols
                        break

                    elif ('30CM' in col_text) and ('1020' not in col_text):
                        cols = [col_no]
                        key_matched_by_keycode[key_code] = cols
                        matched_already += cols
                        break

                    elif ('N값' in col_text) and ('1020' not in col_text):
                        cols = [col_no]
                        key_matched_by_keycode[key_code] = cols
                        matched_already += cols
                        break



            elif key_code == 'joint_max':

                for col_no in cols[:]:
                    col_text = colinfo_dict[col_no]['key']

                    if ('비고' in col_text):
                        cols.remove(col_no)
                        continue
                    
                key_matched_by_keycode[key_code] = cols
                matched_already += cols

            elif key_code == 'joint_min':

                for col_no in cols[:]:
                    col_text = colinfo_dict[col_no]['key']

                    if ('비고' in col_text):
                        cols.remove(col_no)
                        continue
                    
                key_matched_by_keycode[key_code] = cols
                matched_already += cols

            elif key_code == 'joint_avg':

                for col_no in cols[:]:
                    col_text = colinfo_dict[col_no]['key']

                    if ('비고' in col_text):
                        cols.remove(col_no)
                        continue
                    
                key_matched_by_keycode[key_code] = cols
                matched_already += cols


    matched_key_codes = [key for key in key_matched_by_keycode.keys() if key_matched_by_keycode[key]]
    unmatched_cols = sorted(list(set(range(1, len(colinfo_dict)+1)) - set(matched_already)))

    ## 심도 처리
    # 심도 무조건 있음
    depth_col = []
    for col_no in unmatched_cols:

        # 한 column을 봤을 때
        col_text = colinfo_dict[col_no]['key']

        for key_coded, variations in check_variations.items():
            for variation in variations:
                if variation.upper() in col_text:
                    # variation에 해당

                    if key_coded == 'samp_or_Nd':
                        
                        if ('sample_name' in matched_key_codes) and ('N_depth' not in matched_key_codes):
                            # sample name이 이미 있으면
                            # N 채취 심도일 것
                            key_code = 'N_depth'
                            key_matched_by_keycode[key_code] = [col_no]
                            matched_already += [col_no]
                            matched_key_codes += [key_code]

                        elif ('sample_name' not in matched_key_codes) and ('N_depth' in matched_key_codes):
                            # N 채취 심도 이미 있으면
                            # sample_name 일 것
                            key_code = 'sample_name'
                            key_matched_by_keycode[key_code] = [col_no]
                            matched_already += [col_no]
                            matched_key_codes += [key_code]


                        elif ('sample_name' in matched_key_codes) and ('N_depth' in matched_key_codes):
                            pass
                    
                        elif ('sample_name' not in matched_key_codes) and ('N_depth' not in matched_key_codes):
                            key_code = 'N_depth_samp'
                            key_matched_by_keycode[key_code] = [col_no]
                            # key_code = 'sample_name'
                            # key_matched_by_keycode[key_code] = [col_no]
                            matched_already += [col_no]
                            matched_key_codes += [key_code]


                        break


                    elif key_coded == 'depth_or_Nd':
                        if '시료' in col_text:
                            continue

                        depth_col += [col_no]
                        if ('N_depth' in matched_key_codes) and ('scalebar' not in matched_key_codes):
                            # 시추주상도: '심도' 열은 무조건 있음
                            key_code = 'scalebar'
                            key_matched_by_keycode[key_code] = [col_no]
                            matched_already += [col_no]
                            matched_key_codes += [key_code]


                        elif (('N_depth' not in matched_key_codes) and ('N_depth_samp' not in matched_key_codes)) and ('scalebar' in matched_key_codes):
                            # (('N_depth' not in matched_key_codes) and ('N_depth_samp' not in matched_key_codes)) --> 둘다 N_depth 담고 있다.
                            # if (col_no not in matched_already) and (len(depth_col) == 2):
                            if len(depth_col) == 2:
                                key_code = 'N_depth'
                                key_matched_by_keycode[key_code] = [col_no]
                                matched_already += [col_no]
                                matched_key_codes += [key_code]


                        elif ('N_depth' in matched_key_codes) and ('scalebar' in matched_key_codes):
                            pass

                        elif (('N_depth' not in matched_key_codes) and ('N_depth_samp' not in matched_key_codes)) and ('scalebar' not in matched_key_codes):
                            # if col_no not in matched_already:
                            if len(depth_col) == 1:
                                key_code = 'scalebar'
                                key_matched_by_keycode[key_code] = [col_no]
                                matched_already += [col_no]
                                matched_key_codes += [key_code]

                            elif len(depth_col) == 2:
                                key_code = 'N_depth'
                                key_matched_by_keycode[key_code] = [col_no]
                                matched_already += [col_no]
                                matched_key_codes += [key_code]


                        break


                    elif key_coded == 'samp_or_method':
                        if ('sample_name' not in matched_key_codes):
                            key_code = 'sample_name'
                            key_matched_by_keycode[key_code] = [col_no]
                            matched_already += [col_no]
                            matched_key_codes += [key_code]

                        
                        else:
                            pass

                        break

    key_value_dict = {}
    for key_code, cols in key_matched_by_keycode.items():
        # key_matched_by_keycode {key_code [1, 2, 3]}

        for col in cols:

            values = colinfo_dict[col]['value']
            # if not values: continue
    
            # texts = [v[4] for v in values]
            # sec = [tuple(v[:4]) for v in values]
            

            # texts = value['val_text']
            # sec = value['val_bbox']
        #     col_text = [colinfo_dict[col]['key'] for col in cols]


            key_value_dict[key_code] = {}

            key_value_dict[key_code]['val_text'] = values
            key_value_dict[key_code]['val_bbox'] = colinfo_dict[col]['v_bbox']
            

    return key_value_dict

    

########### DATA POST-PROCESSING

def _lines_of_interest(hlines_mask, interest_region):
    '''
    interest_region: bbox = [x1, y1, x2, y2]'''
    height, width = hlines_mask.shape
    column_mask = np.zeros((int(height), int(width)), dtype=np.uint8)

    x1, y1, x2, y2 = interest_region[:]
    column_mask[int(y1)-1:int(y2)+1, int(x1)-1:int(x2)+1] = 255

    line_mask = cv2.bitwise_and(hlines_mask, column_mask)

    hlines = mask2lines(line_mask, 'h')
    hlines = [h for h in hlines if (h[2]-h[0])>(x2-x1)*0.9] ############ 2407: 0.8 -> 0.9 변경
    return hlines



# _layer_name = ['매립', '전답', '맥암', '퇴적', '붕적', '충적', '잔적', '풍화토', '풍화암', '연암', '보통암', '경암', '성토', '콘크리트', '표토', \
#                '자갈모래점토', '점토자갈모래', '핵석', '잡석치환', '점토층', '실트질모래', '자갈질모래', '점토질자갈', '모래질점토', '점토질모래', '기반암층']
korean_regex = r"[가-힣]"
def _bind_layer(text_struct, lines_in_descriptionCol):

    descriptionLine_YCood = [l[3] for l in lines_in_descriptionCol[1:]]
    layer_text = text_struct['layer_description']['val_text'][:]
    # layer_thickness_YCoord = [l['coord'] for l in layer_dict.values()]

    layer_description = []
    layer_description = [[] for block in range(len(descriptionLine_YCood))]
    _tmpLayer = []
    # layer_id = 1

    # 텍스트 기준으로 보자
    
    for layer_id, line_coord in enumerate(descriptionLine_YCood[:]):

        text_exists = 0
        _del = 0
        for i, text in enumerate(layer_text[:]):

            text_exists = 1
            text_coord = (text[1]+text[3])/2
            line_coord = line_coord+10 if (layer_id == len(descriptionLine_YCood)) else line_coord

            if text_coord <= line_coord:
                text = text[4] if ('종료' not in text[4]) and ('다음장' not in text[4].replace(' ', '')) and ('End' not in text[4]) else ''
                _tmpLayer += [text]

                # layer_text.pop(i-_del)
                _del += 1
            else:
                # 담겨있던 _tmpLayer 추가
                layer_description[layer_id] = _tmpLayer

                _tmpLayer = []

                layer_text = layer_text[_del:]
                break
        
        _tmpLayer = [t for t in _tmpLayer if t]
        if _tmpLayer:
            layer_description[layer_id] = _tmpLayer
            break

    # _tmpLayer = [t for t in _tmpLayer if t]
    # if _tmpLayer:
    #     layer_description[layer_id-1] = _tmpLayer


    text_struct['layer_description'] = layer_description
    # text_struct['layer_dict'] = layer_dict

    # print(layer_description)
    return text_struct


def _bind_layername(text_struct, lines_in_targetCol, targetCol): # lines_in_target: layer_name, layer_USCS
    layer_dict = text_struct['layer_dict'].copy()

    layer_dict = [[l['coord']-1, l['coord'], l['coord']] for l in layer_dict.values()]

    targetLine_YCood = [l[3] for l in lines_in_targetCol[1:]]
    layer_text = targetCol['val_text']
    layer_description = []
    layer_description = [[] for v in range(len(layer_dict))]
    _tmpLayer = []
    layer_id = 1


    # 1차기준. 층후 열과 라인의 개수가 똑같으면, 그대로 맵핑하면 됨 ==> 대부분
    # 만약 개수가 다르면, coord으로 판단해야한다
    if len(layer_dict) == len(targetLine_YCood):
        
        _max_line = 100000
        
        for layer_id, line_coord in enumerate(targetLine_YCood[:]):

            _del = 0
            text_exists = 0
            
            for i, text in enumerate(layer_text[:]):
                text_exists = 1
                text_coord = (text[1]+text[3])/2

                if text_coord <= line_coord:
                    text = text[4] if ('색' not in text[4]) else ''
                    _tmpLayer += [text]

                    # layer_text.pop(i-_del)
                    _del += 1

                else:
                    # 이미 있던 _tmpLayer 담기
                    layer_description[layer_id] = _tmpLayer
                    _tmpLayer = []

                    layer_text = layer_text[_del:]
                    break
                
            _tmpLayer = [t for t in _tmpLayer if t]
            if _tmpLayer:
                layer_description[layer_id] = _tmpLayer
                break
        
        # _tmpLayer = [t for t in _tmpLayer if t]
        # if _tmpLayer:
        #     layer_description[layer_id-1] = _tmpLayer

        layer_description = [''.join(des) for des in layer_description]

    else:

        targetLine_YCood = [l[3] for l in lines_in_targetCol]
        for text in layer_text:
            if '색' in text: continue

            line_coord = targetLine_YCood[layer_id]
            if ((text[1]+text[3])/2 <= line_coord):
                _tmpLayer.append(text[4])

            else:
                # 이미 있던 _tmpLayer 담기
                # 어디에 담냐?
                for id, coords in enumerate(layer_dict[layer_id-1:], start=layer_id-1):
                    if line_coord in coords:
                        break

                # layer_description += [_tmpLayer]
                layer_description[id] += _tmpLayer

                while True:
                    # print(layer_description)
                    if (id == 0) or (id <= layer_id-1):
                        break
                    if layer_description[id-1] == []:
                        layer_description[id-1] += _tmpLayer
                        id = id-1
                    else:
                        break

                layer_id += 1

                _tmpLayer = []
                # 마지막 라인이면
                _tmpLayer.append(text[4])
                if (layer_id >= len(targetLine_YCood)):
                    break

        if (_tmpLayer) and (layer_id == len(targetLine_YCood)-1):
            layer_description[-1] += _tmpLayer
        elif (_tmpLayer) and (layer_id < len(targetLine_YCood)-1):
            layer_description[-2] += _tmpLayer
        #     layer_description[-1] += _tmpLayer


        # layer_description = [''.join(des) for des in layer_description if des]
        # print(layer_description)
        layer_description = [''.join(des) for des in layer_description]

        # while len(layer_description) != len(descriptionLine_YCood)-1:
        #     layer_description.append('')

    return layer_description


def _get_scaling_deltaY(text_struct, hlines_mask):
    # 페이지 내 scale 구하기

    thickness = text_struct.get('layer_thickness', {'val_text': [], 'val_bbox': []})
    scalebar = text_struct.get('scalebar', {'val_text': []})

    _by_scalebar = 1
    _by_thickness = 0

    # scalebar가 척도 역할로 정상적으로 존재하면,
    # 무조건 scalebar 기준으로 추출
    while _by_scalebar:
        if (len(scalebar['val_text']) >= 3):

            scalebar = scalebar['val_text'][:3] # 세개만 보자

            scalebar_nums = [float(only_nums(v[4])) for v in scalebar]
        
            diff1, diff2 = scalebar_nums[1]-scalebar_nums[0], scalebar_nums[2]-scalebar_nums[1] # text

            if diff1 == diff2:
                coord1 = scalebar[0][1]
                coord2 = scalebar[1][1]
                coord3 = scalebar[2][1]

                deltaY1 = diff1 / (coord2 - coord1)
                deltaY2 = diff2 / (coord3 - coord2)

                scaling_deltaY = (deltaY1+deltaY2)/2# 한 픽셀이 나타내는 실제 두께
                break
            else:
                _by_scalebar = 0
                _by_thickness = 1
                # reference_col = text_struct.get('scalebar', {'val_text': []})

                # lines_in_col = _lines_of_interest(hlines_mask, reference_col['val_bbox'])
                # scaling_deltaY = 20 / (lines_in_col[-1][3] - lines_in_col[0][3])
        else:
            _by_scalebar = 0
            _by_thickness = 1



    # scalebar가 제대로 존재하지 않는 경우,
    # thickness로 판단 (두께 열은 모든 보고서에 무조건 존재)
    while _by_thickness:
        if len(thickness['val_text']) >= 2:
            # 두께 데이터 개수가 2개 이상일 때
            # 두 선 사이 -> 두께 ==> scale 구할 수 있다
            reference_col = thickness
            lines_in_col = _lines_of_interest(hlines_mask, reference_col['val_bbox'])
            referenceText_YCood = [t[3] for t in reference_col['val_text']]
            referenceLine_YCood = [l[3] for l in lines_in_col]

            # 선 매칭
            scaling_dict = {}
            line_id = 1
            for text_id, text_y in enumerate(referenceText_YCood):
            # 가장 가까운 line과 층후 text 매치하기
                _min = abs(text_y - referenceLine_YCood[line_id])
                for id, line_y in enumerate(referenceLine_YCood[line_id+1:]):
                    diff = abs(text_y-line_y)
                    if diff > _min:
                        scaling_dict[referenceLine_YCood[line_id]] = reference_col['val_text'][text_id][4]
                        line_id += 1
                        break
            
            _tmp = []
            for id, coord in enumerate(list(scaling_dict.keys())[:-1]):
                p_coord1 = coord
                p_coord2 = list(scaling_dict.keys())[id+1]

                real_thick = float(scaling_dict[p_coord2])

                scaling_deltaY = real_thick/(p_coord2-p_coord1)# 한 픽셀이 나타내는 실제 두께

                _tmp += [scaling_deltaY]

            try:
                scaling_deltaY = sum(_tmp) / len(_tmp)
            except:
                reference_col = thickness
                # if not scalebar:
                lines_in_col = _lines_of_interest(hlines_mask, reference_col['val_bbox'])
                scaling_deltaY = 20 / (lines_in_col[-1][3] - lines_in_col[0][3])
            break

        else: 
            # 심도가 'scalebar'가 아니거나,
            # 두께 데이터 개수가 하나일 때,
            # 일반적인 두께 20m를 사용
            reference_col = thickness
            # if not scalebar:
            lines_in_col = _lines_of_interest(hlines_mask, reference_col['val_bbox'])
            scaling_deltaY = 20 / (lines_in_col[-1][3] - lines_in_col[0][3])
            break

    return scaling_deltaY




def _mapping_N_depth(text_struct, hlines_mask, converted_hlines, scaling_deltaY):
    
    N_value = text_struct.get('N', {'val_text': [], 'val_bbox': []})
    N_depth = text_struct.get('N_depth', {'val_text': []})

    _n_tkickness = []
    _n_depth = []
    if not N_depth['val_text']:
        # N치 채취심도가 없는 경우
        # N치가 적힌 텍스트 위치를 기준으로 위치를 정해야 한다
        # lines_in_descriptionCol = _lines_of_interest(hlines_mask, text_struct['N_depth']['val_bbox'])

        reference = _lines_of_interest(hlines_mask, text_struct['N']['val_bbox'])[0][3]
        
        for n_text in N_value['val_text']:
            # print(reference)
            text_coord = (n_text[1]+n_text[3])/2
            
            n_thickness = round(round((text_coord - reference) * scaling_deltaY, ndigits=1)/0.5)*0.5

            _n_tkickness += [n_thickness]
            reference = text_coord

    else:
        # N치 채취심도가 있는 경우

        # 우선 개수 비교
        ############# 수정 필요
        if len(N_depth['val_text']) == len(N_value['val_text']):
            # 개수가 같으면, 그냥 mapping
            for n_depth, n_value in zip(N_depth['val_text'], N_value['val_text']):
                _n_depth += [n_depth[4]]

        else:
            for n_id, n_text in enumerate(N_value['val_text']):
                reference = converted_hlines[0][3] if (n_id==0) else reference

                depth = 0
                for depth_text in N_depth['val_text']:
                    # 같은 라인인지 체크
                    if depth_text[1]-5 <= (n_text[1]+n_text[3])/2 <= depth_text[3]+5:
                        depth = depth_text[4]
                        break

                if (not depth): # 같은 라인인 채취심도가 없으면
                    text_coord = (n_text[1]+n_text[3])/2
                    if not _n_depth: 
                        n_thickness = round(round((text_coord - reference) * scaling_deltaY, ndigits=1)/0.5)*0.5
                        _n_tkickness += [n_thickness]
                        reference = text_coord
                    else: # 마지막 라인일 때
                        n_thickness = round(round((text_coord - reference) * scaling_deltaY, ndigits=1)/0.5)*0.5
                        _n_depth += [float(_n_depth[-1]) + n_thickness]
                        reference = (n_text[1]+n_text[3])/2
                    
                else:
                    # 같은 라인인 채취심도 있을 때
                    if _n_tkickness:
                        text_coord = (n_text[1]+n_text[3])/2
                        # n_thickness = round(round((text_coord - converted_hlines[0][3]) * scaling_deltaY, ndigits=1)/0.5)*0.5
                        n_thickness = round(round((text_coord - reference) * scaling_deltaY, ndigits=1)/0.5)*0.5
                        # _n_tkickness += [n_thickness - _n_tkickness[-1]]
                        _n_tkickness += [n_thickness]
                        reference = text_coord
                    else:
                        _n_depth += [depth]
                        reference = (n_text[1]+n_text[3])/2


    text_struct['N_depth'] = _n_depth

    text_struct['N_thickness'] = _n_tkickness

    return text_struct


def __find_nearest(ref_coord, codomain_col):
    # 가장 가까운 라인 찾기
    # 같은 줄이면서, 가장 가까운 라인을 찾는다 (margin = 5: N치 채취심도 찾을 때와 동일)

    matched_text = ''
    _min = 100
    codomain_text = codomain_col['val_text']
    for text in codomain_text:
        # 같은 라인인지 체크
        if text[1]-5 <= ref_coord <= text[3]+5:
            _diff = abs(ref_coord - (text[1]+text[3])/2)
            if _diff < _min:
                matched_text = text[4]
                _min = _diff
        else:
            continue

    return matched_text



def __match_line(text_struct, hlines_mask, target_col, scaling_deltaY):

    # TCR, RQD, weathered, joint 높이 맞추기
    # 1. (무조건) 층후에서 값 찾기,
    # 1. (무조건) 심도에서 값 찾기,
    # 3. N치에서 값 찾기,
    # 4. 없는 경우 --> scaling Y 이용

    _by_thickness = 1
    _by_scalebar = 1
    _by_nvalue = 0
    _by_scaling = 0

    thickness = []
    depth = []

    _to_find_num = len(target_col['val_text'])


    ##################################### updated: 240110 16:00
    # 텍스트 위치에 따라 라인 매칭
    # 글씨가 없더라도 맵핑하자!!!!
    lines_in_target = _lines_of_interest(hlines_mask, target_col['val_bbox'])
    line_index_matching = [[] for l in range(len(lines_in_target)-1)]
    _line_index_interest = []
    mapping_value = ['' for l in range(len(lines_in_target)-1)]
    textY_in_target = [(t[1]+t[3])/2 for t in target_col['val_text']]
    text_in_target = [t[4] for t in target_col['val_text']]
    _del = 0
    if not text_in_target: # 텍스트가 없더라도, 중간에 라인이 존재한다면 맵핑하자 # 맨 윗 줄만 맵핑하면 됨. 어차피 중간엔 없으니까.
        if len(lines_in_target) > 2:
            line_index_matching[0] = [0, 1]
            _line_index_interest += [0, 1]
        else: # 중간에 라인 없을 때
            return [], []
    else:
        for id, line in enumerate(lines_in_target[1:], start=1):
            for i, textY in enumerate(textY_in_target[_del:]):
                if textY < line[1]:
                    line_index_matching[id-1] = [id-1, id]
                    _line_index_interest += [id-1, id]
                    # textY_in_target.pop(i-_del)
                    # text = text_in_target.pop(i-_del)
                    text = text_in_target[_del]
                    _del += 1

                    # rqd 값
                    if mapping_value[id-1]:
                        # if block_id == len(mapping_value)-1:
                        mapping_value[id-1] = mapping_value[id-1] + '/' + text       
                    else:
                        mapping_value[id-1] = text
                        # 심도 set
                else:
                    break

    _line_index_interest = list(set(_line_index_interest))

    lines_in_target = _lines_of_interest(hlines_mask, target_col['val_bbox'])
    targetLine_YCood = [l[3] for l in lines_in_target]
    _in_thickness = ['' for l in range(len(targetLine_YCood))]
    _in_depth = ['' for l in range(len(targetLine_YCood))]
    _in_N = ['' for l in range(len(targetLine_YCood))]
    for i, yCoord in enumerate(targetLine_YCood[1:], start=1):
        _thick_matched = __find_nearest(yCoord, text_struct['layer_thickness']) # 값 하나
        _depth_matched = __find_nearest(yCoord, text_struct['scalebar']) # 값 하나
        _N_matched = __find_nearest(yCoord, text_struct['N']) # 값 하나

        # 심도에서 찾은 경우, 조건 걸기
        _depth_matched = str(only_nums(_depth_matched)) if only_nums(_depth_matched) and float(only_nums(_depth_matched))<= 100 else ''
        _N_matched = str(only_nums(_N_matched)) if '/' not in _N_matched else ''
        if i in _line_index_interest:
            _in_thickness[i] = _thick_matched
            _in_depth[i] = _depth_matched
            _in_N[i] = _N_matched
    

    depth = ['' for l in range(len(targetLine_YCood))]
    thickness = ['' for l in range(len(targetLine_YCood))]
    _start_scaling = 0
    for id in _line_index_interest:
        _thick_matched = _in_thickness[id]
        _depth_matched = _in_depth[id]
        _N_matched = _in_N[id]

        if id == 0:
            # depth[id] = (lines_in_target[id][3], 0)
            # thickness[id] = (lines_in_target[id][3], 0)
            continue

        if _depth_matched or _N_matched: # 무조건 depth
            depth[id] = (lines_in_target[id][3], _depth_matched) if _depth_matched else (lines_in_target[id][3], _N_matched)
            continue

        if _thick_matched:
            thickness[id] = (lines_in_target[id][3], _thick_matched)
            continue

        if (not _thick_matched) or (not _depth_matched) or (not _N_matched):
            # 아무것도 매치되는 게 없을 때
            coord = lines_in_target[id][3]
            reference = lines_in_target[0][3]

            thickness_calc = round((coord - reference) * scaling_deltaY, ndigits=1)

            thickness[id] = (lines_in_target[id][3], thickness_calc)

            _start_scaling = 1 if id == 1 else 0
            continue


    __depth_check = [v for v in depth if v]

    if __depth_check:
        _all_depth = 0
        while not _all_depth:
            for i, (dep, th) in enumerate(zip(depth, thickness)):
                if i == 0: 
                    # depth[i] = 0
                    # thickness[i] = 0
                    continue
                
                if dep: # depth 값이 있을 경우
                    # depth[i] = dep[1]
                    continue
                elif th: # thickness 값이 있을 경우
                    if depth[i-1]:
                        coord = th[0]
                        reference = depth[i-1][0]

                        thickness_calc = round(abs((coord - reference)) * scaling_deltaY, ndigits=1)

                        depth[i] = (coord, round(float(depth[i-1][1]) + thickness_calc, 1))

                    elif depth[i+1]:
                        coord = th[0]
                        reference = depth[i+1][0]

                        thickness_calc = round(abs((coord - reference)) * scaling_deltaY, ndigits=1)

                        depth[i] = (coord, round(float(depth[i+1][1]) - thickness_calc, 1))

                else: # depth, thickness 둘 다 없을 경우
                    # 매칭되지 않아도 될 끝 값일 것
                    depth[i] = 0
            _all_depth = 0 if '' in depth[1:] else 1
        thickness = []

    else: # 거의 없음
        mapping_value = [v for v in mapping_value if v]
        return mapping_value, [['', ''] for v in range(len(mapping_value))]


    # thickness를 이용
    for block_id, lines in enumerate(line_index_matching):
        if not lines: continue
        id1 = lines[0]
        id2 = lines[1]

        if id1 == 0:
            depth1 = 0
            depth2 = depth[id2][1]
        else:
            depth1 = depth[id1][1]
            depth2 = depth[id2][1]
        line_index_matching[block_id] = [depth1, depth2]

    depth = line_index_matching


    mapping_value = [v for v in mapping_value if v]
    depth = [v for v in depth if v]

    return mapping_value, depth



def _mapping_rockprop_depth(text_struct, hlines_mask, scaling_deltaY):

    tcr_rqd = text_struct.get('TCR_RQD', {'val_text': [], 'val_bbox': []})
    tcr = text_struct.get('TCR', {'val_text': [], 'val_bbox': []})
    rqd = text_struct.get('RQD', {'val_text': [], 'val_bbox': []})
    joint_max = text_struct.get('joint_max', {'val_text': [], 'val_bbox': []})
    joint_min = text_struct.get('joint_min', {'val_text': [], 'val_bbox': []})
    joint_avg = text_struct.get('joint_avg', {'val_text': [], 'val_bbox': []})
    weathered = text_struct.get('weathered', {'val_text': [], 'val_bbox': []})

    # tcr_rqd
    if tcr_rqd['val_bbox']:
        # 1. 층후
        tcr_rqd, tcr_rqd_depth = __match_line(text_struct, hlines_mask, tcr_rqd, scaling_deltaY)

        text_struct['TCR_RQD'] = tcr_rqd
        text_struct['TCR_RQD_depth'] = tcr_rqd_depth


    if tcr['val_bbox']:
        tcr, tcr_depth = __match_line(text_struct, hlines_mask, tcr, scaling_deltaY)

        text_struct['TCR'] = tcr
        text_struct['TCR_depth'] = tcr_depth

    
    if rqd['val_bbox']:
        rqd, rqd_depth = __match_line(text_struct, hlines_mask, rqd, scaling_deltaY)
        
        text_struct['RQD'] = rqd
        text_struct['RQD_depth'] = rqd_depth


    if joint_max['val_bbox']:
        joint_max, joint_max_depth = __match_line(text_struct, hlines_mask, joint_max, scaling_deltaY)
        
        text_struct['joint_max'] = joint_max
        text_struct['joint_max_depth'] = joint_max_depth


    if joint_min['val_bbox']:
        joint_min, joint_min_depth = __match_line(text_struct, hlines_mask, joint_min, scaling_deltaY)
        
        text_struct['joint_min'] = joint_min
        text_struct['joint_min_depth'] = joint_min_depth


    if joint_avg['val_bbox']:
        joint_avg, joint_avg_depth = __match_line(text_struct, hlines_mask, joint_avg, scaling_deltaY)
        
        text_struct['joint_avg'] = joint_avg
        text_struct['joint_avg_depth'] = joint_avg_depth


    if weathered['val_bbox']:
        weathered, weathered_depth = __match_line(text_struct, hlines_mask, weathered, scaling_deltaY)
        
        text_struct['weathered'] = weathered
        text_struct['weathered_depth'] = weathered_depth

    return text_struct



def data_postprocessing(pagesize, img, text_struct, hlines):
    '''
    raw_extracted = {'scalebar':, {'val_text':[[x1, y1, x2, y2, text], ], 'val_bbox':[column bbox]}, ...}'''

    # 위치 재조정 ratio
    pdf_width = pagesize[0]
    pdf_height = pagesize[1]

    img_height, img_width = img.shape
    x_ratio = pdf_width / img_width
    y_ratio = pdf_height / img_height

    # pdf 사이즈에 맞춤
    converted_hlines = [(line[0] * x_ratio, line[1] * y_ratio, line[2] * x_ratio, line[3] * y_ratio) for line in hlines]
    hlines_mask = np.zeros((int(pdf_height), int(pdf_width)), dtype=np.uint8)
    for l in converted_hlines:
        hlines_mask[int(l[1]):int(l[3])+1, int(l[0]):int(l[2])+1] = 255

    scaling_deltaY = _get_scaling_deltaY(text_struct, hlines_mask)
    last_line_thickness = round((converted_hlines[-1][3] - converted_hlines[0][3]) * scaling_deltaY, ndigits=0)

    text_struct['last_line_thickness'] = last_line_thickness


    # thickness -> depth로 바꾸기
    _layer_thickness = text_struct.get('layer_thickness', {})
    _layer_thickness_text = _layer_thickness.get('val_text', [])
    _layer_thickness_line = _lines_of_interest(hlines_mask, text_struct['layer_thickness']['val_bbox'])
    layer_dict = dict(zip([i for i in range(len(_layer_thickness_line)-1)], [{} for i in range(len(_layer_thickness_line)-1)]))
    _start = 0
    _layer_depth = []
    for i in range(len(_layer_thickness_line)-1):

        if len(_layer_thickness_line) == len(_layer_thickness_text):
            _th = _layer_thickness_text[i][4]
            _layer_depth = str(round(_start+float(_th), 1))
            text_struct['layer_thickness']['val_text'][i+1][4] = _layer_depth
            _start = round(_start+float(_th), 1)

            layer_dict[i]['thickness'] = _layer_depth

        else: # 일반적으로 line이 하나 더 많음
            if i < len(_layer_thickness_text):
                _th = _layer_thickness_text[i][4]
                _layer_depth = str(round(_start+float(_th), 1))
                text_struct['layer_thickness']['val_text'][i][4] = _layer_depth
                _start = round(_start+float(_th), 1)

                layer_dict[i]['thickness'] = _layer_depth

            else:
                _layer_depth = ''
                layer_dict[i]['thickness'] = _layer_depth
        layer_dict[i]['coord'] = _layer_thickness_line[i+1][3]

    text_struct['layer_dict'] = layer_dict
    
    # layer_dict 전처리
    while len(text_struct['layer_dict']) > 1:
        _last_layer = len(text_struct['layer_dict'])-1
        if (not text_struct['layer_dict'][_last_layer]['thickness']) and (not text_struct['layer_dict'][_last_layer-1]['thickness']):
            text_struct['layer_dict'].pop(_last_layer)
        else:
            break

    


    ######## 1. tcr-rqd depth
    # TCR, RQD, weathered, joint 높이 맞추기
    text_struct = _mapping_rockprop_depth(text_struct, hlines_mask, scaling_deltaY)


    _del = 0
    for text_id, text in enumerate(text_struct['N']['val_text'][:]):
        if '/' not in text[4]:
            text_struct['N']['val_text'].pop(text_id-_del) # pop: (6.4)
            _del += 1
    ######## 2. N_depth - N
    # N치 - 채취심도 맞추기
    text_struct = _mapping_N_depth(text_struct, hlines_mask, converted_hlines, scaling_deltaY)


    ######## 3. layer description
    # layer description 묶기
    lines_in_descriptionCol = _lines_of_interest(hlines_mask, text_struct['layer_description']['val_bbox'])
    text_struct = _bind_layer(text_struct, lines_in_descriptionCol)

    # 지층 특수문자 찾기
    layer_description = text_struct['layer_description'][:]
    _signs = []
    layer_description = [l for l in layer_description if l]
    for t in layer_description:
        block_text = ''.join(t).replace(' ', '')
        _sign_list = re.findall(section_regex, block_text)
        _s = _sign_list[0] if _sign_list else ''
        _signs += [_s]
    _signs = [s for s in _signs if s]

    if len(_signs) == 0:
        layer_character = ''
    elif len(_signs) == 1:
        layer_character = _signs[0]
    else:
        layer_character = _signs[1]


    text_struct['layer_char'] = layer_character

    # print(text_struct['layer_dict'])
    # print(text_struct['layer_description'])


    # if len(text_struct['layer_dict']) == len(text_struct['layer_description']):
    #     for i, (layer_id, layer_dict) in enumerate(text_struct['layer_dict'].items()):
    #         layer_dict['description_id'] = i
    #         text_struct['layer_dict'][layer_id] = layer_dict


    # # layer dict에
    # # 층후도 없고 지층기술도 없으면 맨 끝임: 삭제
    # last_layer_id = max(text_struct['layer_dict'].keys())
    # if not text_struct['layer_dict'][last_layer_id].get('thickness') and not str(text_struct['layer_dict'][last_layer_id].get('description_id')):
    #     text_struct['layer_dict'].pop(last_layer_id)

    # layer_name
    if text_struct.get('layer_name', {}): # layer_name 항목이 있을 때
        if text_struct['layer_name'].get('val_text'): # 실제 텍스트가 있을 때
            lines_in_targetCol = _lines_of_interest(hlines_mask, text_struct['layer_name']['val_bbox'])
            _layer_name = _bind_layername(text_struct, lines_in_targetCol, text_struct['layer_name'])
            text_struct['layer_name'] = _layer_name

            for layer_id, layer_dict in text_struct['layer_dict'].items():
                layer_dict['layer_name'] = _layer_name[layer_id]
                text_struct['layer_dict'][layer_id] = layer_dict
        else:
            for layer_id, layer_dict in text_struct['layer_dict'].items():
                layer_dict['layer_name'] = ''
                text_struct['layer_dict'][layer_id] = layer_dict
    else:
        for layer_id, layer_dict in text_struct['layer_dict'].items():
            layer_dict['layer_name'] = ''
            text_struct['layer_dict'][layer_id] = layer_dict

    # layer_USCS
    if text_struct.get('layer_USCS', {}):
        if text_struct['layer_USCS'].get('val_text'):
            lines_in_targetCol = _lines_of_interest(hlines_mask, text_struct['layer_USCS']['val_bbox'])
            _layer_USCS = _bind_layername(text_struct, lines_in_targetCol, text_struct['layer_USCS'])
            text_struct['layer_USCS'] = _layer_USCS

            for layer_id, layer_dict in text_struct['layer_dict'].items():
                layer_dict['layer_USCS'] = _layer_USCS[layer_id]
                text_struct['layer_dict'][layer_id] = layer_dict
        else:
            for layer_id, layer_dict in text_struct['layer_dict'].items():
                layer_dict['layer_USCS'] = ''
                text_struct['layer_dict'][layer_id] = layer_dict
    else:
        for layer_id, layer_dict in text_struct['layer_dict'].items():
            layer_dict['layer_USCS'] = ''
            text_struct['layer_dict'][layer_id] = layer_dict


    # print(text_struct['layer_dict'])
    # print(text_struct['layer_description'])
                
    # 지층명, uscs, description 엮기
    while len(text_struct['layer_dict']) > 1:
        _last_layer = len(text_struct['layer_dict'])-1
        if (not text_struct['layer_dict'][_last_layer]['thickness']) and (not text_struct['layer_dict'][_last_layer]['layer_name']) \
                and (not text_struct['layer_dict'][_last_layer]['layer_USCS']) and (not text_struct['layer_description'][-1]):
            text_struct['layer_description'] = text_struct['layer_description'][:-1]
            text_struct['layer_dict'].pop(_last_layer)
        else:
            break
            
    
    
    ###### 나머지 key value 정리   
    # print() 
    data_struct = text_struct.copy()
    for key, value in data_struct.items():
        try:
            value.get('val_text', [])
        
            data_struct[key] = [v[4].strip() for v in value['val_text']]

        except:
            continue


    return data_struct
    
