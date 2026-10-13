
import os, sys
import time

import tkinter
from tkinter import filedialog
import tkinter.ttk
import tkinter.messagebox
import tkinter.font as font

import customtkinter
from tksheet import Sheet

from PIL import ImageTk, Image

import configparser
import logging
import sys
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
import threading


class PopupWindow(tkinter.Toplevel):
    def __init__(self, parent, progressbar, *args, **kwargs):

        super().__init__()

        self.parent = parent
        x = self.parent.winfo_x()
        y = self.parent.winfo_y()

        self.geometry("+%d+%d" %(x+650,y+400))
        self.overrideredirect(True)

        progressbar(self, border_width=1).pack()



class PreprocessBar(customtkinter.CTkFrame):

    def __init__(self, master, controller, *args, **kwargs):

        super().__init__(master, **kwargs)
        self.controller = controller
        self.master = master

        self.pack_propagate(0)

        # widgets
        self.dot_num = 1
        self.title = customtkinter.CTkLabel(self, text='Preparing documentation ..{}'.format('.'*self.dot_num), 
                                            text_color='black', font=customtkinter.CTkFont(size=18, weight='bold'))
        self.title.pack(anchor='w', ipadx=5, padx=20, pady=(15, 0))
        
        self.text = customtkinter.CTkLabel(self, text='Converting to images ..', 
                                           text_color='black', height=10, font=customtkinter.CTkFont(size=15), fg_color='transparent')
        self.text.pack(anchor='sw', ipadx=5, padx=25, pady=(10, 0), ipady=0)

        self.koreantext = customtkinter.CTkLabel(self, text='몇 분 정도 소요될 수 있습니다.', 
                                                 text_color='black', font=customtkinter.CTkFont('맑은 고딕', size=12), fg_color='transparent')
        self.koreantext.pack(anchor='nw', ipadx=5, padx=25, pady=(0, 0), ipady=0)



    def _update(self, *arg, preprocess):
        if (preprocess == 0.5):
            
            self.text.configure(text='Text preprocessing ..')
            self.text.update()
            self.text.update_idletasks()

            self.master.update()
            self.master.update_idletasks()
            
            return
        
        elif (preprocess == 1):

            self.title.configure(text='Preprocessing Completed')
            self.title.update()
            self.title.update_idletasks()

            # self.text.configure(text='')
            # self.koreantext.configure(text='')
            # self.text.update()
            # self.text.update_idletasks()
            # self.koreantext.update()
            # self.koreantext.update_idletasks()

            time.sleep(1.5)
            self.master.destroy()

            
        else:
            preprocess_percent = int(preprocess*100)

            # if (preprocess_percent // 10) % 2 == 0:
            #     self.dot_num = 1
            # else:
            #     self.dot_num = 2

            # self.title.configure(text='Preparing documentation ..{}'.format('.'*self.dot_num))

            self.master.update()
            self.master.update_idletasks()

            
            

        

class DivideBar(customtkinter.CTkFrame):

    def __init__(self, master, controller, *args, **kwargs):

        super().__init__(master, **kwargs)
        self.controller = controller
        self.master = master
        
        self.whole_page = len(self.controller.divider.images)

        # widgets
        self.title = customtkinter.CTkLabel(self, text='Classifying into geo-tests ...', font=customtkinter.CTkFont(size=15, weight='bold'))
        self.title.pack(anchor='w', ipadx=5, padx=20, pady=(15, 0))

        self.dprocess_bar = customtkinter.CTkProgressBar(self, height=15, corner_radius=0)
        self.dprocess_bar.pack(anchor='center', ipadx=5, padx=20, pady=(2, 0), fill='x')
        self.dprocess_bar.set(0)


        self.cur_page = customtkinter.CTkLabel(self, text='In progress  |  ', font=customtkinter.CTkFont(size=13))
        self.cur_page.pack(side='left', ipadx=5, padx=20, pady=(2, 20))

        self.page_label = customtkinter.CTkLabel(self, text=str(self.whole_page)+'  pages', font=customtkinter.CTkFont(size=13))
        # self.whole_page = customtkinter.CTkLabel(self, text=' /      ' + str(10)+'  pages', font=customtkinter.CTkFont(size=13))
        self.page_label.pack(side='right', ipadx=5, padx=20, pady=(2, 20))

        # customtkinter.CTkFrame(self, fg_color='transparent', height=20).pack(side='bottom')


        # tkinter.Button(self, text='test', command=self.test).pack()

        # self.controller.preprocess.trace_add('write', self.update_t) # set


    def _update(self, *args, divide_process):
        if divide_process.get() / self.whole_page == 1:
            self.dprocess_bar.set(divide_process.get() / self.whole_page)
            self.cur_page.configure(text='In progress  |  ' + str(divide_process.get()))
            self.update_idletasks()

            time.sleep(1)

            self.master.destroy()
        
        else:
            self.dprocess_bar.set(divide_process.get() / self.whole_page)

            # self.dprocess_bar.set(self.controller.dprocess.get()/10)
            self.cur_page.configure(text='In progress  |  ' + str(divide_process.get()))
            self.update_idletasks()

        # if self.controller.dprocess.get() == 1:
        #     self.text.configure(text='Text preprocessing ..')
        #     self.update_idletasks()

        # elif self.controller.dprocess.get() == 0:
        #     self.master.withdraw()



        

class ExtractBar(customtkinter.CTkFrame):

    def __init__(self, master, controller, *args, **kwargs):

        super().__init__(master, **kwargs)
        self.controller = controller
        self.master = master

        self.window = self
        self.window.grid_rowconfigure((0), weight=2, uniform='a')
        self.window.grid_rowconfigure((1,2,3,4,5,6,7,8,9), weight=3, uniform='a')
        self.window.grid_columnconfigure(0, weight=1)
        # self.window.grid_propagate(0)


        # widgets
        self.title = customtkinter.CTkLabel(self, text='Extracting ...', font=customtkinter.CTkFont(size=15, weight='bold'), anchor='sw')
        self.title.grid(row=0, column=0, padx=20, sticky="nsew")

        ## 시추주상도
        self.drill_log_frame = customtkinter.CTkFrame(self.window, fg_color="transparent")
        self.drill_log_frame.grid(row=1, column=0, sticky="nsew", pady=10)
        self.drill_log_bar = customtkinter.CTkProgressBar(self.drill_log_frame, height=12, fg_color='gray85', progress_color='gray85') # fg_color='gray75', progress_color='royal blue2'
        self.drill_log_bar.pack(side='bottom', anchor='center', ipadx=5, padx=20, pady=(0, 0), fill='x')
        
        self.drill_log_text = customtkinter.CTkLabel(self.drill_log_frame, text='시추주상도', font=customtkinter.CTkFont('맑은고딕', size=17), anchor='sw', text_color='gray70')
        self.drill_log_text.pack(side='left', anchor='w', ipadx=1, padx=20, pady=(2, 0), fill='x', expand=True)
        
        self.drill_log_progress = customtkinter.CTkLabel(self.drill_log_frame, text='', font=customtkinter.CTkFont(size=15), anchor='se')
        self.drill_log_progress.pack(side='right', anchor='e', ipadx=1, padx=20, pady=(2, 0), fill='x', expand=True)
        
        # self.drill_log_bar.set(0)


        self.ok_btn = customtkinter.CTkButton(self.window, text='OK', command=self.controller.join_data, fg_color='white', text_color='gray70', border_color='gray85', border_width=1)
        self.ok_btn.grid(row=9, column=0, pady=20, sticky='s')


    def _update(self, *arg, test, process, success):
        ''' process: 0~1
        '''

        if test == '공내전단시험':
            test_title = self.borehole_shear_text
            process_bar = self.borehole_shear_bar
            process_text = self.borehole_shear_progress

        elif test == '하향식탄성파시험':
            test_title = self.downhole_text
            process_bar = self.downhole_bar
            process_text = self.downhole_progress


        elif test == '시추주상도':
            test_title = self.drill_log_text
            process_bar = self.drill_log_bar
            process_text = self.drill_log_progress


        elif test == '현장투수시험':
            test_title = self.field_permeability_text
            process_bar = self.field_permeability_bar
            process_text = self.field_permeability_progress


        elif test == '공내재하시험':
            test_title = self.pressuremeter_text
            process_bar = self.pressuremeter_bar
            process_text = self.pressuremeter_progress


        elif test == '암석일축압축강도시험':
            test_title = self.rock_ucs_text
            process_bar = self.rock_ucs_bar
            process_text = self.rock_ucs_progress


        elif test == '실내토질시험':
            test_title = self.soil_prop_text
            process_bar = self.soil_prop_bar
            process_text = self.soil_prop_progress


        elif test == '토질일축압축시험':
            test_title = self.soil_ucs_text
            process_bar = self.soil_ucs_bar
            process_text = self.soil_ucs_progress


        if process == 1:
            if all(success): # [1, 1, 1]
                process_bar.set(process)
                process_bar.configure(fg_color='gray75', progress_color='forest green')
                process_text.configure(text='')
            elif not any(success): # [0, 0, 0]
                # test_title.configure(text_color='DarkOrange2')

                process_bar.set(process)
                process_bar.configure(fg_color='gray75', progress_color='DarkOrange2')
                process_text.configure(text='')
            elif not all(success): # [1, 0, 0]
                # test_title.configure(text_color='DarkOrange3')

                process_bar.set(process)
                process_bar.configure(fg_color='gray75', progress_color='chartreuse3')
                # process_text.configure(text='일부 추출', font=customtkinter.CTkFont('맑은고딕', size=17), text_color='DarkOrange2')
                process_text.configure(text='')

            self.ok_btn.configure(text_color='black', border_color='black', border_width=1)

        else:
            test_title.configure(text_color='black')

            process_bar.configure(fg_color='gray75', progress_color='royal blue2')
            process_bar.set(process)

            # print(process)

            process_text.configure(text='{} %'.format(int(process*100)))
