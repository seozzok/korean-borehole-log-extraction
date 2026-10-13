
import re

import os
import cv2
from pprint import pprint



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




##################
def ui_formatting(data_dict):
    for key, value in data_dict.items():

        if key == 'layer_name':
            new_list = []
            for i, v in enumerate(value[:]):
                if i % 2 != 0:
                    continue
                
                else:
                    v = v.replace(' ', '') + '층'
                    new_list += [v]
                
            data_dict[key] = new_list

        
        elif key == 'layer_description':

            for i, block in enumerate(value):

                for j, text in enumerate(block):

                    tList = text.split(' ')
                    for start, t in enumerate(tList):
                        if not t:
                            continue
                        else: break
                    nText = ' '.join(tList[start:])

                    block[j] = nText
                
                value[i] = block
                    


        else:
            new_list = []
            for i, v in enumerate(value[:]):

                nText = v.replace(' ', '')

                value[i] = nText

            data_dict[key] = value


    return data_dict


def _int2float(num_list):
    if len(num_list) == 1:
        return num_list[0]
    elif len(num_list) == 0:
        # 숫자가 없는 경우
        return ''
    else:
        return num_list[0]+'.'+num_list[1]
    

def only_nums(text):
    # re 를 통해 찾은 숫자는 [int] 아니면 [int, int] (. 으로 연결된 float) 일 것
    return _int2float(re.findall('\d+', text.replace(' ', '').replace(',', '')))


def valid_date(date):
    ymd_all = re.findall('\d+', date.replace(' ', ''))
    if len(ymd_all) == 1:
        ymd_all = [only_nums(d) for d in date.split(' ')]
        ymd_all = [d for d in ymd_all if d]

    if len(ymd_all) >= 3:
        ymd = ymd_all[:3]
        y,m,d = ymd[0], ymd[1], ymd[2]
        m = '{:02d}'.format(int(m))
        d = '{:02d}'.format(int(d))
        return '{y}-{m}-{d}'.format(y=y,m=m,d=d)
    elif len(ymd_all) == 2:
        y, m = ymd_all[0], ymd_all[1]
        m = '{:02d}'.format(int(m))
        return '{y}-{m}'.format(y=y,m=m)



def get_textchunk(chars):
    # chars: [(140.9999237060547, 328.7957458496094, 144.91587829589844, 336.62945556640625, 'o'), ]
    # 가로로 읽는 기준

    chars = sorted(chars, key=lambda x: x[1])



    lines = []
    tmp_line = []
    for i, c in enumerate(chars):
        if (i == 0) or (upper_y1 <= (c[1]+c[3])/2 <= lower_y1):
        # if (i == 0) or (upper_y1 <= c_y <= lower_y1):
            # 같은 라인
            tmp_line += [c]
            upper_y1 = c[1]
            lower_y1 = c[3]


        else:
            # 다른 라인
            # 이 때까지 저장된 tmp_line 저장
            tmp_line.sort(key=lambda x: x[0])
            line_t = ''.join([c[4] for c in tmp_line]) #.replace(' ', '')

            if line_t:
                # 저장된 tmp_line이 공백이 아닐 경우만 저장
                line_x1 = min([c[0] for c in tmp_line])
                line_y1 = min([c[1] for c in tmp_line])
                line_x2 = max([c[2] for c in tmp_line])
                line_y2 = max([c[3] for c in tmp_line])

                lines += [[line_x1, line_y1, line_x2, line_y2, line_t]]

            tmp_line = []
            tmp_line += [chars[i]]
            upper_y1 = chars[i][1]
            lower_y1 = chars[i][3]
            

    if tmp_line:
        tmp_line.sort(key=lambda x: x[0])
        line_x1 = min([c[0] for c in tmp_line])
        line_y1 = min([c[1] for c in tmp_line])
        line_x2 = max([c[2] for c in tmp_line])
        line_y2 = max([c[3] for c in tmp_line])
        line_t = ''.join([c[4] for c in tmp_line]) #.replace(' ', '')


        if line_t:
            lines += [[line_x1, line_y1, line_x2, line_y2, line_t]]

            
    return lines
   


def _get_str_similarity(answer_string, input_string):
    intersection_cardinality = len(set.intersection(*[set(answer_string), set(input_string)]))
    union_cardinality = len(set.union(*[set(answer_string), set(input_string)]))
    similar = intersection_cardinality / float(union_cardinality)
    return similar


def text_postprocessing_info(data_dict):
    '''
    입력한 data_dict의 값을
    알맞은 형식으로 후처리'''
    
    if not data_dict: # 일반사항 부분이 존재하지 않을 때
        data_dict = {'borehole': '',
                    'coordinates_x': '',
                    'coordinates_y': '',
                    'elevation': '',
                    'watertable': '',
                    'date': '',
                    'holedia': ''}
        return data_dict

    
    
    for key, value in data_dict.copy().items():

        if not value: # ''
            # 값이 없으면 그대로
            continue
        
        if key == 'borehole':
            value = value.replace(' ', '')
            if '[' in value:
                dump_index = value.find('[')
                value = value[:dump_index]
            elif '(' in value:
                dump_index = value.find('(')
                value = value[:dump_index]

            data_dict[key] = value


        elif key == 'coordinates':

            x_index = value.upper().find('X')
            y_index = value.upper().find('Y')

            # 일반적으로 x가 먼저, y가 나중에 나온다고 가정
            if (x_index == -1) and (y_index == -1):
                # x, y가 값에 없을 때
                x_value = ''
                y_value = ''

            # 하나만 있을 때
            elif (x_index == -1) and (y_index != -1):
                x_value = ''
                y_value = only_nums(value[y_index:])

            elif (x_index != -1) and (y_index == -1):
                x_value = only_nums(value[x_index:])
                y_value = ''

            else:
                x_value = only_nums(value[x_index:])
                y_value = only_nums(value[y_index:])

            data_dict['coordinates_x'] = x_value
            data_dict['coordinates_y'] = y_value

            data_dict.pop('coordinates', None)
        

        elif key == 'coordinates_x':
            x_index = value.upper().find('X')

            if (x_index == -1):
                # x가 값에 없을 때
                x_value = ''
            else:
                x_value = only_nums(value[x_index:])
            data_dict['coordinates_x'] = x_value


        elif key == 'coordinates_y':
            y_index = value.upper().find('Y')

            if (y_index == -1):
                # x가 값에 없을 때
                y_value = ''
            else:
                y_value = only_nums(value[y_index:])
            data_dict['coordinates_y'] = y_value


        elif key == 'date':
            value = valid_date(value)
            data_dict['date'] = value


        elif key == 'elevation':
            ele = only_nums(value) if value[0] != '-' else '-'+only_nums(value)
            data_dict['elevation'] = ele


        elif key == 'holedia':
            if 'NX' in value:
                value = '76.2'
            elif 'BX' in value:
                value = '63.5'
            data_dict['holedia'] = value


        elif key == 'watertable':
            value = only_nums(value)

            data_dict['watertable'] = value
    
    return data_dict




korean_regex = r"[^가-힣]"
def text_postprocessing_data(data_dict):
    '''
    입력한 data_dict의 값을
    알맞은 형식으로 replace'''

    for key, value_list in data_dict.copy().items():

        if not value_list: # ''
            # 값이 없으면 그대로
            continue

        value_text_list = value_list['val_text']
        if not value_text_list:
            continue

        if (key == 'joint_avg') or (key == 'joint_max') or (key == 'joint_min'):
            value_text_list = get_textchunk(value_text_list)
            for i, value in enumerate(value_text_list[:]):
                text = value[4]
                if (text == 'NA') or (text == 'N/A') or (text == 'N.A'):
                    continue
                else:
                    value_text_list[i][4] = only_nums(text)

            value_text_list = [v for v in value_text_list if v[4]]
            data_dict[key]['val_text'] = value_text_list


        elif key == 'layer_description':
            value_text_list = get_textchunk(value_text_list)
            if ('觀察' in value_text_list[0][4].replace(' ', '')) or ('Description' in value_text_list[0][4].replace(' ', '')) or\
                ('N' == value_text_list[0][4].replace(' ', '').upper()):
                value_text_list = value_text_list[1:]

            value_text_list = [v for v in value_text_list if v[4]]
            data_dict[key]['val_text'] = value_text_list
            


        elif key == 'layer_name':
            value_text_list = get_textchunk(value_text_list)
            if ('土質名' in value_text_list[0][4].replace(' ', '')) or ('N' == value_text_list[0][4].replace(' ', '').upper()):
                value_text_list = value_text_list[1:]

            for i, value in enumerate(value_text_list[:]):
                text = value[4]

                value_text_list[i][4] = text.replace(' ', '')

            value_text_list = [text for text in value_text_list if '색' not in text[4]]

            value_text_list = [v for v in value_text_list if v[4]]
            data_dict[key]['val_text'] = value_text_list


        elif key == 'layer_thickness':
            value_text_list = get_textchunk(value_text_list)
            for i, value in enumerate(value_text_list[:]):
                text = value[4]

                value_text_list[i][4] = only_nums(text)

            value_text_list = [value for value in value_text_list if value[4]]
            data_dict[key]['val_text'] = value_text_list


        elif key == 'layer_USCS':
            value_text_list = get_textchunk(value_text_list)
            if ('류' in value_text_list[0][4].replace(' ', '')) or ('oulde' in value_text_list[0][4].replace(' ', '')):
                value_text_list = value_text_list[1:]

            value_text_list = [v for v in value_text_list if len(v[4])>1] # 'c'

            data_dict[key]['val_text'] = value_text_list


        elif key == 'N':
            if ('CM' in value_text_list[0][4].replace(' ', '').upper()) or ('관입량' in value_text_list[0][4].replace(' ', '')):
                value_text_list = value_text_list[1:]

            # _del = 0
            # for i, v in enumerate(value_text_list[:]):
            #     text = v[4]
            #     if ('(' in text) and ('/' not in text):
            #         continue
                    # del(value_text_list[i-_del])
                    # _del += 1
                # elif ('(' in text) and ('/' in text): # (1510./03)
                #     text = ''.join([char for i, char in enumerate(text[1:]) if i%2==1])
                #     value_text_list[i-_del][4]=text

                #     text = ''.join([char for i, char in enumerate(text[1:]) if i%2==0])
                #     _tmp = value_text_list[i-_del]
                #     _tmp[4] = text
                    # value_text_list.append([_tmp])
            # print(value_text_list)
            for i, v in enumerate(value_text_list):
                text = v[4]
                
                value_text_list[i][4] = text.replace(' ', '')

            # new_values = []
            # for value in value_list[:]:
            #     nums = value[4].split('/')
            #     new_values += [*nums]
            # new_values = [v.replace(' ', '') for v in new_values if v]

            # value_list = []
            # for i in range(int(len(new_values[:])/2)): 
            #     cm = new_values[2*i]
            #     N = new_values[2*i+1]

            #     value_list += [cm + '/' + N]

            value_text_list = [v for v in value_text_list if v[4]]
            value_text_list.sort(key= lambda x: x[1])
            # print(value_text_list)


            # '/'이 쪼개져 있는 경우 정리
            text_before = []
            for i, value in enumerate(value_text_list[:]):
                if '(' in value: continue

                x1, y1, x2, y2 = value[:4]
                nums = value[4].split('/')

                # nums = [v for v in nums if v]
                if len([v for v in nums if v]) == 2: # 7/30
                    continue
                else:
                    if text_before:
                        if '/' in value[4]:
                            if '/' == value[4][-1]: # 7/
                                new_text = value[4] + text_before[4]
                                new_x1 = min(text_before[0], value[0])
                                new_y1 = min(text_before[1], value[1])
                                new_x2 = max(text_before[2], value[2])
                                new_y2 = max(text_before[3], value[3])

                                value_text_list[i-1] = [new_x1, new_y1, new_x2, new_y2, new_text]
                                value_text_list[i] = []

                                text_before = []
                            elif '/' == value[4][0]: # /30
                                new_text = text_before[4] + value[4]
                                new_x1 = min(text_before[0], value[0])
                                new_y1 = min(text_before[1], value[1])
                                new_x2 = max(text_before[2], value[2])
                                new_y2 = max(text_before[3], value[3])

                                value_text_list[i-1] = [new_x1, new_y1, new_x2, new_y2, new_text]
                                value_text_list[i] = []

                                text_before = []
                        elif '/' in text_before[4]:
                            if '/' == text_before[4][-1]: # 7/
                                new_text = text_before[4] + value[4]
                                new_x1 = min(text_before[0], value[0])
                                new_y1 = min(text_before[1], value[1])
                                new_x2 = max(text_before[2], value[2])
                                new_y2 = max(text_before[3], value[3])

                                value_text_list[i-1] = [new_x1, new_y1, new_x2, new_y2, new_text]
                                value_text_list[i] = []

                                text_before = []
                            elif '/' == value[4][0]: # /30
                                new_text = value[4] + text_before[4]
                                new_x1 = min(text_before[0], value[0])
                                new_y1 = min(text_before[1], value[1])
                                new_x2 = max(text_before[2], value[2])
                                new_y2 = max(text_before[3], value[3])

                                value_text_list[i-1] = [new_x1, new_y1, new_x2, new_y2, new_text]
                                value_text_list[i] = []

                                text_before = []
                        # else:
                            # 둘 다 '/' 없을 경우



                    else:
                        regen_nums = '/'.join(nums)
                        text_before = value
                        

                # if not '/' in value:
                #     text_before = value
                #     continue

                # if value[4] != regen_nums: # 7/
                #     text_before = value

                # else:
                #     if (text_before):
                #         new_text = text_before[4] + value[4]
                #         new_x1 = min(text_before[0], value[0])
                #         new_y1 = min(text_before[1], value[1])
                #         new_x2 = max(text_before[2], value[2])
                #         new_y2 = max(text_before[3], value[3])

                #         value_text_list[i-1] = [new_x1, new_y1, new_x2, new_y2, new_text]
                #         value_text_list[i] = []

                #         text_before = []

                    
            value_text_list = [v for v in value_text_list if v]

            data_dict[key]['val_text'] = value_text_list



        elif key == 'N_depth':
            value_text_list = get_textchunk(value_text_list)
            if ('심도' in value_text_list[0][4].replace(' ', '').upper()) \
                or ('(m)' in value_text_list[0][4].replace(' ', '').upper()):
                value_text_list = value_text_list[1:]

            for i, value in enumerate(value_text_list[:]):
                text = value[4]

                value_text_list[i][4] = only_nums(text)

            value_text_list = [text for text in value_text_list \
                          if (only_nums(text[4])) and ('S' not in text[4].upper()) and ('(' not in text[4])]
            
            value_text_list = [v for v in value_text_list if v[4]]
            data_dict[key]['val_text'] = value_text_list


        elif key == 'N_depth_samp':
            value_text_list = get_textchunk(value_text_list)
            # N-depth만 있거나
            # sample name이랑 같이 있거나
            
            n_depth = []
            samp_name = []
            for v in value_text_list:
                text = v[4]
                if ('S' in text.upper()) or ('NONE' in text.upper()):
                    # sample name
                    v[4] = text.replace(' ', '')
                    samp_name += [v]
                else:
                    v[4] = only_nums(text)
                    n_depth += [v]

            samp_name = [v for v in samp_name if v[4]]
            n_depth = [n for n in n_depth if n[4]]

            data_dict['N_depth'] = {}
            data_dict['N_depth']['val_bbox'] = value_list['val_bbox']
            data_dict['N_depth']['val_text'] = n_depth

            data_dict['sample_name'] = {}
            data_dict['sample_name']['val_bbox'] = value_list['val_bbox']
            data_dict['sample_name']['val_text'] = samp_name

            data_dict.pop('N_depth_samp')


        elif (key == 'RQD') or (key == 'TCR'):
            value_text_list = get_textchunk(value_text_list)
            if ('%' in value_text_list[0][4]):
                value_text_list = value_text_list[1:]

            for i, v in enumerate(value_text_list):
                text = v[4]
                
                value_text_list[i][4] = only_nums(text)

            value_text_list = [v for v in value_text_list if v[4]]
            data_dict[key]['val_text'] = value_text_list


        elif key == 'sample_name':
            value_text_list = get_textchunk(value_text_list)
            if ('번호' in value_text_list[0][4].replace(' ', '')) or ('番號' in value_text_list[0][4].replace(' ', ''))\
                or ('방법' in value_text_list[0][4].replace(' ', '')):
                value_text_list = value_text_list[1:]

            for i, v in enumerate(value_text_list):
                text = v[4]
                if ('WON' in text.upper()):
                    continue
                
                value_text_list[i][4] = text.replace(' ', '')

            value_text_list = [v for v in value_text_list if v[4]]
            data_dict[key]['val_text'] = value_text_list


        elif key == 'scalebar':
            if ('m' in value_text_list[0][4].replace(' ', '')):
                value_text_list = value_text_list[1:]
            # print(value_text_list)
            # value_text_list = get_textchunk(value_text_list)
            for i, v in enumerate(value_text_list):
                
                text = v[4]
                
                value_text_list[i][4] = text.replace(' ', '')

            value_text_list = [v for v in value_text_list if v[4]]
            data_dict[key]['val_text'] = value_text_list


        elif key == 'TCR_RQD':
            value_text_list = get_textchunk(value_text_list)
            if ('N' in value_text_list[0][4].replace(' ', '').upper()) or ('%' in value_text_list[0][4].replace(' ', '')):
                value_text_list = value_text_list[1:]

            value_text_list = [v for v in value_text_list if v[4]]
            data_dict[key]['val_text'] = value_text_list


        elif key == 'weathered':
            value_text_list = get_textchunk(value_text_list)
            value_text_list = [v for v in value_text_list if v[4]]
            data_dict[key]['val_text'] = value_text_list


    return data_dict




_layer_name = ['매립', '전답', '맥암', '퇴적', '붕적', '충적', '잔적', '풍화토', '풍화암', '연암', '보통암', '경암', '성토', '콘크리트', '표토', \
               '자갈모래점토', '점토자갈모래', '핵석', '잡석치환', '점토층', '실트질모래', '자갈질모래', '점토질자갈', '모래질점토', '점토질모래', '기반암층']
korean_regex = r"[가-힣]"
section_regex = r"[^\uAC00-\uD7A30-9a-zA-Z\s]"
_key_order = ['scalebar', 'sample_name', 'last_line_thickness', 'N_depth', 'N_thickness', 'N', \
              'layer_dict', 'layer_thickness', 'layer_char', 'layer_description', 'layer_name', 'layer_USCS',\
             'TCR_RQD', 'TCR_RQD_depth', 'TCR_RQD_thickness', 'TCR', 'TCR_depth', 'TCR_thickness', 'RQD', 'RQD_depth', 'RQD_thickness',\
                'joint_max', 'joint_max_depth', 'joint_max_thickness', 'joint_min', 'joint_min_depth', 'joint_min_thickenss', 'joint_avg', 'joint_avg_depth', 'joint_avg_thickness', 'weathered', 'weathered_depth', 'weathered_thickness']
def merge_page(data_dict, is_continuation=0, previous_data_dict=None):
    # sorting
    data_dict = {k: data_dict[k] for k in _key_order if k in data_dict}
    for key, value in data_dict.copy().items():
        if (not value) and (key != 'layer_thickness')and (key != 'layer_description')and (key != 'N'): # 데이터가 없으면 remove
            data_dict.pop(key)
            continue

        if key == 'scalebar':
            data_dict.pop(key)
            

        elif key == 'sample_name':
            data_dict.pop(key)


        elif key == 'last_line_thickness':
            if is_continuation:
                data_dict['last_line_thickness'] += previous_data_dict['last_line_thickness']


        elif key == 'N_depth':
            if is_continuation:
                data_dict['N_depth'] = previous_data_dict['N_depth'][:] + data_dict['N_depth']


        elif key == 'N_thickness':
            if is_continuation:
                _start_depth = previous_data_dict['last_line_thickness']
                _tmp = []
                for thickness in data_dict['N_thickness']:
                    _prev_depth = _tmp[-1] if _tmp else _start_depth

                    _tmp += [_prev_depth + float(thickness)]

                data_dict['N_depth'] = _tmp
                data_dict['N_depth'] = previous_data_dict['N_depth'][:] + data_dict['N_depth']
            else: # 첫 페이지 일 때
                _start_depth = 0
                _tmp = []
                for i, thickness in enumerate(data_dict['N_thickness']):
                    _tmp += [_start_depth+float(thickness)]
                    _start_depth = _tmp[i]
                data_dict['N_depth'] = _tmp
            data_dict.pop('N_thickness')
                    

        elif key == 'N':
            if is_continuation:
                data_dict['N'] = previous_data_dict['N'][:] + data_dict['N']


        #### 지층정보
        elif key == 'layer_dict':
            if is_continuation:
                _previous_layer_num = len(previous_data_dict['layer_dict'])
                _previous_last_layer = _previous_layer_num-1
                
                if not data_dict['layer_dict'][0]['thickness']:
                    # 현재 페이지가 뒷 페이지인데 층후가 없으면, 
                    # 더 이상 추가적인 지층이 없다는 의미
                    # layer name도, layer uscs도 없음 (라인이 없음)
                    data_dict['layer_dict'] = previous_data_dict['layer_dict']

                # 추가적인 지층 있음
                else:
                    if not (previous_data_dict['layer_dict'][_previous_last_layer]['thickness']):
                        # 앞선 지층에서 이어졌다

                        if len(previous_data_dict['layer_dict']) != 1:
                            _previous_last_layer_thickness = previous_data_dict['layer_dict'][_previous_last_layer-1].get('thickness', '')
                        else:
                            _previous_last_layer_thickness = previous_data_dict['layer_dict'][0].get('thickness', '')

                        _previous_last_layer_thickness = _previous_last_layer_thickness if _previous_last_layer_thickness else 0
                        # 앞선 지층에 이어 thickness
                        # _current_last_layer_thickness = round(float(_previous_last_layer_thickness) + float(data_dict['layer_dict'][0]['thickness']), 1)

                        _previous_last_layer_name = previous_data_dict['layer_dict'][_previous_last_layer].get('layer_name', '')
                        _previous_last_layer_uscs = previous_data_dict['layer_dict'][_previous_last_layer].get('layer_USCS', '')

                        _current_first_layer_name = data_dict['layer_dict'][0].get('layer_name', '')
                        _current_first_layer_uscs = data_dict['layer_dict'][0].get('layer_USCS', '')
                        
                        for layer_num, ld in data_dict['layer_dict'].items():

                            if layer_num == 0:
                                # 뒷 페이지 첫 번째 지층은
                                # 앞 페이지 마지막 지층과 합쳐야 함
                                previous_data_dict['layer_dict'][_previous_last_layer]['layer_name'] = _previous_last_layer_name if _previous_last_layer_name else _current_first_layer_name
                                previous_data_dict['layer_dict'][_previous_last_layer]['layer_USCS'] = _previous_last_layer_uscs if _previous_last_layer_uscs else _current_first_layer_uscs
                                previous_data_dict['layer_dict'][_previous_last_layer]['thickness'] = round(float(_previous_last_layer_thickness) + float(data_dict['layer_dict'][0]['thickness']), 1)

                                # _previous_last_layer_thickness = previous_data_dict['layer_dict'][_previous_last_layer]['thickness']
                            else:
                                previous_data_dict['layer_dict'][_previous_last_layer+layer_num] = ld
                            
                                if not ld['thickness']: continue

                                previous_data_dict['layer_dict'][_previous_last_layer+layer_num]['thickness'] = round(float(_previous_last_layer_thickness) \
                                                                                                                      + float(previous_data_dict['layer_dict'][_previous_last_layer+layer_num]['thickness']), 1)
                                
                        data_dict['layer_dict'] = previous_data_dict['layer_dict']
                    else:
                        # 앞선 지층에서 이어지지 않았다.
                        _previous_last_layer_thickness = previous_data_dict['layer_dict'][_previous_last_layer].get('thickness', '')

                        for layer_num, ld in data_dict['layer_dict'].items():
                            previous_data_dict['layer_dict'][_previous_last_layer+layer_num+1] = ld

                            if not ld['thickness']: continue
                        
                            previous_data_dict['layer_dict'][_previous_last_layer+layer_num+1]['thickness'] = round(float(_previous_last_layer_thickness) \
                                                                                                                    + float(previous_data_dict['layer_dict'][_previous_last_layer+layer_num+1]['thickness']), 1)


                        data_dict['layer_dict'] = previous_data_dict['layer_dict']




        elif key == 'layer_thickness':
            if is_continuation:
                _last_thick = previous_data_dict['layer_depth'][-1] if previous_data_dict['layer_depth'] else 0
                _depth = [round(float(_last_thick)+float(v), 1) for v in data_dict['layer_thickness']]
                # data_dict['layer_thickness'] = previous_data_dict['layer_thickness'][:] + data_dict['layer_thickness']
                data_dict['layer_depth'] = previous_data_dict['layer_depth'][:] + _depth
                
            else:
                data_dict['layer_depth'] = data_dict['layer_thickness']

            # print(data_dict['layer_depth'])

        elif key == 'layer_description':
            if is_continuation:

                if data_dict['layer_description']:
                    if not previous_data_dict.get('layer_description'):
                        # 이전 지층 기술 부분이 없을 때
                        pass

                    # elif (''.join(previous_data_dict['layer_description'][-1]) == ''.join(data_dict['layer_description'][0])) and data_dict['layer_description'][0]:
                    elif data_dict['layer_description'][0] and \
                        _get_str_similarity(''.join(previous_data_dict['layer_description'][-1]).replace(' ', ''), ''.join(data_dict['layer_description'][0]).replace(' ', '')) > 0.93:
                        # 이전 지층 기술 부분과 매우 비슷할 때
                        ########## 안됨 ---> 다른 지층인데, 기술 설명 똑같을 수 있음
                        data_dict['layer_description'] = previous_data_dict['layer_description'][:] + data_dict['layer_description'][1:]
                        
                    else:
                        # 이전 지층기술
                        if not data_dict['layer_description'][0]:
                            data_dict['layer_description'] = previous_data_dict['layer_description'][:] + data_dict['layer_description'][1:]

                        elif not previous_data_dict['layer_description'][-1]:
                            previous_data_dict['layer_description'][-1].extend(data_dict['layer_description'][0])
                            data_dict['layer_description'] = previous_data_dict['layer_description'][:] + data_dict['layer_description'][1:]
                            
                        else:
                            is_layerStart = 0
                            first_line  = data_dict['layer_description'][0][0].replace(' ', '')

                            for layer_name in _layer_name:
                                if (layer_name in first_line) and (len(''.join(re.findall(korean_regex, first_line))) <= 6) \
                                    and (previous_data_dict['layer_char'] in first_line)\
                                    and ('의' not in first_line)\
                                    and (len(previous_data_dict['layer_description'][-1]) > 1):
                                    is_layerStart = 1
                                    break

                            if is_layerStart: # 레이어 시작이 맞을 경우
                                data_dict['layer_description'] = previous_data_dict['layer_description'][:] + data_dict['layer_description']
                                
                            else: # 레이어 시작이 아닌 경우
                                # 이전 데이터셋 뒤에 현재 데이터셋 첫 번째 지층 설명 붙이기
                                previous_data_dict['layer_description'][-1].extend(data_dict['layer_description'][0])
                                data_dict['layer_description'] = previous_data_dict['layer_description'][:] + data_dict['layer_description'][1:]


        
        # elif key == 'layer_name':
        #     if is_continuation:
        #         # 중복처리
        #         # layer description을 기준으로 함
        #         if len(previous_data_dict['layer_name'][:] + data_dict['layer_name']) != len(data_dict['layer_description'])\
        #             and (previous_data_dict['layer_name'][-1] == data_dict['layer_name'][0]):
        #             data_dict['layer_name'] = previous_data_dict['layer_name'][:] + data_dict['layer_name'][1:]
        #             _layer_dup = 1
        #         else:
        #             _layer_dup = 0
        #             data_dict['layer_name'] = previous_data_dict['layer_name'][:] + data_dict['layer_name']

        
        # elif key == 'layer_USCS':
        #     if is_continuation:
        #         if (previous_data_dict['layer_USCS'][-1] == data_dict['layer_USCS'][0]) and _layer_dup:
        #             data_dict['layer_USCS'] = previous_data_dict['layer_USCS'][:] + data_dict['layer_USCS'][1:]
        #         else:
        #             data_dict['layer_USCS'] = previous_data_dict['layer_USCS'][:] + data_dict['layer_USCS']


        elif key == 'TCR_RQD':
            if not value[0]:
                data_dict['TCR_RQD'] = data_dict['TCR_RQD'][1:]

            if is_continuation:
                _tcr_rqd_addup = 0
                if '/' not in data_dict['TCR_RQD'][0].replace(' ', ''):
                    previous_data_dict['TCR_RQD'][-1] = previous_data_dict['TCR_RQD'][-1] + '/' + data_dict['TCR_RQD'][0]
                    _tcr_rqd_addup = 1

                    data_dict['TCR_RQD'] = previous_data_dict.get('TCR_RQD', [])[:] + data_dict['TCR_RQD'][1:]
                else:
                    data_dict['TCR_RQD'] = previous_data_dict.get('TCR_RQD', []) + data_dict['TCR_RQD']


        elif key == 'TCR_RQD_depth':
            if not value[0]:
                data_dict['TCR_RQD_depth'] = data_dict['TCR_RQD_depth'][1:]

            if is_continuation:
                _start_depth = previous_data_dict['TCR_RQD_depth'][-1][-1] if previous_data_dict.get('TCR_RQD_depth') \
                                else data_dict['TCR_RQD_depth'][0][0] #round(float(previous_data_dict['layer_depth'][-1]), 1)

                data_dict['TCR_RQD_depth'][0][0] = _start_depth #+ round(float(data_dict['TCR_RQD_depth'][0][0]),1)      

                data_dict['TCR_RQD_depth'] = previous_data_dict.get('TCR_RQD_depth', []) + data_dict['TCR_RQD_depth']

            else: # 첫 페이지이면
                if data_dict['TCR_RQD_depth'][0][0] == 0:
                    data_dict['TCR_RQD_depth'][0][0] = '0'


        # elif key == 'TCR_RQD_thickness':
        #     if not value[0]:
        #         data_dict['TCR_RQD_thickness'] = data_dict['TCR_RQD_thickness'][1:]

        #     _type = data_dict['TCR_RQD_thickness'].pop(-1)

        #     if is_continuation:
        #         if _type == 0:
        #             if previous_data_dict.get('TCR_RQD_depth'):
        #                 _start_depth = float(previous_data_dict['TCR_RQD_depth'][-1][-1])
        #             else:
        #                 if previous_data_dict.get('layer_depth'):
        #                     _start_depth = round(float(previous_data_dict['layer_depth'][-1]), 1)
        #                 else:
        #                     _start_depth = 0
        #         else: # scalebar를 통해 계산했을 때
        #             _start_depth = previous_data_dict['last_line_thickness']
        #         _tmp = []
        #         for thickness in data_dict['TCR_RQD_thickness']:
        #             if not thickness: continue
        #             _tmp += [[_start_depth + float(thickness[0]), _start_depth + float(thickness[1])]]

        #         data_dict['TCR_RQD_depth'] = _tmp
        #         if _tcr_rqd_addup: # tcr, rqd 가 페이지 나눠져서 들어가 있을 때
        #             previous_data_dict['TCR_RQD_depth'][-1][-1] = data_dict['TCR_RQD_depth'][0][-1]
        #             data_dict['TCR_RQD_depth'] = previous_data_dict.get('TCR_RQD_depth', [])[:] + data_dict['TCR_RQD_depth'][1:]

        #         else:
        #             data_dict['TCR_RQD_depth'] = previous_data_dict.get('TCR_RQD_depth', [])[:] + data_dict['TCR_RQD_depth']
        #     else: # 첫 페이지 일 때
        #         data_dict['TCR_RQD_thickness'] = [v for v in data_dict['TCR_RQD_thickness'] if v]
        #         _start_depth = data_dict['TCR_RQD_thickness'][0][0]
        #         _tmp = []
        #         for i, thickness in enumerate(data_dict['TCR_RQD_thickness']):
        #             _tmp += [[_start_depth, round(float(thickness[1]), 1)]]
        #             _start_depth = round(float(thickness[1]), 1)
        #         data_dict['TCR_RQD_depth'] = _tmp
        #     data_dict.pop('TCR_RQD_thickness')



        elif key == 'TCR':
            if not value[0]:
                data_dict['TCR'] = data_dict['TCR'][1:]

            if is_continuation:
                data_dict['TCR'] = previous_data_dict.get('TCR', []) + data_dict['TCR']


        elif key == 'TCR_depth':
            if not value[0]:
                data_dict['TCR_depth'] = data_dict['TCR_depth'][1:]

            if is_continuation:
                _start_depth = previous_data_dict['TCR_depth'][-1][-1] if previous_data_dict.get('TCR_depth') \
                                else round(float(previous_data_dict['layer_depth'][-1]), 1)

                data_dict['TCR_depth'][0][0] = _start_depth            

                data_dict['TCR_depth'] = previous_data_dict.get('TCR_depth', []) + data_dict['TCR_depth']

            else: # 첫 페이지이면
                if data_dict['TCR_depth'][0][0] == 0:
                    data_dict['TCR_depth'][0][0] = '0'


        # elif key == 'TCR_thickness':
        #     if not value[0]:
        #         data_dict['TCR_thickness'] = data_dict['TCR_thickness'][1:]

        #     _type = data_dict['TCR_thickness'].pop(-1)

        #     if is_continuation:
        #         if _type == 0:
        #             if previous_data_dict.get('TCR_depth'):
        #                 _start_depth = float(previous_data_dict['TCR_depth'][-1][-1])
        #             else:
        #                 if previous_data_dict.get('layer_depth'):
        #                     _start_depth = round(float(previous_data_dict['layer_depth'][-1]), 1)
        #                 else:
        #                     _start_depth = 0
        #         else: # scalebar를 통해 계산했을 때
        #             _start_depth = previous_data_dict['last_line_thickness']
        #         _tmp = []
        #         for thickness in data_dict['TCR_thickness']:
        #             if not thickness: continue
        #             _tmp += [[_start_depth + float(thickness[0]), _start_depth + float(thickness[1])]]

        #         data_dict['TCR_depth'] = _tmp
        #         # if _tcr_rqd_addup: # tcr, rqd 가 페이지 나눠져서 들어가 있을 때
        #         #     previous_data_dict['TCR_depth'][-1][-1] = data_dict['TCR_depth'][0][-1]
        #         #     data_dict['TCR_depth'] = previous_data_dict.get('TCR_depth', [])[:] + data_dict['TCR_depth'][1:]

        #         # else:
        #         data_dict['TCR_depth'] = previous_data_dict.get('TCR_depth', [])[:] + data_dict['TCR_depth']

        #     else: # 첫 페이지 일 때
        #         data_dict['TCR_thickness'] = [v for v in data_dict['TCR_thickness'] if v]
        #         _start_depth = data_dict['TCR_thickness'][0][0]
        #         _tmp = []
        #         for i, thickness in enumerate(data_dict['TCR_thickness']):
        #             _tmp += [[_start_depth, round(float(thickness[1]), 1)]]
        #             _start_depth = round(float(thickness[1]), 1)
        #         data_dict['TCR_depth'] = _tmp
        #     data_dict.pop('TCR_thickness')



        elif key == 'RQD':
            if not value[0]:
                data_dict['RQD'] = data_dict['RQD'][1:]

            if is_continuation:
                data_dict['RQD'] = previous_data_dict.get('RQD', []) + data_dict['RQD']


        elif key == 'RQD_depth':
            if not value[0]:
                data_dict['RQD_depth'] = data_dict['RQD_depth'][1:]

            if is_continuation:
                _start_depth = previous_data_dict['RQD_depth'][-1][-1] if previous_data_dict.get('RQD_depth') \
                                else round(float(previous_data_dict['layer_depth'][-1]), 1)

                data_dict['RQD_depth'][0][0] = _start_depth            

                data_dict['RQD_depth'] = previous_data_dict.get('RQD_depth', []) + data_dict['RQD_depth']

            else: # 첫 페이지이면
                if data_dict['RQD_depth'][0][0] == 0:
                    data_dict['RQD_depth'][0][0] = '0'


        elif key == 'joint_max':
            if not value[0]:
                data_dict['joint_max'] = data_dict['joint_max'][1:]

            if is_continuation:
                data_dict['joint_max'] = previous_data_dict.get('joint_max', []) + data_dict['joint_max']


        elif key == 'joint_max_depth':
            if not value[0]:
                data_dict['joint_max_depth'] = data_dict['joint_max_depth'][1:]

            if is_continuation:
                _start_depth = previous_data_dict['joint_max_depth'][-1][-1] if previous_data_dict.get('joint_max_depth') \
                                else round(float(previous_data_dict['layer_depth'][-1]), 1)

                data_dict['joint_max_depth'][0][0] = _start_depth            

                data_dict['joint_max_depth'] = previous_data_dict.get('joint_max_depth', []) + data_dict['joint_max_depth']

            else: # 첫 페이지이면
                if data_dict['joint_max_depth'][0][0] == 0:
                    data_dict['joint_max_depth'][0][0] = '0'


        elif key == 'joint_min':
            if not value[0]:
                data_dict['joint_min'] = data_dict['joint_min'][1:]

            if is_continuation:
                data_dict['joint_min'] = previous_data_dict.get('joint_min', []) + data_dict['joint_min']


        elif key == 'joint_min_depth':
            if not value[0]:
                data_dict['joint_min_depth'] = data_dict['joint_min_depth'][1:]

            if is_continuation:
                _start_depth = previous_data_dict['joint_min_depth'][-1][-1] if previous_data_dict.get('joint_min_depth') \
                                else round(float(previous_data_dict['layer_depth'][-1]), 1)

                data_dict['joint_min_depth'][0][0] = _start_depth            

                data_dict['joint_min_depth'] = previous_data_dict.get('joint_min_depth', []) + data_dict['joint_min_depth']

            else: # 첫 페이지이면
                if data_dict['joint_min_depth'][0][0] == 0:
                    data_dict['joint_min_depth'][0][0] = '0'



        elif key == 'joint_avg':
            if not value[0]:
                data_dict['joint_avg'] = data_dict['joint_avg'][1:]

            if is_continuation:
                data_dict['joint_avg'] = previous_data_dict.get('joint_avg', []) + data_dict['joint_avg']


        elif key == 'joint_avg_depth':
            if not value[0]:
                data_dict['joint_avg_depth'] = data_dict['joint_avg_depth'][1:]

            if is_continuation:
                _start_depth = previous_data_dict['joint_avg_depth'][-1][-1] if previous_data_dict.get('joint_avg_depth') \
                                else round(float(previous_data_dict['layer_depth'][-1]), 1)

                data_dict['joint_avg_depth'][0][0] = _start_depth            

                data_dict['joint_avg_depth'] = previous_data_dict.get('joint_avg_depth', []) + data_dict['joint_avg_depth']

            else: # 첫 페이지이면
                if data_dict['joint_avg_depth'][0][0] == 0:
                    data_dict['joint_avg_depth'][0][0] = '0'

        elif key == 'weathered':
            if not value[0]:
                data_dict['weathered'] = data_dict['weathered'][1:]

            if is_continuation:
                data_dict['weathered'] = previous_data_dict.get('weathered', []) + data_dict['weathered']


        elif key == 'weathered_depth':
            if not value[0]:
                data_dict['weathered_depth'] = data_dict['weathered_depth'][1:]

            if is_continuation:
                _start_depth = previous_data_dict['weathered_depth'][-1][-1] if previous_data_dict.get('weathered_depth') \
                                else round(float(previous_data_dict['layer_depth'][-1]), 1)

                data_dict['weathered_depth'][0][0] = _start_depth            

                data_dict['weathered_depth'] = previous_data_dict.get('weathered_depth', []) + data_dict['weathered_depth']

            else: # 첫 페이지이면
                if data_dict['weathered_depth'][0][0] == 0:
                    data_dict['weathered_depth'][0][0] = '0'

    return data_dict


_layer_uscs = {
               '풍화토': ['풍화토'],
               '풍화암': ['풍화암'],
               '연암': ['연암'],
               '보통암': ['보통암'],
               '경암': ['경암'],
               '실트질모래': ['실트질모래', 'SM'],
               '실트질점토': ['실트섞인점토', 'CL', '실트질점토']}


def postprocessing_nvalue(data_dict, N_depth, N):

    # N치 겹칠 경우
    _nd_before = ''
    nn = []
    n_cm = []
    _del = 0
    if N:
        for i, (nd, n) in enumerate(zip(N_depth[:], N[:])):
            if _nd_before != nd:
                nums = n.split('/')
                nn += [nums[0]]
                n_cm += [nums[1]]
                _nd_before = nd
            else:
                N_depth.pop(i-_del)
                _nd_before = nd
                _del += 1
                continue
        data_dict['N'] = nn
        data_dict['N_cm'] = n_cm
        data_dict['N_depth'] = N_depth

    return data_dict



def postprocessing_tcrrqd(data_dict, tcr_rqd, tcr_rqd_depth, tcr, tcr_depth, rqd, rqd_depth):

    _tr_before = ''
    tcr_rqd = [v for v in tcr_rqd if v]
    tcr_rqd_depth = [v for v in tcr_rqd_depth if v]
    _del = 0
    if tcr_rqd:
        for i, (trd, tr) in enumerate(zip(tcr_rqd_depth[:], tcr_rqd[:])):
            if _tr_before != tr:
                nums = tr.split('/')
                tcr_rqd[i] = list(nums)
                _tr_before = tr
            else:
                cur_dep = tcr_rqd_depth.pop(i-_del)
                tcr_rqd_depth[i-_del-1][-1] = cur_dep[0]
                _tr_before = tr
                _del += 1
                continue
        data_dict['TCR_RQD'] = tcr_rqd
        data_dict['TCR_RQD_depth'] = tcr_rqd_depth



    tcr = [v for v in tcr if v]
    tcr_depth = [v for v in tcr_depth if v]
    rqd = [v for v in rqd if v]
    rqd_depth = [v for v in rqd_depth if v]
    tcr_rqd = []
    if tcr and rqd:
        for i, (t, r) in enumerate(zip(tcr, rqd)):
            tcr_rqd += [[t, r]]
        _depth = tcr_depth
        data_dict['TCR_RQD'] = tcr_rqd
        data_dict['TCR_RQD_depth'] = _depth

    return data_dict


def postprocessing_joint(data_dict, joint_max, joint_max_depth, joint_min, joint_avg):
    joint_max = [v for v in joint_max if v]
    joint_max_depth = [v for v in joint_max_depth if v]
    joint_min = [v for v in joint_min if v]
    joint_min_depth = [v for v in joint_max_depth if v]
    joint_avg = [v for v in joint_avg if v]
    joint_avg_depth = [v for v in joint_max_depth if v]

    joint = []
    if joint_max:
        for i, (j_max, j_min, j_avg) in enumerate(zip(joint_max, joint_min, joint_avg)):
            joint += [[j_max, j_min, j_avg]]
        joint_depth = joint_max_depth

        data_dict['joint'] = joint
        data_dict['joint_depth'] = joint_depth
    return data_dict



def postprocessing_layerblock(data_dict, layer_dict, layer_description, layer_name, layer_uscs):
    # layer_depth: 실제 레이어만큼 있음
    # layer_description

    # _layer_num = len(layer_dict)
    # _layer_index = _layer_num-1

    # # print(layer_dict)
    # if not layer_dict[_layer_index].get('thickness', ''):
    #     layer_dict.pop(_layer_index)
    # if not layer_description[-1]:
    #     layer_description = layer_description[:-1]        

    # layer_depth = [l['thickness'] for l in layer_dict.values()]
    # layer_name = [l['layer_name'] for l in layer_dict.values()]
    # layer_uscs = [l['layer_USCS'] for l in layer_dict.values()]


    if len(layer_dict) > len(layer_description):
        if ([v for v in layer_name if v]):
            new_description = [[] for v in range(len(layer_dict))]
            des_id = 0
            for i, name in enumerate(layer_name):
                if i == 0:
                    new_description[i] = layer_description[des_id]
                    continue

                first_line = layer_description[des_id][0]
                _name_made = ''.join(re.findall(korean_regex, first_line))

                if (_name_made.replace(' ', '').replace('층', '') == name.replace(' ', '').replace('층', '')):
                    new_description[i] = layer_description[des_id]
                    des_id += 1
                else: 
                    new_description[i] = new_description[i-1]
            layer_description = new_description

    # print(borehole)
    # print(layer_description)
    # print(layer_name)
    # print(layer_uscs)

    # layer uscs 없을 때 처리
    try:
        for i, des in enumerate(layer_description):
            if not des: continue

            first_line = des[0]
            _name_made = ''.join(re.findall(korean_regex, first_line))
            # layer_name_from_description += [_name_made]

            if not layer_name[i]:
                layer_name[i] = _name_made
                if not layer_uscs[i]:
                    for u, vars in _layer_uscs.items():
                        for var in vars:
                            if var in ''.join(des).replace(' ', '').upper():
                                uscs = u
                                break
                            else:
                                uscs = ''
                                break
                        if uscs:
                            layer_uscs[i] = uscs
                            break
            else:
                name = layer_name[i]
                if layer_uscs[i]: continue

                if (_name_made.replace('층', '') != name.replace('층', '')) and not layer_uscs[i]:
                    layer_uscs[i] = name
                elif (_name_made.replace('층', '') == name.replace('층', '')) and not layer_uscs[i]:
                    # uscs 결정 필요
                    for u, vars in _layer_uscs.items():
                        for var in vars:
                            if var in ''.join(des).replace(' ', '').replace('\n', '').upper():
                                uscs = u
                                break
                            else:
                                uscs = ''
                                break
                        if uscs:
                            layer_uscs[i] = uscs
                            break
    except:
        # 개수가 안맞을 때 오류가 난다
        # 일반적으로 layer_description
        layer_description = ['' for v in range(len(layer_dict))]
        layer_uscs = layer_uscs


    # data_dict['layer_depth'] = layer_depth
    data_dict['layer_description'] = layer_description
    # data_dict['layer_name'] = layer_name
    data_dict['layer_USCS'] = layer_uscs

    return data_dict


def final_postprocessing(data_dict):
    
    # 데이터 뽑기
    easting = data_dict.get('coordinates_y', '')
    northing = data_dict.get('coordinates_x', '')
    elevation = data_dict.get('elevation', '')
    date = data_dict.get('date', '')
    watertable = data_dict.get('watertable', '')
    holedia = data_dict.get('holedia', '')

    layer_dict = data_dict.get('layer_dict', [])
    layer_depth = data_dict.get('layer_depth', [])
    layer_name = data_dict.get('layer_name', [])

    layer_uscs = data_dict.get('layer_USCS', [])
    layer_description = data_dict.get('layer_description', [])

    N_depth = data_dict.get('N_depth', [])
    N = data_dict.get('N', [])
    
    tcr_rqd = data_dict.get('TCR_RQD', [])
    tcr_rqd_depth = data_dict.get('TCR_RQD_depth', [])
    tcr = data_dict.get('TCR', [])
    tcr_depth = data_dict.get('TCR_depth', [])
    rqd = data_dict.get('RQD', [])
    rqd_depth = data_dict.get('RQD_depth', [])
    joint_max = data_dict.get('joint_max', [])
    joint_max_depth = data_dict.get('joint_max_depth', [])
    joint_min = data_dict.get('joint_min', [])
    joint_min_depth = data_dict.get('joint_min_depth', [])
    joint_avg = data_dict.get('joint_avg', [])
    joint_avg_depth = data_dict.get('joint_avg_depth', [])
    weathered = data_dict.get('weathered', [])
    weathered_depth = data_dict.get('weathered_depth', [])


    # N치 겹칠 경우
    # _nd_before = ''
    # nn = []
    # n_cm = []
    # _del = 0
    # if N:
    #     for i, (nd, n) in enumerate(zip(N_depth[:], N[:])):
    #         if _nd_before != nd:
    #             nums = n.split('/')
    #             nn += [nums[0]]
    #             n_cm += [nums[1]]
    #             _nd_before = nd
    #         else:
    #             N_depth.pop(i-_del)
    #             _nd_before = nd
    #             _del += 1
    #             continue
    #     data_dict['N'] = nn
    #     data_dict['N_cm'] = n_cm
    #     data_dict['N_depth'] = N_depth
    try:
        data_dict = postprocessing_nvalue(data_dict, N_depth, N)
    except:
        data_dict = data_dict


    # tcr family 겹칠 경우
    # _tr_before = ''
    # tcr_rqd = [v for v in tcr_rqd if v]
    # tcr_rqd_depth = [v for v in tcr_rqd_depth if v]
    # _del = 0
    # if tcr_rqd:
    #     for i, (trd, tr) in enumerate(zip(tcr_rqd_depth[:], tcr_rqd[:])):
    #         if _tr_before != tr:
    #             nums = tr.split('/')
    #             tcr_rqd[i] = list(nums)
    #             _tr_before = tr
    #         else:
    #             cur_dep = tcr_rqd_depth.pop(i-_del)
    #             tcr_rqd_depth[i-_del-1][-1] = cur_dep[0]
    #             _tr_before = tr
    #             _del += 1
    #             continue
    #     data_dict['TCR_RQD'] = tcr_rqd
    #     data_dict['TCR_RQD_depth'] = tcr_rqd_depth



    # tcr = [v for v in tcr if v]
    # tcr_depth = [v for v in tcr_depth if v]
    # rqd = [v for v in rqd if v]
    # rqd_depth = [v for v in rqd_depth if v]
    # tcr_rqd = []
    # if tcr and rqd:
    #     for i, (t, r) in enumerate(zip(tcr, rqd)):
    #         tcr_rqd += [[t, r]]
    #     _depth = tcr_depth
    #     data_dict['TCR_RQD'] = tcr_rqd
    #     data_dict['TCR_RQD_depth'] = _depth
    try:
        data_dict = postprocessing_tcrrqd(data_dict, tcr_rqd, tcr_rqd_depth, tcr, tcr_depth, rqd, rqd_depth)
    except:
        data_dict = data_dict

    
    # joint family
    # joint_max = [v for v in joint_max if v]
    # joint_max_depth = [v for v in joint_max_depth if v]
    # joint_min = [v for v in joint_min if v]
    # joint_min_depth = [v for v in joint_max_depth if v]
    # joint_avg = [v for v in joint_avg if v]
    # joint_avg_depth = [v for v in joint_max_depth if v]

    # joint = []
    # if joint_max:
    #     for i, (j_max, j_min, j_avg) in enumerate(zip(joint_max, joint_min, joint_avg)):
    #         joint += [[j_max, j_min, j_avg]]
    #     joint_depth = joint_max_depth

    #     data_dict['joint'] = joint
    #     data_dict['joint_depth'] = joint_depth
    try:
        data_dict = postprocessing_joint(data_dict, joint_max, joint_max_depth, joint_min, joint_avg)
    except:
        data_dict = data_dict



    # layer name, layer uscs, layer description
    # layer dict, layer description 맨 끝 지우기
        
    # print(borehole)
    # print(layer_description)
    # print(layer_dict)
    
    try:
        _layer_num = len(layer_dict)
        _layer_index = _layer_num-1

        # print(layer_dict)
        if not layer_dict[_layer_index].get('thickness', ''):
            layer_dict.pop(_layer_index)
        if not layer_description[-1]:
            layer_description = layer_description[:-1]        

        layer_depth = [l['thickness'] for l in layer_dict.values()]
        layer_name = [l['layer_name'] for l in layer_dict.values()]
        layer_uscs = [l['layer_USCS'] for l in layer_dict.values()]

        data_dict['layer_depth'] = layer_depth
        data_dict['layer_name'] = layer_name
        data_dict = postprocessing_layerblock(data_dict, layer_dict, layer_description, layer_name, layer_uscs)
    except:
        data_dict = data_dict

    


    # if len(layer_dict) > len(layer_description):
    #     if ([v for v in layer_name if v]):
    #         new_description = [[] for v in range(len(layer_dict))]
    #         des_id = 0
    #         for i, name in enumerate(layer_name):
    #             if i == 0:
    #                 new_description[i] = layer_description[des_id]
    #                 continue

    #             first_line = layer_description[des_id][0]
    #             _name_made = ''.join(re.findall(korean_regex, first_line))

    #             if (_name_made.replace(' ', '').replace('층', '') == name.replace(' ', '').replace('층', '')):
    #                 new_description[i] = layer_description[des_id]
    #                 des_id += 1
    #             else: 
    #                 new_description[i] = new_description[i-1]
    #         layer_description = new_description

    # # print(borehole)
    # # print(layer_description)
    # # print(layer_name)
    # # print(layer_uscs)

    # # layer uscs 없을 때 처리
    # try:
    #     for i, des in enumerate(layer_description):
    #         if not des: continue

    #         first_line = des[0]
    #         _name_made = ''.join(re.findall(korean_regex, first_line))
    #         # layer_name_from_description += [_name_made]

    #         if not layer_name[i]:
    #             layer_name[i] = _name_made
    #             if not layer_uscs[i]:
    #                 for u, vars in _layer_uscs.items():
    #                     for var in vars:
    #                         if var in ''.join(des).replace(' ', '').upper():
    #                             uscs = u
    #                             break
    #                         else:
    #                             uscs = ''
    #                             break
    #                     if uscs:
    #                         layer_uscs[i] = uscs
    #                         break
    #         else:
    #             name = layer_name[i]
    #             if layer_uscs[i]: continue

    #             if (_name_made.replace('층', '') != name.replace('층', '')) and not layer_uscs[i]:
    #                 layer_uscs[i] = name
    #             elif (_name_made.replace('층', '') == name.replace('층', '')) and not layer_uscs[i]:
    #                 # uscs 결정 필요
    #                 for u, vars in _layer_uscs.items():
    #                     for var in vars:
    #                         if var in ''.join(des).replace(' ', '').replace('\n', '').upper():
    #                             uscs = u
    #                             break
    #                         else:
    #                             uscs = ''
    #                             break
    #                     if uscs:
    #                         layer_uscs[i] = uscs
    #                         break
    # except:
    #     layer_uscs = layer_uscs

    # data_dict['layer_depth'] = layer_depth
    # data_dict['layer_description'] = layer_description
    # data_dict['layer_name'] = layer_name
    # data_dict['layer_USCS'] = layer_uscs

    




    weathered = [v for v in weathered if v]
    weathered_depth = [v for v in weathered_depth if v]

    # dataset_dict[bh] = data_dict


    return data_dict




def formatting(data_dict, datas):
    # datas = {}
    # print(datas)
    LOCA = datas.get('LOCA', [])
    WSTD = datas.get('WSTD', [])
    SAMP = datas.get('SAMP', [])
    CORE = datas.get('CORE', [])
    CDIA = datas.get('CDIA', [])
    GEOL = datas.get('GEOL', [])
    DISC = datas.get('DISC', [])
    WETH = datas.get('WETH', [])
    FRAC = datas.get('FRAC', [])
    ISPT = datas.get('ISPT', [])

    # for data_dict in dataset_dict.values():
    # try:
    borehole = data_dict.get('borehole', '')

    easting = data_dict.get('coordinates_y', '')
    northing = data_dict.get('coordinates_x', '')
    elevation = data_dict.get('elevation', '')
    date = data_dict.get('date', '')
    watertable = data_dict.get('watertable', '')
    holedia = data_dict.get('holedia', '')

    layer_depth = data_dict.get('layer_depth', [])
    layer_thickness = data_dict.get('layer_thickness', [])
    layer_name = data_dict.get('layer_name', [])
    # print(borehole)
    if layer_name:
        for i, text in enumerate(layer_name):
            if not text: continue
            if text[-1] == '층':
                continue
            else:
                layer_name[i] = text+'층'
    layer_uscs = data_dict.get('layer_USCS', [])
    layer_description = data_dict.get('layer_description', [])

    N_depth = data_dict.get('N_depth', [])
    N = data_dict.get('N', [])
    N_cm = data_dict.get('N_cm', [])
    
    tcr_rqd = data_dict.get('TCR_RQD', [])
    tcr_rqd_depth = data_dict.get('TCR_RQD_depth', [])
    tcr = data_dict.get('TCR', [])
    tcr_depth = data_dict.get('TCR_depth', [])
    rqd = data_dict.get('RQD', [])
    rqd_depth = data_dict.get('RQD_depth', [])
    joint_max = data_dict.get('joint_max', [])
    joint_max_depth = data_dict.get('joint_max_depth', [])
    joint_min = data_dict.get('joint_min', [])
    joint_min_depth = data_dict.get('joint_min_depth', [])
    joint_avg = data_dict.get('joint_avg', [])
    joint_avg_depth = data_dict.get('joint_avg_depth', [])
    weathered = data_dict.get('weathered', [])
    weathered_depth = data_dict.get('weathered_depth', [])

    joint = data_dict.get('joint', [])
    joint_depth = data_dict.get('joint_depth', [])

    
    # WSTD
    WSTD.append([borehole, watertable])

    # SAMP
    SAMP.append([borehole, '', '', '', '', '', '', '', '', '', ''])

    # CORE
    for rock_prop, prop_depth in zip(tcr_rqd, tcr_rqd_depth):
        CORE.append([borehole, str(prop_depth[0]), str(prop_depth[1]), str(rock_prop[0]), str(rock_prop[1]), str(holedia)])

    

    # GEOL
    # print(borehole)
    # print(layer_depth)
    # print(layer_name)
    # print(layer_description)
    # print(layer_uscs)
    geol_borehole = []
    for i, depth in enumerate(layer_depth):
        if layer_name:
            layer = layer_name[i]
            # h_upper = round(float(h_lower), 1)
            # h_lower = round(h_lower + round(float(thickness), 1), 1)
            h_upper = 0 if i==0 else h_lower
            h_lower = depth
            try:
                uscs = layer_uscs[i]
            except:
                uscs = ''

            try:
                layer_disc = '\n'.join(layer_description[i])
            except:
                layer_disc = ''

            GEOL.append([borehole, layer, str(h_upper), str(h_lower), uscs, '', layer_disc])
            geol_borehole.append([borehole, layer, str(h_upper), str(h_lower), uscs, '', layer_disc])
        else:
            continue


    # DISC
    for i, description in enumerate(layer_description):
        description_text = ''.join(description).replace(' ', '').upper()

        coreloss = 1 if 'CORELOSS' in description_text else 0
        frac = 1 if '파쇄' in description_text else 0
        dike = 1 if ('암맥' in description_text) or ('맥암' in description_text) else 0
        fault = 1 if '단층' in description_text else 0
        if coreloss or frac or dike or fault:
            # h_top = layer_depth[0]
            # h_bottom = layer_depth[1]

            h_top = geol_borehole[i][2]
            h_bottom = geol_borehole[i][3]

            coreloss = 'o' if coreloss else ''
            frac = 'o' if frac else ''
            dike = 'o' if dike else ''
            fault = 'o' if fault else ''

            DISC.append([borehole, str(h_top), str(h_bottom), '', '', '', '', '', '', '', coreloss, frac, dike, fault])

    # WETH
    try:
        for w, w_depth in zip(weathered, weathered_depth):
            WETH.append([borehole, str(w_depth[0]), str(w_depth[1]), w])
    except:
        WETH.append([borehole, '', '', ''])


    # FRAC
    try:
        for j, j_depth in zip(joint, joint_depth):
            FRAC.append([borehole, str(j_depth[0]), str(j_depth[1]), '', str(j[0]), str(j[1]), str(j[2])])
    except:
        FRAC.append([borehole, '', '', '', '', '', ''])


    # ISPT
    if not N:
        ISPT.append([borehole, '', '', '', ''])
    else:
        h_lower = 0
        for i, depth in enumerate(N_depth):
            n = N[i]
            cm = N_cm[i]
            # ISPT.append([borehole, depth, n, str(int(cm)*10), str(int(50*300/int(n)*10))])
            if int(cm) != 0:
                ISPT.append([borehole, depth, n, str(int(cm)*10), str(int(30*int(n)/int(cm)))])
            else:
                ISPT.append([borehole, depth, n, str(int(cm)*10), ''])


    # LOCA
    LOCA.append([borehole, easting, northing, str(GEOL[-1][3]), elevation, '', date])

    # CDIA
    CDIA.append([borehole, str(GEOL[-1][3]), holedia])


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

    return datas
