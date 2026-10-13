
import os, sys

import tkinter
from tkinter import filedialog
import tkinter.ttk
import tkinter.messagebox
import tkinter.font

import tksheet
import customtkinter

from ui.scrollable_notebook import ScrollableNotebook

# from image_zoomer import *
# from upload import Upload


from PIL import ImageTk, Image


customtkinter.set_appearance_mode("Light")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")



headings = {'LOCA': ['시추공', 'Easting', 'Northing', '최종시추심도', '시추위치 지반표고', '최종굴착심도', '작업 일시'],
            'WSTD': ['시추공', '지하수위'],
            'CORE': ['시추공', '코어시료 상단심도', '코어시료 하단심도', 'TCR값', 'RQD값', '코어시료 지름'],
            'CDIA': ['시추공', '케이싱 심도', '케이싱 지름'],
            'GEOL': ['시추공', '지층분류', '지층상단심도', '지층하단심도', '지층종류', '지층순서', '비고'],
            'DISC': ['시추공', '상단심도', '하단심도', '주절리군 번호', '불연속면 번호', '불연속면 종류', '불연속면 경사', '불연속면 경사방향', '소규모/중규모 거칠기', '충전물질', 'Core Loss 유무', '파쇄 유무', '암맥 (또는 맥암) 유무', '단층 유무'],
            'WETH': ['시추공', '상단심도', '하단심도', '풍화등급'], 
            'FRAC': ['시추공', '상단심도', '하단심도', '주절리군 번호', '절리 최대간격', '절리 최소간격', '절리 평균간격', 'FI 값 (m당 불연속면수)', '절리간격 분류'],
            'ISPT': ['시추공', '시험 깊이', '타수', '관입깊이', 'N 값'],
            }



class DataSheet(customtkinter.CTkFrame):
    def __init__(self, master, controller, *args, **kwargs):
        # tk.Frame.__init__(self, parent, *args, **kwargs)

        super().__init__(master, **kwargs)

        # self.frame = tk.Frame(self)
        # Data 넣기

        self.sheet = tksheet.Sheet(self, width=500,
                           data = [["" for c in range(10)]+["" for c in range(26)] for r in range(5)] +\
                                    [["" for c in range(50)] for r in range(45)],
                            font=('맑은고딕', 12, "normal")) # width=700, height=775,
        
        self.sheet.enable_bindings()
        self.sheet.pack(fill='both', expand=True)



class DataEditor(customtkinter.CTkFrame):

    def __init__(self, master, controller, *args, **kwargs):

        super().__init__(master, *args,  **kwargs)

        self.frame = master
        self.controller = controller
        self.image_manager = controller.asset_manager


        self.controller = controller

        self.customed_style = tkinter.ttk.Style()
        self.customed_style.configure('Custom.TNotebook', background='white', font=('맑은고딕', 12)) # , padding=[12, 3]
        self.customed_style.configure('Custom.TNotebook.Tab', font=('Helvetica', 10), padding=[12, 3]) # padding=[12, 3], , background=[("selected", 'white')]
        

        self.download_icon = self.image_manager.download_icon
        self.nb_greenlight = self.image_manager.nb_greenlight
        self.nb_yellowlight = self.image_manager.nb_yellowlight

        self.tabs = []

        # widgets

        self.title = customtkinter.CTkLabel(self, text='Geo Data sheet', font=customtkinter.CTkFont(size=15, weight='bold'))
        self.title.pack(anchor='w', ipadx=5, padx=20, pady=(15, 0))

        self.sheet_frame = customtkinter.CTkFrame(self, bg_color='transparent', border_color='black', border_width=1.3)
        self.sheet_frame.pack(fill='both', expand=True, padx=(20, 20), pady=(0, 15)) # 
        self.sheet_frame.pack_propagate(0)

        self.tabsheet = ScrollableNotebook(self.sheet_frame, style='Custom.TNotebook') # , tabmenu=True
        self.tabsheet.pack(fill='both', expand=True, padx=(2,3), pady=2) # , padx=(20, 20)
        

        # tab들

        self.LOCA = customtkinter.CTkFrame(self.sheet_frame, bg_color='transparent')
        self.tabsheet.add(self.LOCA, text='LOCA')
        self.LOCA = DataSheet(master=self.LOCA, controller=self.controller) # frame
        self.LOCA.pack(fill='both', expand=True, ipadx=2, ipady=2) # , padx=(20, 20)
        self.tabs.append('LOCA')


        self.WSTD = customtkinter.CTkFrame(self.sheet_frame, bg_color='transparent')
        self.tabsheet.add(self.WSTD, text='WSTD')
        self.WSTD = DataSheet(master=self.WSTD, controller=self.controller) # frame
        self.WSTD.pack(fill='both', expand=True, ipadx=2, ipady=2) # , padx=(20, 20)
        self.tabs.append('WSTD')



        self.CORE = customtkinter.CTkFrame(self.sheet_frame, bg_color='transparent')
        self.tabsheet.add(self.CORE, text='CORE')
        self.CORE = DataSheet(master=self.CORE, controller=self.controller) # frame
        self.CORE.pack(fill='both', expand=True, ipadx=2, ipady=2) # , padx=(20, 20)
        self.tabs.append('CORE')


        self.CDIA = customtkinter.CTkFrame(self.sheet_frame, bg_color='transparent')
        self.tabsheet.add(self.CDIA, text='CDIA')
        self.CDIA = DataSheet(master=self.CDIA, controller=self.controller) # frame
        self.CDIA.pack(fill='both', expand=True, ipadx=2, ipady=2) # , padx=(20, 20)
        self.tabs.append('CDIA')


        self.GEOL = customtkinter.CTkFrame(self.sheet_frame, bg_color='transparent')
        self.tabsheet.add(self.GEOL, text='GEOL')
        self.GEOL = DataSheet(master=self.GEOL, controller=self.controller) # frame
        self.GEOL.pack(fill='both', expand=True, ipadx=2, ipady=2) # , padx=(20, 20)
        self.tabs.append('GEOL')


        self.DISC = customtkinter.CTkFrame(self.sheet_frame, bg_color='transparent')
        self.tabsheet.add(self.DISC, text='DISC')
        self.DISC = DataSheet(master=self.DISC, controller=self.controller) # frame
        self.DISC.pack(fill='both', expand=True, ipadx=2, ipady=2) # , padx=(20, 20)
        self.tabs.append('DISC')


        self.WETH = customtkinter.CTkFrame(self.sheet_frame, bg_color='transparent')
        self.tabsheet.add(self.WETH, text='WETH')
        self.WETH = DataSheet(master=self.WETH, controller=self.controller) # frame
        self.WETH.pack(fill='both', expand=True, ipadx=2, ipady=2) # , padx=(20, 20)
        self.tabs.append('WETH')


        self.FRAC = customtkinter.CTkFrame(self.sheet_frame, bg_color='transparent')
        self.tabsheet.add(self.FRAC, text='FRAC')
        self.FRAC = DataSheet(master=self.FRAC, controller=self.controller) # frame
        self.FRAC.pack(fill='both', expand=True, ipadx=2, ipady=2) # , padx=(20, 20)
        self.tabs.append('FRAC')

        
        self.ISPT = customtkinter.CTkFrame(self.sheet_frame, bg_color='transparent')
        self.tabsheet.add(self.ISPT, text='ISPT')
        self.ISPT = DataSheet(master=self.ISPT, controller=self.controller) # frame
        self.ISPT.pack(fill='both', expand=True, ipadx=2, ipady=2) # , padx=(20, 20)
        self.tabs.append('ISPT')

        # tab dict
        self.tabDict = {'LOCA': self.LOCA, 'WSTD': self.WSTD, 
                        'CORE': self.CORE, 'GEOL': self.GEOL,
                        'DISC': self.DISC, 'WETH': self.WETH, 'FRAC': self.FRAC,
                        'ISPT': self.ISPT, 'CDIA': self.CDIA} #  'SAMP': self.SAMP, 
        
        self.save_btn = customtkinter.CTkButton(self, text='Finish Editing', fg_color="transparent", border_width=1, text_color=("gray10", "#DCE4EE"),
                                                height=30, font=customtkinter.CTkFont(size=14),
                                                hover_color='steel blue',
                                                command=self.controller.save_edit)
        self.extract_btn = customtkinter.CTkButton(self, text=' EXPORT   ', image=self.download_icon, font=customtkinter.CTkFont('Arial', size=14),
                                                   fg_color="dark green", border_width=2, hover_color='RoyalBlue4',
                                                   height=30,
                                                   command=self.controller.export) # 
        


        self.extract_btn.pack(anchor='e', side='right', padx=10, pady=(0, 30))
        self.save_btn.pack(anchor='e', side='right', padx=5, pady=(0, 30))

        self.extract_btn.pack_propagate(0)
        self.save_btn.pack_propagate(0)



    def _update(self, datas, workers=None):
        for tab, dataSheet in self.tabDict.items():
            dataSheet.sheet.set_sheet_data([["" for c in range(10)]+["" for c in range(26)] for r in range(5)] +\
                                    [["" for c in range(500)] for r in range(500)])

        if (not datas) or (not workers):
            for tab_id in range(len(self.tabs)):
                self.tabsheet.tab(tab_id, state='normal', image='')
            return
      
        # datas: 뽑힌 tab만 존재
        worked_tab = {}
        tab_succuess = {}
        tab_activated = self.tabs[:]
        for worker_id, worker in enumerate(workers):
            if worker is None:
                # 세부시험이 포함되어 있지 않거나,
                # 추출을 수행하지 않을 때

                # worker - tab 매칭
                if worker_id == 0: # 시추주상도
                    tabs = ['LOCA', 'WSTD', 'CORE', 'CDIA', 'GEOL', 'DISC', 'WETH', 'FRAC', 'ISPT']


                # tab 비활성화
                for tab_name in tabs:
                    tab_id = self.tabs.index(tab_name)
                    self.tabsheet.tab(tab_id, state='disabled')

                    tab_activated.remove(tab_name)
                continue


            # 추출을 수행한 애
            success = worker.success # 페이지 별 저장

            if isinstance(worker.tab, list): # 시추주상도
                
                tab_list = worker.tab

                for tab in tab_list:
                    worked_tab[tab] = 1 # 일한 탭

                    # 성공 여부도 check
                    if all(success): # 모두 성공
                        tab_succuess[tab] = 1
                    else:
                        tab_succuess[tab] = 0

            else:
                tab = worker.tab
                worked_tab[tab] = 1
                if all(success): # 모두 성공
                    tab_succuess[tab] = 1
                else:
                    tab_succuess[tab] = 0


        for tab_name, tab in self.tabDict.items():
            tab_id = self.tabs.index(tab_name)

            # if not worked_tab.get(tab_name, ""):
            #     self.tabsheet.tab(tab_id, state='disabled')
            #     continue
            # else:
            #     self.tabsheet.tab(tab_id, state='normal')

            if tab_name in tab_activated:
                if tab_succuess[tab_name]:
                    
                    data = datas[tab_name][:]
                    if data:
                        self.tabsheet.tab(tab_id, state='normal') # , image=self.nb_greenlight, compound='left'
                        data.insert(0, headings[tab_name])
                    
                        self.write_on_tab(tab, data)
                    else:
                        self.tabsheet.tab(tab_id, state='disabled')

                else:
                    self.tabsheet.tab(tab_id, state='normal', image=self.nb_yellowlight, compound='left') # , image=self.nb_yellowlight, compound='left'
                    data = datas[tab_name][:]
                    data.insert(0, headings[tab_name])
                    
                    self.write_on_tab(tab, data)




    def save_func(self):
        file = self.controller.uploader.file_list.focus()
        self.controller.workList[file]['process'] = 0.8
        self.controller._processbar.update_bar(0.8)


    def write_on_tab(self, tab, datas=None):


        # for k, v in datas.items():
        #     v.insert(0, headings[k])
        #     tab = self._editor.tabDict[k]
        #     self._editor.write_on_tab(tab, v)


        tab.sheet.set_sheet_data(datas)
        tab.sheet.sheet_display_dimensions(len(datas)+100,50)
        tab.sheet.align_rows([0], align='center')
        # tab.sheet.set_all_row_heights(20)
        


    def get_tab_data(self):
        
        
        self.datas = dict(zip(self.tabDict.keys(), [[] for n in range(len(self.tabDict))]))
        for tab, dataSheet in self.tabDict.items():
            data = dataSheet.sheet.get_sheet_data()
            data = data[1:]

            self.datas[tab] = data

        return self.datas
