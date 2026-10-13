

import os

import cv2
import numpy as np
import fitz

import PIL as plt
from PIL import Image

import time
import random
from pprint import pprint


def pdf2img(pdf_path):
    doc = fitz.open(pdf_path)
    for i in range(len(doc)):
        page = doc.load_page(i)
        pix = page.get_pixmap()
        mode = "RGBA" if pix.alpha else "RGB"
        img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
        yield img



# opencv error: 경로에 한글이 포함될 때
# custom funtion 사용
def imwrite(file_path, img, params=None):
    try: 
        ext = os.path.splitext(file_path)[1]
        result, n = cv2.imencode(ext, img, params)
        if result: 
            with open(file_path, mode='w+b') as f:
                n.tofile(f)
                return True
        else: 
            return False 
    except Exception as e: 
        print(e)
        return False


def imread( file_path ) :
    stream = open( file_path.encode("utf-8") , "rb")
    bytes = bytearray(stream.read())
    np_array = np.asarray(bytes, dtype=np.uint8)
    return cv2.imdecode(np_array , cv2.IMREAD_UNCHANGED)



def img_frombytes(data):
    size = data.shape[::-1]
    print(size)
    databytes = np.packbits(data, axis=1)
    return Image.frombytes(mode='1', size=size, data=databytes)





vkernel = np.ones((50, 1), np.uint8)
hkernel = np.ones((1, 50), np.uint8)
def vhLines(gray_img, thres=250):
    '''
    흑백 이미지에서 전체 모든 수직, 수평선 도출
    후처리를 거치지 않은 선들로 불필요한 선들이 포함

    input: gray scale image <np.array>
    output: 입력 이미지와 같은 크기의 binary images로 구성된 <tuple>, 
            수직선 mask, 수평선 mask
    '''
    _, img_binary = cv2.threshold(gray_img, thres, 255, cv2.THRESH_BINARY_INV)

    vlines_mask = cv2.erode(img_binary, vkernel)
    vlines_mask = cv2.dilate(vlines_mask, vkernel) # 이미지 크기 array (0,1)
    hlines_mask = cv2.erode(img_binary, hkernel)
    hlines_mask = cv2.dilate(hlines_mask, hkernel) # 이미지 크기 array (0,1)

    return vlines_mask, hlines_mask


def mask2lines(line_mask, line_type):
    '''
    binary image 형태의 선 구조 마스크를 
    [[x1, y1, x2, y2], [...],...] 형태의 점들 리스트 형태로 변환

    input: line_mask <선 구조 binary mask>, line_type='v' or 'h': 수직 or 수평
    output: [[x1, y1, x2, y2], [...],...] 형태의 점들 리스트 <list>
    '''
    _, _, stats, _ = cv2.connectedComponentsWithStats(line_mask)

    if line_type == 'v':
        lines = [] # [x1 y1 x2 y2]
        for x, y, w, h, cnt in stats:
            if w >= 15: 
                continue
            lines += [[int(x+w/2), int(y), int(x+w/2), int(y+h)]]


        lines = sorted(lines, key=lambda x: x[0])

    if line_type == 'h':
        lines = [] # [x1 y1 x2 y2]
        for x, y, w, h, cnt in stats:
            if h >= 15: continue
            lines += [[int(x), int(y+h/2), int(x+w), int(y+h/2)]]
        lines = sorted(lines, key=lambda x: x[1])

    return lines



def rois(vlines_mask, hlines_mask):
    '''
    한 이미지에 대해 수직선 마스크, 수평선 마스크를 통해
    레이아웃의 변화를 감지하여 
    일반사항 섹션 roi, 데이터 섹션 roi를 반환 

    input: 수직, 수평 line_mask <선 구조 binary mask>
    output: info_roi, data_roi: [x, y, w, h], [x, y, w, h] 형태 roi 정보 <tuple>
    '''


    mask = vlines_mask + hlines_mask

    _, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)
    stats = sorted(stats, key=lambda x: x[0])

    img_w = max([x[2] for x in stats])

    roi_boxes = [] # x y w h 
    for i, (x, y, w, h, cnt) in enumerate(stats):
        if (h<60) or (w == img_w) or (w < img_w*0.6): continue #   (cnt<5000)
        roi_boxes += [[x,y,w,h]]

    # 테두리가 잡혀있을 경우: 테두리를 제외
    while len(roi_boxes) > 1:
        
        x1, y1, w1, h1 = roi_boxes[0] # 테두리가 존재한다면 얘가 테두리일 것
        x2, y2, w2, h2 = roi_boxes[1]

        # box1이 box2를 완전히 포함하고 있으면
        if (x1 < x2) and (x1+w1 > x2+w2) and (y1 < y2) and (y1+h1 > y2+h2):
            roi_boxes = roi_boxes[1:]

        else:
            break

    # y에 따라 정렬, 위에서부터 정렬
    roi_boxes = sorted(roi_boxes, key=lambda x: x[1])

    ## info section과 data section 나누기
    ## roi가 여러 개일 경우, 마지막 box가 무조건 data section으로.
    if len(roi_boxes) > 1:
        data_roi = roi_boxes[-1]
        info_roi = roi_boxes[:-1]

        # info
        info_x = min([x[0] for x in info_roi])
        info_y = min([x[1] for x in info_roi])
        info_w = max([x[2] for x in info_roi])
        info_y2 = max([x[1]+x[3] for x in info_roi])
        info_roi = [info_x, info_y, info_w, info_y2-info_y]

    ## roi box가 하나일 경우, info와 data section 나눠야함
    # 기준은, roi 내 가장 긴 세로선이 존재 위치
    elif len(roi_boxes) == 1:
        x_roi = roi_boxes[0][0]
        y_roi = roi_boxes[0][1]
        w_roi = roi_boxes[0][2]
        h_roi = roi_boxes[0][3]
        vlines = mask2lines(vlines_mask, 'v') # order: x좌표 # x1 y1 x2 y2

        # print(vlines)

        vline_in_roi = [x for x in vlines if x_roi< x[0]< x_roi+w_roi]
        lengths = [x[3]-x[1] for x in vline_in_roi]
        len_thres = h_roi * 0.6
        vline_in_data = [x for x in vline_in_roi if x[3]-x[1] > len_thres]
        vlinestart_in_data = [x[1] for x in vline_in_data]

        ## 수정필요
        y_data = vlinestart_in_data[1]

        info_roi = [x_roi, y_roi, w_roi, y_data-y_roi]
        data_roi = [x_roi, y_data, w_roi, h_roi-(y_data-y_roi)]

    return info_roi, data_roi



def ycompsDataDrilled(data_roi, vlines_mask, hlines_mask):
    '''
    한 이미지에 대해 수직선 마스크, 수평선 마스크 및 데이터 섹션 정보를 통해
    항목 부분을 제외한 '시추 데이터' 부분의 y 좌표를 변환

    input: data_roi, 수직, 수평 line_mask
    output: 시추 데이터 value 시작 y, 끝 y <tuple>
    '''

    data_mask = np.zeros(hlines_mask.shape, np.uint8)
    data_mask[data_roi[1]:data_roi[1]+data_roi[3], data_roi[0]:data_roi[0]+data_roi[2]] =255

    vlines_mask = cv2.bitwise_and(data_mask, vlines_mask)
    vlines = mask2lines(vlines_mask, 'v')
    # 수정필요
    vlineend_in_data = [x[3] for x in vlines]
    y3 = vlineend_in_data[1]


    hlines_mask = cv2.bitwise_and(data_mask, hlines_mask)
    hlines = mask2lines(hlines_mask, 'h')

    for l in hlines[1:]:
        if (l[0] < vlines[1][0]) and (l[2]-l[0])>0.8*data_roi[2]: # 
            y2 = l[1]
            break
        else:
            y2 = hlines[2][1]
        


    return y2, y3
    

def vhcompsDataDrilled(data_roi, vlines_mask, hlines_mask):
    '''
    한 이미지에 대해 수직선 마스크, 수평선 마스크 및 데이터 섹션 정보를 통해
    데이터 섹션을 구성하는 수직선 점 리스트, 수평선 점 리스트 반환

    input: data_roi, 수직, 수평 line_mask
    output: vlines, hlines: 각각 [[x1, y1, x2, y2], [...],...] 형태의 점들 리스트 <tuple>
    '''
    
    data_mask = np.zeros(hlines_mask.shape, np.uint8)
    data_mask[data_roi[1]:data_roi[1]+data_roi[3], data_roi[0]:data_roi[0]+data_roi[2]] =255

    hlines_mask = cv2.bitwise_and(data_mask, hlines_mask)
    hlines = mask2lines(hlines_mask, 'h')

    y2, y3 = ycompsDataDrilled(data_roi, vlines_mask, hlines_mask)
    key_mask = np.zeros(vlines_mask.shape, np.uint8)
    key_mask[data_roi[1]:y2, data_roi[0]:data_roi[0]+data_roi[2]] =255
    vlines_mask = cv2.bitwise_and(key_mask, vlines_mask)
    vlines_tmp = mask2lines(vlines_mask, 'v')
    vlines = []
    for i, l in enumerate(vlines_tmp):
        if l[3]-l[1] <20:
            continue
        if l[3] == y2:
            vlines += [[l[0], l[1] ,l[2], y3]]
        else:
            vlines += [l]

    return vlines, hlines

        
def vhcompInfo(info_roi, vlines_mask, hlines_mask):
    '''
    한 이미지에 대해 수직선 마스크, 수평선 마스크 및 일반사항 섹션 정보를 통해
    일반사항 섹션을 구성하는 수직선 점 리스트, 수평선 점 리스트 반환

    input: data_roi, 수직, 수평 line_mask
    output: vlines, hlines: 각각 [[x1, y1, x2, y2], [...],...] 형태의 점들 리스트 <tuple>
    '''

    info_mask = np.zeros(hlines_mask.shape, np.uint8)
    info_mask[info_roi[1]:info_roi[1]+info_roi[3], info_roi[0]:info_roi[0]+info_roi[2]] =255

    vlines_mask = cv2.bitwise_and(info_mask, vlines_mask)
    vlines = mask2lines(vlines_mask, 'v')

    hlines_mask = cv2.bitwise_and(info_mask, hlines_mask)
    hlines = mask2lines(hlines_mask, 'h')

    return vlines, hlines


def _sorted_by_line(pts_list, thres=20):
    '''
    위 -> 아래, 왼쪽-> 오른쪽 정렬
    
    input: [[x,y], [x,y], ...] <np.array>
    ourput: 정렬된 어레이, 정렬된 어레이의 row 리스트, 정렬된 어레이의 row 내 순서 (col과 비슷한 개념), 정렬 인덱스 어레이
    '''

    # 높이 오름차순 정렬
    sorted_index = np.array(sorted(range(len(pts_list)), key=lambda k: (pts_list[k][1], pts_list[k][0])))
    pts_list = np.array(sorted(pts_list, key=lambda x:(x[1], x[0])))
    pts_list_rowsorted = []
    row = -1
    before_y = 0
    for i, pt in enumerate(pts_list):
        y = pt[1]
        if abs(y - before_y) > thres:
            # 다른 라인
            row += 1
        pts_list_rowsorted += [[row, pt[0], pt[1]]]
        before_y = y

    # row 별 x 정렬
    nested_sorted_index = np.array(sorted(range(len(pts_list_rowsorted)), key=lambda k: (pts_list_rowsorted[k][0], pts_list_rowsorted[k][1])))
    pts_list_sorted = pts_list[nested_sorted_index]
    
    sorted_index = sorted_index[nested_sorted_index]

    # row 내 order: col_order
    row_before = -1
    seq_within_row = []
    seq_tmp = 0
    for row in [x[0] for x in pts_list_rowsorted]:
        if row_before == row:
            seq_tmp += 1
        else:
            seq_tmp = 0
        seq_within_row += [seq_tmp]
        row_before = row


    return pts_list_sorted, [x[0] for x in pts_list_rowsorted], seq_within_row, np.array(sorted_index)
    


## example: general infomation section
def keyvalSecInfo(img, info_vlines, info_hlines, thres=10):
    cv_key = None
    keyval_dict = {}
    if not info_vlines[1:-1]:

        # 외곽 껍데기를 제외했을 때 수직선이 존재하지 않으면,
        # 표 형태가 아님

        if not info_hlines[1:-1]:
            # 일반사항 부분이 아예 존재하지 않을 때
            return {}
        

        # 껍데기 제외
        outer_top, outer_bottom = info_hlines[0][1], info_hlines[-1][1]
        info_hlines = info_hlines[1:-1]

        # x 좌표 
        info_hlines = sorted(info_hlines, key=lambda x:(x[0], x[1]))
        # info_hlines = sorted(info_hlines, key=lambda x:x[0])

        # 세로 분단 구분선 x좌표
        x_start = [x[0] for x in info_hlines]
        id_left = list(((np.array(x_start[1:]) - np.array(x_start[:-1])) > 50)).index(True)

        # 세로 분단 구분선을 통해 선분 구분
        info_hlines_1 = np.array(info_hlines[:id_left+1])
        info_hlines_2 = np.array(info_hlines[id_left+1:])

        # 각 분단별 sorted by line
        _, rows_1, seq_within_row_1, sorted_index_1 = _sorted_by_line([x[:2] for x in info_hlines_1])
        _, rows_2, seq_within_row_2, sorted_index_2 = _sorted_by_line([x[:2] for x in info_hlines_2])

        info_hlines_1 = info_hlines_1[sorted_index_1]
        info_hlines_2 = info_hlines_2[sorted_index_2]
        # print(info_hlines_1)
        # print(info_hlines_2)


        # 분단별로 for문
        # 1분단: x끝은 outer left, y끝은 위 box 혹은 outer top
        # 2분단: x끝은 1분단 끝 혹은 앞 box, y 끝은 위 box 혹은 outer top
        for i, l in enumerate(info_hlines_1):

            x1 = l[0]
            y1 = l[1]
            x2 = l[2]

            row = rows_1[i]
            col_seq = seq_within_row_1[i]

            
            # value
            val_x = x1
            val_y_btm = y1
            val_w = x2 - x1 + thres*1.5
            if row == 0:
                # 맨 위
                val_y = outer_top + thres
                val_h = val_y_btm - val_y
            else:
                val_y = info_hlines_1[i-col_seq-1][1] + thres
                val_h = val_y_btm - val_y


            # key
            key_y = val_y
            key_h = val_h
            if col_seq == 0:
                key_x = info_vlines[0][0]
                key_w = val_x - key_x - thres
            else:
                key_x = info_hlines_1[i-1][0]
                key_w = val_x - key_x - thres

            key = (key_x, key_y, key_w, key_h)
            val = [val_x, val_y, val_w, val_h]
            keyval_dict[key] = val


        left_x = max([x[2] for x in info_hlines_1])
        for i, l in enumerate(info_hlines_2):

            x1 = l[0]
            y1 = l[1]
            x2 = l[2]

            row = rows_2[i]
            col_seq = seq_within_row_2[i]

            # value
            val_x = x1
            val_y_btm = y1
            val_w = x2 - x1 + thres
            if row == 0:
                # 맨 위
                val_y = outer_top + thres
                val_h = val_y_btm - val_y
            else:
                val_y = info_hlines_2[i-col_seq-1][1] + thres
                val_h = val_y_btm - val_y


            # key
            key_y = val_y
            key_h = val_h
            if col_seq == 0:
                key_x = left_x + thres*1.5
                key_w = val_x - key_x - thres
            else:
                key_x = info_hlines_2[i-1][2]
                key_w = val_x - key_x - thres

            key = (key_x, key_y, key_w, key_h)
            val = [val_x, val_y, val_w, val_h]
            keyval_dict[key] = val


        info_hlines = list(info_hlines_1) + list(info_hlines_2)


    else:
        # 표 형태일 때
        # section

        section_mask = np.ones(img.shape, dtype=np.uint8)*255
        for l in info_vlines:
            # x1 y1 x2 y2
            section_mask[l[1]:l[3]+1, l[0]:l[2]+1] = 0
        for l in info_hlines:
            section_mask[l[1]:l[3]+1, l[0]:l[2]+1] = 0
        # imwrite(save_path, section_mask)

        
        _, _, stats, _ = cv2.connectedComponentsWithStats(section_mask, connectivity=4) # _, _, stats, area
        # stats = sorted(stats, key=lambda x: x[4], reverse=True)
        # stats: x,y 오름차순으로 정렬
        rects = []
        for i, (x, y, w, h, cnt) in enumerate(stats):

            if (w >= (info_hlines[0][2] - info_hlines[0][0])*0.9) and (h >= (info_hlines[0][3] - info_hlines[0][1])*0.9) \
                or (h<15): continue #  
            # if cnt > 10000: continue

            rects += [[x,y,w,h]]


        keyList = []
        valueList = []
        before_key = 0
        is_key = 1 # key: 1, val: 0
        before_box_end = 2000 # 같은 라인인지 확인하기 위함
        for bbox in rects:

            box_start = bbox[0] # 시작 x 점
            if abs(box_start - before_box_end) > 10:
                # 현재 박스 시작점과 이전 박스 끝점의 x좌표 차이가 많이 나면, 다른 라인
                # 다른 라인 시작이므로, 현재 bbox는 무조건 key가 될 것.
                is_key = 1


            if is_key == before_key:
                # 1
                # key와 value가 번갈아 나타나야 하나, key가 연속적으로 나타날 때
                # 앞선 bbox가 쓸데없는 애임 (ex. 시료채취방법) -> 삭제
                keyList = keyList[:-1]
                
            
            before_box_end = bbox[0]+bbox[2]
            before_key = is_key
            if is_key:
                keyList += [tuple(bbox)]
                is_key = 0
            else: # value bbox
                valueList += [bbox]
                is_key = 1
            

        keyval_dict = dict(zip(keyList, valueList))


    return keyval_dict




def keyvalSecData(img, vlines_data, hlines_data, rowlines_data):
    ### vlines_data: (x1, y1, x2, y2)

    section_mask = np.ones(img.shape, dtype=np.uint8)*255

    for l in vlines_data:
            # x1 y1 x2 y2
        section_mask[l[1]:l[3]+1, l[0]:l[2]+1] = 0
    for l in hlines_data:
        section_mask[l[1]:l[3]+1, l[0]:l[2]+1] = 0

    header_mask = np.zeros(img.shape, dtype=np.uint8)
    header_mask[rowlines_data[0]:rowlines_data[1], :] = 255
    section_mask = cv2.bitwise_and(section_mask, header_mask)


    _, _, stats, _ = cv2.connectedComponentsWithStats(section_mask, connectivity=4)

    rects = []
    for i, (x, y, w, h, cnt) in enumerate(stats):

        if (w >= (vlines_data[-1][0] - vlines_data[0][0])*0.9) or x == 0 or x+w==img.shape[1]: 
            continue #   (h >= (rowlines_data[0][3] - rowlines_data[0][1])*0.9) 
        # if cnt > 10000: continue

        rects += [[x,y,w,h]]


    keyList = []
    valueList = []
    for keySec in rects:

        if keySec[1]+keySec[3] == rowlines_data[1]:

            # 좌표를 비율에 맞게 조정
            # x1, x2 = keySec[0], keySec[0]+keySec[2]
            # y1, y2 = keySec[1], keySec[1]+keySec[3] 
            # y_end = rowlines_data[-1]

            x1, x2 = keySec[0], keySec[0]+keySec[2]
            y1, y2 = keySec[1], keySec[1]+keySec[3] 
            y_end = rowlines_data[-1]

            keyList += [(x1, y1, x2, y2)]
            valueList += [(x1, y2, x2, y_end)]

    return dict(zip(tuple(keyList), tuple(valueList)))




## example
def get_col_row_DataDrilled(gray_img):
    '''
    흑백 이미지에서 데이터 섹션 추출에 필요한 x 리스트, y 리스트 반환
    

    input: gray scale image <np.array>
    output: colList: 데이터 섹션 템플릿 수직선들의 x 좌표
            rowList: 데이터 섹션 템플릿 내 1. 데이터 섹션 시작 y 좌표, 2. 항목 부분 끝 y 좌표, 3. 시추 데이터 끝 y 좌표
                     항목: y1~y2, value: y2~y3
    '''

    vlines_mask, hlines_mask = vhLines(gray_img)
    info_roi, data_roi = rois(vlines_mask, hlines_mask)
    y1 = data_roi[1]
    y2, y3 = ycompsDataDrilled(data_roi, vlines_mask, hlines_mask)
    # key: y1~y2, value: y2~y3
    rowList = [y1, y2, y3]

    vlines, hlines = vhcompsDataDrilled(data_roi, vlines_mask, hlines_mask)
    colList = [vline[0] for vline in vlines]

    return colList, rowList


def get_lines_DataDrilled(gray_img):
    '''
    흑백 이미지에서 데이터 섹션을 구성하는 수직선, 수평선 점들 리스트 반환
    

    input: gray scale image <np.array>
    output: vlines, hlines
    '''

    vlines_mask, hlines_mask = vhLines(gray_img)
    info_roi, data_roi = rois(vlines_mask, hlines_mask)

    vlines, hlines = vhcompsDataDrilled(data_roi, vlines_mask, hlines_mask)

    return vlines, hlines




def main_segmentation(gray_img):
    vlines_mask, hlines_mask = vhLines(gray_img)
    info_roi, data_roi = rois(vlines_mask, hlines_mask)


    vlines_info, hlines_info = vhcompInfo(info_roi, vlines_mask, hlines_mask)
    vlines_data, hlines_data = vhcompsDataDrilled(data_roi, vlines_mask, hlines_mask)
    
    rowlines_data = [data_roi[1], *ycompsDataDrilled(data_roi, vlines_mask, hlines_mask)] # y1 y2 y3

    secDictInfo = keyvalSecInfo(gray_img, vlines_info, hlines_info)
    secDictData = keyvalSecData(gray_img, vlines_data, hlines_data, rowlines_data)


    # hlines_data에서 실제 데이터가 존재하는 부분만 추리기 (hlines_data)
    for l in hlines_data[:]:
        if (l[1] < rowlines_data[1]) or (l[1] > rowlines_data[2]):
            hlines_data.remove(l)

    
    return secDictInfo, secDictData, hlines_data


