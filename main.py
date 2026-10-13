

import os, sys
import time

from pprint import pprint

import tkinter
from tkinter import filedialog
import tkinter.ttk
import tkinter.messagebox
import tkinter.font as font

import customtkinter
from tksheet import Sheet


from assets.asset_manager import AssetManager
from settings import Settings

# from ui.uploader import Uploader
from ui.main_window import MainWindow

from ui.utils import *

from ui.popup_window import PopupWindow, PreprocessBar, DivideBar, ExtractBar

from divide.divider import Divider
from extract.main import MainExtractor

# import extract

from PIL import ImageTk, Image

import threading
from collections import namedtuple





customtkinter.set_appearance_mode("Light")
customtkinter.set_default_color_theme("dark-blue")


class App(customtkinter.CTk):

    def __init__(self,  *args, **kwargs):

        super().__init__()

        self.main_path = os.path.dirname(os.path.abspath(__file__))
        self.asset_manager = AssetManager(self.main_path)

        self.TESTS_DISPLAYED = Settings.TESTS_DISPLAYED
        self.TEST_ACTIVATED = Settings.TEST_ACTIVATED


        # UI
        self.title('Geo-Data Searcher')
        self.bind("<F11>", lambda event: self.attributes("-fullscreen",
                                    not self.attributes("-fullscreen")))
        self.minsize(1800, 970)
        self.geometry("+%d+%d" %(10, 10))


        # 기본 설정
        # 옵션
        self.option_selection = {'시추주상도': tkinter.IntVar(value=1),
                                 '공내재하시험': tkinter.IntVar(value=1),
                                 '공내전단시험': tkinter.IntVar(value=1),
                                 '현장투수시험': tkinter.IntVar(value=1),
                                 '하향식탄성파시험': tkinter.IntVar(value=1),
                                 '실내토질시험': tkinter.IntVar(value=1),
                                 '암석일축압축강도시험': tkinter.IntVar(value=1),
                                 '토질일축압축시험': tkinter.IntVar(value=1)}
        self.option_savelog = tkinter.IntVar(value=0)
        # app data
        self.appData = {}


        ## mainwindow_display section
        self.mainwindow = MainWindow(self)
        self.uploader = self.mainwindow.uploader
        self.process_navigator = self.mainwindow.process_navigator
        self.test_indexor = self.mainwindow.test_indexor
        self.data_editor = self.mainwindow.data_editor
        self.pdf_viewer = self.mainwindow.pdf_viewer


        # 사용자 클릭 시 reaction 항목
        self.uploader.currentPdf.trace_add('write', self.update_page)
        self.test_indexor.currentPageId.trace_add('write', lambda e, images, image_id: \
                                                  self.pdf_viewer._update(images=self.appData[self.uploader.currentPdf.get()]['images'], image_id=self.test_indexor.currentPageId.get()))
        self.pdf_viewer.currentImageId.trace_add('write', lambda e, n, image_id: self.get_imageId(ui_imageId=self.pdf_viewer.currentImageId.get()))

        # 시험
        self.currentTest = tkinter.StringVar()




    def show_about(self):
        tkinter.messagebox.showinfo(title="Program Info", 
                                    message="Version :  {} \nDate :  {} \nOS :  {}".format(Settings.VERSION, Settings.DATE, Settings.OS))



    def startThread(self, func, daemon=False):
        thread = threading.Thread(target=func)
        thread.daemon = daemon
        thread.start()



    def clear_all(self):

        self.appData = {}

        if not self.uploader.pdf_list.get_children():
            return

        for folder in self.uploader.pdf_list.get_children():
            files = self.uploader.pdf_list.get_children(folder)
            if not files:
                self.uploader.pdf_list.delete(folder)
            else:
                for f in files:
                    self.uploader.pdf_list.delete(f)
                self.uploader.pdf_list.delete(folder)

        self.test_indexor._update(None, self.option_selection)
        self.process_navigator._update(0)
        self.data_editor._update(None)
        self.pdf_viewer._update(images=None, image_id=None)

        # appData 초기화
        self.appData = {}



    def upload(self):
        files = filedialog.askopenfilenames(title='Upload PDF files', \
            filetypes=[("PDF 파일", "*.pdf")], \
            initialdir='C:/', multiple=True)
                
        if not files:
            return

        # set app workspace
        for pdf in files:
            if not self.appData.get(pdf, None):
                tmpDict = {}
                tmpDict['process'] = 0.2
                tmpDict['divided_result'] = {} # cnn + rule-based
                tmpDict['test_info'] = {} # ui-formatted divided result
                tmpDict['text'] = []
                tmpDict['raw_text'] = {}
                tmpDict['data_extracted'] = {}
                tmpDict['images'] = []
                tmpDict['image_id'] = 0
                tmpDict['extractor'] = None

                self.appData[pdf] = tmpDict

        # update ui
        self.uploader._update(files)
        if not self.uploader.currentPdf.get():
            self.process = 0.2
            self.process_navigator._update(self.process)

        self.mainwindow.filemenu2.entryconfig(0, state='active')


    def delete_pdf(self):
        curwork = self.uploader.currentPdf.get()

        self.appData.pop(curwork)
        self.uploader.currentPdf.set(None)

        self.uploader.pdf_list.delete(curwork)

        for folder in self.uploader.pdf_list.get_children():
            files = self.uploader.pdf_list.get_children(folder)
            if not files:
                self.uploader.pdf_list.delete(folder)

        if self.uploader.pdf_list.get_children():
            self.process_navigator._update(0.2)
        else:
            self.process_navigator._update(0)
            
        self.test_indexor._update(None, self.option_selection)
        self.data_editor._update(None)
        self.pdf_viewer._update(images=None, image_id=None)

        self.uploader.currentPdf.set(None)


    def update_page(self, var, index, mode):

        # 선택 파일이 바뀌었을 때
        curwork = self.uploader.currentPdf.get()
        
        if curwork:
            self.images = self.appData[curwork]['images']
            self.image_id = self.appData[curwork]['image_id']
            
            self.process_navigator._update(self.appData[curwork]['process'])
            self.test_indexor._update(self.appData[curwork]['test_info'], self.option_selection)
            self.data_editor._update(self.appData[curwork]['data_extracted'], self.appData[curwork]['extractor'])
            self.pdf_viewer._update(images=self.appData[curwork]['images'], image_id=self.appData[curwork]['image_id'])

            self.update_idletasks()



    def popup_preprocess(self):

        self.preprocess_popup = tkinter.Toplevel(self)
        self.preprocess_popup.geometry("300x110")
        self.preprocess_popup.resizable(0, 0)
        self.preprocess_popup.pack_propagate(0)

        # self.update()
        window_width = self.winfo_width()
        window_height = self.winfo_height()

        self.preprocess_popup.geometry("+%d+%d" %(int(self.winfo_x()+window_width/2-180),int(self.winfo_y()+window_height/2-60)))
        self.preprocess_popup.overrideredirect(True)
        self.preprocess_popup.attributes('-alpha',0.95)
        self.preprocess_popup.attributes('-topmost', True)
        self.preprocess_popup.grab_set()


        self.preprocess_bar = PreprocessBar(master=self.preprocess_popup, controller=self, 
                                            fg_color="gray99", border_width=2, border_color='gray60')
        self.preprocess_bar.pack(expand=True, fill='both')

        self.preprocess_bar.update()
        self.preprocess_bar.update_idletasks()
        self.preprocess_popup.update()
        self.preprocess_popup.update_idletasks()

        self.update()
        self.update_idletasks()


    def popup_divide(self):
        popup = tkinter.Toplevel(self)

        # self.update()
        window_width = self.winfo_width()
        window_height = self.winfo_height()

        popup.geometry("+%d+%d" %(int(self.winfo_x()+window_width/2-180),int(self.winfo_y()+window_height/2-60)))
        popup.overrideredirect(True)
        popup.attributes('-topmost', True)
        popup.grab_set()

        self.divide_bar = DivideBar(popup, self)
        self.divide_bar.pack()

        self.divide_bar.update()
        self.divide_bar.update_idletasks()
        popup.update()
        popup.update_idletasks()

        self.update()
        self.update_idletasks()


    def check_preprocess(self):
        
        if self.preprocess_threading.is_alive():
            # self.preprocess_bar.preprocess_bar.step()
            self.after(20, self.check_preprocess)
        else:
            time.sleep(1)

            self.configure(cursor='')

            self.main_analyze()


    def main_analyze(self):
        currentPdf = self.uploader.currentPdf.get()

        self.popup_divide()

        self.divider.divide_process.trace_add('write', 
                                lambda e, n, divide_process: 
                                self.divide_bar._update(divide_process=self.divider.divide_process))

        self.divider.divide(self.TESTS_DISPLAYED, self.TEST_ACTIVATED)

        # result
        process = 0.4
        test_info = self.divider.test_info_formatted
        data_extracted = dict(zip(self.data_editor.tabDict.keys(), [[[]] for v in range(len(self.data_editor.tabDict.keys()))]))
        images = self.divider.images
        image_id = 0

        # update 
        self.appData[currentPdf]['process'] = process
        self.appData[currentPdf]['test_info'] = test_info
        self.appData[currentPdf]['text'] = self.divider.page_tlines
        self.appData[currentPdf]['raw_text'] = {}
        self.appData[currentPdf]['data_extracted'] = data_extracted
        self.appData[currentPdf]['images'] = images
        self.appData[currentPdf]['image_id'] = image_id



        # # update ui
        self.process_navigator._update(process)
        self.test_indexor._update(test_info, self.option_selection)
        self.pdf_viewer._update(images=images, image_id=image_id)

        self.mainwindow.filemenu2.entryconfigure(1, state="normal")
        pass


    def _analyze(self):
        # 대분류

        currentPdf = self.uploader.currentPdf.get()

        if not currentPdf:
            tkinter.messagebox.showerror('Error', message='보고서가 선택되지 않았습니다.')
            return

        # popup
        # self.startThread(self.popup_preprocess)
        self.popup_preprocess()

        self.configure(cursor='watch')
        self.preprocess_popup.configure(cursor='watch')

        
        try:
            self.divider = Divider(currentPdf, controller_main_path=self.main_path)
        except: # 파일을 열 수 없을 때
            self.preprocess_popup.destroy()
            tkinter.messagebox.showerror('Error', message='Broken file: 파일을 열 수 없습니다.')
            self.configure(cursor='')
            return

        # 전처리 (이미지 변환, 텍스트 변환)
        self.divider.preprocess_process.trace_add('write', 
                                lambda e, n, preprocess: 
                                self.preprocess_bar._update(preprocess=self.divider.preprocess_process.get()))
        
        self.preprocess_threading = threading.Thread(target=self.divider.preprocess)
        self.preprocess_threading.daemon = True
        self.preprocess_threading.start()
        self.after(20, self.check_preprocess)


    def analyze(self):
        self.startThread(self._analyze())

    
    def get_imageId(self, ui_imageId):
        currentPdf = self.uploader.currentPdf.get()

        self.appData[currentPdf]['image_id'] = ui_imageId

        # print(self.appData[currentPdf]['image_id'])


    def get_testPages(self):
        '''
        - test_indexor를 통해 ui에 입력된 시험-페이지 정보 얻기 (page_info)
        - appData test_info (ui-formatted 대분류 결과) 업데이트

        page_info: {'시추주상도': [1, 2, 3]}'''
        
        currentPdf = self.uploader.currentPdf.get()
        test_info = self.appData[currentPdf]['test_info'] # ui-formatted 대분류 결과

        target_testList = self.test_indexor._to_extract
        page_info = dict(zip(target_testList, [[] for i in range(len(target_testList))])) # 추출할 시험만 추려서 정리

        for test in test_info.keys():
            
            page_str = str(self.test_indexor.test_table.item(test)['values'][1])

            pages_id = page_str2list(page_str)

            self.appData[currentPdf]['test_info'][test]['pages'] = pages_id # appData update

            if test in target_testList:
                page_info[test] = pages_id

        return page_info # {'시추주상도': [1, 2, 3]}
    

    def get_dataExtracted(self):
        '''
        - test_indexor를 통해 ui에 입력된 (최종 수정된) 데이터 얻기
        - appData data_extracted 업데이트'''

        currentPdf = self.uploader.currentPdf.get()
        data_dict = dict(zip(self.data_editor.tabDict.keys(), [[] for n in range(len(self.data_editor.tabDict))]))

        for tab, dataSheet in self.data_editor.tabDict.items():
            data = dataSheet.sheet.get_sheet_data()
            data = data[1:]

            data_dict[tab] = data

        self.appData[currentPdf]['data_extracted']= data_dict

        return data_dict


    def popup_extract(self):
        self.popup = tkinter.Toplevel(master=self)
        self.popup.title('Extraction status')
        self.popup.geometry("400x750")
        self.popup.grid_columnconfigure(0, weight=1)
        self.popup.grid_rowconfigure(0, weight=1)

        window_width = self.winfo_width()
        window_height = self.winfo_height()

        self.popup.geometry("+%d+%d" %(int(self.winfo_x()+window_width/2-150),int(self.winfo_y()+window_height/2-350)))

        self.extract_bar = ExtractBar(master=self.popup, controller=self, fg_color="white")
        self.extract_bar.grid(row=0, column=0, sticky="nsew")

        self.extract_bar.update()
        self.extract_bar.update_idletasks()
        self.popup.update()
        self.popup.update_idletasks()

        self.update()
        self.update_idletasks()

        


    def extract(self):
        currentPdf = self.uploader.currentPdf.get()

        # popup
        self.popup_extract()

        
        images = self.appData[currentPdf]['images']
        pages_tlines = self.appData[currentPdf]['text']

        self.images = images

        page_info = self.get_testPages()



        self.main_extractor = MainExtractor(currentPdf, page_info, images, pages_tlines)

        try:
            self.main_extractor.drill_log.process.trace_add('write', 
                                                        lambda e, test, process: 
                                                        self.extract_bar._update(test='시추주상도', process=self.main_extractor.drill_log.process.get(),
                                                                                 success=self.main_extractor.drill_log.success))
        except: pass


        self.startThread(self.main_extractor.extract)


    def join_data(self):

        self.popup.destroy()

        currentPdf = self.uploader.currentPdf.get()

        raw_text = self.appData[currentPdf]['raw_text'] # {}
        data_extracted = self.appData[currentPdf]['data_extracted'] # {'': []...}


        for worker in self.main_extractor.workers:
            # data_extracted: 뽑힌 tab만 존재

            if worker is None: continue


            raw_text[worker.name] = worker.raw_text
            raw_text[worker.name].insert(0, worker.pages)

            if isinstance(worker.tab, list): # 시추주상도
                  tab_list = worker.tab
                  
                  for tab in tab_list:
                        data_extracted[tab] = worker.data[tab]

            else:
                  data_extracted[worker.tab] = worker.data
                    
        # # self.popup.destroy()



        # # set app workspace
        self.appData[currentPdf]['process'] = 0.6
        self.appData[currentPdf]['raw_text'] = raw_text
        self.appData[currentPdf]['data_extracted'] = data_extracted
        self.appData[currentPdf]['extractor'] = self.main_extractor.workers


        # # # update ui
        # print(self.data_extracted)
        self.process_navigator._update(0.6)
        self.data_editor._update(data_extracted, self.main_extractor.workers)



    def save_edit(self):
        ''' 
        주요 기능 없음
        프로세스바만 업데이트 '''       

        for tab_name, tab in self.data_editor.tabDict.items():
            tab_id = self.data_editor.tabs.index(tab_name)

            if self.data_editor.tabsheet.tab(tab_id=tab_id)['state'] == 'normal':
                self.data_editor.tabsheet.tab(tab_id, state='normal', image='')


        currentPdf = self.uploader.currentPdf.get()
        self.appData[currentPdf]['process'] = 0.8

        # # # update ui
        self.process_navigator._update(0.8)






    def export(self):
        currentPdf = self.uploader.currentPdf.get()
        if self.appData[currentPdf]['process'] < 0.6:
            return
        elif self.appData[currentPdf]['process'] == 0.6:
            answer = tkinter.messagebox.askokcancel("Confirmation", message="추출 데이터 변경 사항을 저장하시겠습니까?")
            if not answer:
                return

        # 저장 위치 지정
        dst_path = tkinter.filedialog.asksaveasfilename(filetypes=[('excel file', '.xlsx')], title='Export data as', defaultextension=".xlsx")
        if not dst_path:
            return

        data_extracted = self.get_dataExtracted()

        # 엑셀 쓰기 및 저장
        self.configure(cursor='watch')
        write_on_xlsx(data=data_extracted, template=self.asset_manager.result_template, dst_path=dst_path)
        if self.option_savelog.get():
            save_logtxt(data=self.appData[currentPdf]['raw_text'], dst_path=dst_path)



        # set app workspace
        self.appData[currentPdf]['data_extracted'] = data_extracted
        self.appData[currentPdf]['process'] = 1.0
        
        
        # # # update ui
        self.process_navigator._update(1.0)
        self.configure(cursor='')



if __name__ == '__main__':
    

    app = App()

    
    app.mainloop()

