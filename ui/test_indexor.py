

import os, sys

import tkinter
from tkinter import filedialog
import tkinter.ttk
import tkinter.messagebox
import tkinter.font

import customtkinter
from PIL import ImageTk, Image

from ui.utils import *


# def page_list2str(pages):
#     '''
#     pages: page list <list>
    
#     return: page_str <str>'''

#     if not pages:
#         return ''
    
#     if len(pages) == 1:
#         return str(pages[0]+1)

#     pages.sort()
#     min_page = min(pages)
#     max_page = max(pages)

#     page_group = []
#     tmp_group = [pages[0]] # 그룹마다 정의
#     for page in pages[1:]:
#         before_page = tmp_group[-1]

#         if page-before_page == 1:
#             # 연속된 숫자일 경우
#             tmp_group += [page]
        
#         else:
#             # 연속된 숫자가 아닐 경우
#             page_group += [tmp_group]
#             tmp_group = [page]

#     page_group += [tmp_group]

#     page_str = []
#     for group in page_group:
#         min_page = min(group)
#         max_page = max(group)

#         if min_page == max_page:
#             group_str = str(min_page+1)
#         else:
#             group_str = '{min_page}-{max_page}'.format(min_page=min_page+1, max_page=max_page+1)
#         page_str += [group_str]

#     return ', '.join(page_str)
    

# def page_str2list(page_str):
#     # ui-formatted page string
#     if not page_str:
#         return []

#     consecutive_page = page_str.split(', ')

#     page_list = []
#     for group in consecutive_page:

#         if '-' in group:
#             minPage, maxPage = tuple(group.split('-'))
#             pages = [page for page in range(int(minPage), int(maxPage)+1)]
#         else:
#             pages = [int(group)]

#         page_list += pages

#     # print(consecutive_page)
#     return page_list







class TestIndexor(customtkinter.CTkFrame):

    def __init__(self, master, controller, *args, **kwargs):
        
        super().__init__(master, *args, **kwargs)
        
        self.frame = master
        self.controller = controller
        self.image_manager = controller.asset_manager

        # default 
        self.defalut_tests = self.controller.TESTS_DISPLAYED
        self.default_activated_labels = self.controller.TEST_ACTIVATED # 전체 모두
        self._to_extract = []
        self._focus = None
        

        self.style = tkinter.ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("d.Treeview", background="white", foreground="black", fieldbackground="white", bd=1, font=('맑은 고딕', 11),
                             rowheight=21)
        self.style.configure('d.Treeview.Heading', font=('맑은 고딕', 11))


        self.selected_icon = self.image_manager.selected_icon
        self.unselected_icon = self.image_manager.unselected_icon
        self.inactive_icon = self.image_manager.inactive_icon


        # widgets
        self.title = customtkinter.CTkLabel(self, text='Tests', font=customtkinter.CTkFont("arial", size=16, weight='bold'))

        self.tv_frame = customtkinter.CTkFrame(self, bg_color='transparent')
        self.tv_frame.grid_columnconfigure(0, weight=1)
        self.tv_frame.grid_rowconfigure(0, weight=1)
        

        self.test_table = tkinter.ttk.Treeview(self.tv_frame, columns=['시험목록', "Pages", '속성'], height=12, style='d.Treeview', selectmode='none')
        self.test_table.column("#0", width=60, anchor='e', stretch=False)
        self.test_table.heading("#0",text='선택', command=self.select_all, image=self.unselected_icon)

        self.test_table.column('시험목록', width=300, anchor='w', stretch=False)
        self.test_table.heading('시험목록',text="시험목록")
        self.test_table.column("Pages", width=10, anchor='center')
        self.test_table.heading("Pages",text="Pages")
        self.test_table.column("속성", width=10, anchor='center')
        self.test_table.heading("속성",text="속성")
        
        for test in self.defalut_tests:
            self.test_table.insert('', 'end', text='', values=[' '+test, '', ''],iid=test, tags='default')

        self.test_table.tag_configure("default", foreground="#A9A9A9")
        self.test_table.tag_configure("nontarget", foreground="#A9A9A9", background='#EEEEE8') # 페이지 없거나, 추출 타겟이 아닐 때
        self.test_table.tag_configure('unextractable', foreground='black') # 텍스트 추출이 불가할 때
        self.test_table.tag_configure('extractable', foreground='black') # 추출이 가능할 때


        ####
        # tkinter.Button(self, text='test', command=self.test).pack()    
    
        self.vsb = tkinter.ttk.Scrollbar(self.tv_frame, orient="vertical", command=self.test_table.yview)
        self.title.pack(anchor='w', ipadx=5, padx=20,) #  pady=(15, 0)
        self.tv_frame.pack(side='right', fill='both', expand=True, padx=(20, 20)) # 
        self.test_table.grid(row=0, column=0, sticky='nswe')
        self.vsb.grid(row=0, column=1, sticky='ns')
        

        self.test_table.configure(yscrollcommand=self.vsb.set)

        self.test_table.bind('<Double-Button-1>', self.doubleclick) # ,self.doubleclick
        self.test_table.bind('<ButtonRelease-1>', self._on_click)

        #
        self.currentTest = tkinter.StringVar()
        self.currentPageId = tkinter.IntVar()
    

    def _update(self, test_dict, option_selection):
        ''' 
        test_dict: {'slake durability': {'active': 1, 'extractable': 1, 'pages_id': []}, }'''


        # 초기화
        for test in self.defalut_tests:
            self.test_table.delete(test)
            self.test_table.insert('', 'end', text='', values=[' '+test, '', ''],iid=test, tags='default')

        if not test_dict:
            return
        

        self.test_table.config(selectmode='browse')
        self.test_table.heading("#0",text='선택', command=self.select_all, image=self.selected_icon) # 

        self.activated_labels = self.default_activated_labels[:]
        for iid, info in test_dict.items():
            # iid: test_name
            

            pages_id = info['pages_id']
            page = page_list2str(pages_id)
            is_active = info['active']
            is_extractable = info['extractable']
            value_extractable = '⚠' if not is_extractable else ''

            
            
            if (not is_active) or (not page): 
                self.test_table.item(iid, values=[' '+iid, page, value_extractable], tags='nontarget')
                if is_active:                
                    self.activated_labels.remove(iid)

            else:
                if not is_extractable:
                    self.test_table.item(iid, values=[' '+iid, page, value_extractable], tags='unextractable', image=self.inactive_icon)
                    self.activated_labels.remove(iid)
                else:
                    if option_selection[iid].get():
                        self.test_table.item(iid, values=[' '+iid, page, value_extractable], tags='extractable', image=self.selected_icon)
                        self._to_extract += [iid]
                    else:
                        self.test_table.item(iid, values=[' '+iid, page, value_extractable], tags='extractable', image=self.unselected_icon)
                        # self._to_extract += [iid]

        self.activated_labels = tuple(self.activated_labels)
        self._to_extract = list(self.activated_labels[:])


    def _check_allSelected(self):

        if set(self.activated_labels) - set(self._to_extract):
            return 0
        else:
            return 1


    def select_all(self):

        if self._check_allSelected():
            # 모두 추출하기로 되어있으면
            # 전체 해제
            self.test_table.heading("#0", image=self.unselected_icon)
            for test_iid in self.activated_labels:
                self._to_extract.remove(test_iid)
                self.test_table.item(test_iid, image=self.unselected_icon)

        else:
            self.test_table.heading("#0", image=self.selected_icon)
            for test_iid in self.activated_labels:
                self._to_extract += [test_iid]
                self.test_table.item(test_iid, image=self.selected_icon)

        return True


    def _on_click(self, event):

        if self.test_table.identify_region(event.x, event.y) == 'heading':
            return

        if self.test_table.identify_row(event.y) == '':
            return

        # 시험이 선택되었을 때
        test_iid = self.test_table.identify_row(event.y)
        selectValues = self.test_table.item(test_iid)

        page_str = str(selectValues['values'][1])
        tag = selectValues['tags'][0]

        pages_id = page_str2list(page_str)

        if not pages_id:
            return
        else:
            self.currentTest.set(test_iid)
            self.currentPageId.set(min(pages_id))



        # 체크 버튼 수정하고자 할 때
        if tag == 'extractable':
            if self.test_table.identify_region(event.x, event.y) == 'tree':

                if test_iid not in self._to_extract:
                    self.test_table.item(test_iid, image=self.selected_icon)
                    self._to_extract += [test_iid]

                elif test_iid in self._to_extract:
                    self.test_table.item(test_iid, image=self.unselected_icon)
                    self._to_extract.remove(test_iid)

                if self._check_allSelected():
                # 모두 추출하기로 되어있으면
                    self.test_table.heading("#0", image=self.selected_icon)
                else:
                    self.test_table.heading("#0", image=self.unselected_icon)



###########
    def doubleclick(self, event):        
                #마우스 위치 감지
        self.update()

        if self.test_table.identify_region(event.x, event.y) == 'heading':
            return

        if self.test_table.identify_row(event.y) == '':
            return
        
        if self.test_table.identify_column(event.x) not in ['#2'] :
            return

        column = self.test_table.identify_column(event.x)
        test_iid = self.test_table.identify_row(event.y)

        selectValues = self.test_table.item(test_iid)

                #마우스가 위치한 부분의 셀 크기 확인
        columnIndex = int(column[1:]) - 1
        columnBox = self.test_table.bbox(test_iid,column) # x, y, width, height # treeview 위젯에 대하여

                #확인 된 셀크기 기준으로 위에 새로운 임시 위젯 생성
        # self.vsb.grid_forget()


        entryEdit = tkinter.Entry(self, width = columnBox[2])
        entryEdit.place(x=self.tv_frame.winfo_x()+columnBox[0], y=self.tv_frame.winfo_y()+columnBox[1],
                        w=columnBox[2],h=columnBox[3]) # +columnBox[3]*2.25
        entryEdit.editingColumnIndex = columnIndex
        entryEdit.editingRowIndex = test_iid
        entryEdit.editingItemIid = test_iid
        entryEdit.insert(0,selectValues.get("values")[columnIndex])
        # entryEdit.insert(0, selectValues['values'][1])
        entryEdit.select_range(0,'end')
        entryEdit.focus()

                #임시 생성된 위젯에서 키 바인딩
        entryEdit.bind("<FocusOut>", self.on_focus_out)
        entryEdit.bind("<Return>",self.on_enter_pressed)
        entryEdit.bind("<Tab>",self.on_enter_pressed)
        

    def on_focus_out(self, event):
        event.widget.destroy()

        self.test_table.config(yscrollcommand=self.vsb.set)
        self.vsb.config(command=self.test_table.yview)

    def on_enter_pressed(self, event):
        new_text = event.widget.get()

        selectIid = event.widget.editingItemIid
        columnIndex = event.widget.editingColumnIndex

        currentValues = self.test_table.item(selectIid).get("values")
        currentValues[1] = new_text
        # currentValues = [new_text, '' , '']
        self.test_table.item(selectIid,values=currentValues)
        event.widget.destroy()

        self.test_table.config(yscrollcommand=self.vsb.set)
        self.vsb.config(command=self.test_table.yview)

###########
