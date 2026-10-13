

import shutil
import openpyxl

def page_list2str(pages):
    '''
    pages: page list <list>
    
    return: page_str <str>'''

    if not pages:
        return ''
    
    if len(pages) == 1:
        return str(pages[0]+1)

    pages.sort()
    min_page = min(pages)
    max_page = max(pages)

    page_group = []
    tmp_group = [pages[0]] # 그룹마다 정의
    for page in pages[1:]:
        before_page = tmp_group[-1]

        if page-before_page == 1:
            # 연속된 숫자일 경우
            tmp_group += [page]
        
        else:
            # 연속된 숫자가 아닐 경우
            page_group += [tmp_group]
            tmp_group = [page]

    page_group += [tmp_group]

    page_str = []
    for group in page_group:
        min_page = min(group)
        max_page = max(group)

        if min_page == max_page:
            group_str = str(min_page+1)
        else:
            group_str = '{min_page}-{max_page}'.format(min_page=min_page+1, max_page=max_page+1)
        page_str += [group_str]

    return ', '.join(page_str)
    

def page_str2list(page_str):
    # ui-formatted page string
    if not page_str:
        return []

    consecutive_page = page_str.split(', ')

    page_list = []
    for group in consecutive_page:

        if '-' in group:
            minPage, maxPage = tuple(group.split('-'))
            pages = [page-1 for page in range(int(minPage), int(maxPage)+1)]
        else:
            pages = [int(group)-1]

        page_list += pages

    # print(consecutive_page)
    return page_list


import os
def write_on_xlsx(data, template, dst_path):
    # 템플릿 복사
    if os.path.exists(dst_path):
        os.remove(dst_path)
    shutil.copy(template, dst_path)

    wb = openpyxl.load_workbook(dst_path)

    for sheet_name, values in data.items():
        if not values:
            continue

        sheet = wb[sheet_name]

        for row_id, row_value in enumerate(values, start=6):
            for col_id, value in enumerate(row_value, start=2):
                if not value: continue
                sheet.cell(row_id, col_id, value)

    wb.save(filename=dst_path)
    wb.close()




def save_logtxt(data, dst_path=None):
    if dst_path:
        txt_dst_path = dst_path.replace('xlsx', 'txt')

    raw_list = []

    for test_name, values in data.items():
    
        pages = values[0]  # [1, 2, 3]
        texts = values[1:]  # [[], [], []]

        for p, text in zip(pages, texts):
            cur_test = []

            cur_test += [p+1]
            cur_test += [test_name]
            cur_test += [text]

            raw_list += [cur_test]


    # 페이지로 정렬
    raw_list.sort(key=lambda data: data[0])


    txt_list = []
    # formatting
    for data in raw_list:
        txt_list += ['\n']
        txt_list += ['#'*40]
        txt_list += ['page = {}'.format(str(data[0]))]
        txt_list += ['test name = {}'.format(data[1])]
        txt_list += ['text = {\n']

        for text in data[2]:
            txt_list += [str(text)]

        txt_list += ['\n}']
        
    
    try:
        f = open(txt_dst_path, "w", encoding='utf-8')
        f.write('\n'.join(txt_list))
        f.close()
    except:
        f = open(txt_dst_path, "w", encoding='cp949')
        f.write('\n'.join(txt_list))
        f.close()

    # print(raw_list)
