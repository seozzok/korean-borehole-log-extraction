

import os, sys
import time

import tkinter
from tkinter import filedialog
import tkinter.ttk
import tkinter.messagebox
import tkinter.font as font

import customtkinter


from ui.uploader import Uploader
from ui.process_navigator import ProcessNavigator
from ui.test_indexor import TestIndexor
from ui.data_editor import DataEditor
from ui.pdf_viewer import PdfViewer


class MainWindow(customtkinter.CTkFrame):
    """ just place 
        - uploader
        - processbar
        - test_indexor
        - datasheet
        - viewer

        on main app window"""
    
    def __init__(self, master, *args, **kwargs):

        super().__init__(master, *args, **kwargs)

        customtkinter.set_appearance_mode("Light")
        customtkinter.set_default_color_theme("dark-blue")

        self.window = master
        self.controller = master

        self.image_manager = self.controller.asset_manager

        
        ## upload frame과 process frame을 나눔
        self.window.grid_columnconfigure(0, weight=3)
        self.window.grid_columnconfigure(1, weight=40)
        self.window.grid_rowconfigure(0, weight=2)
        self.window.grid_rowconfigure(1, weight=200)

        # menu bar
        self.memubarframe = customtkinter.CTkFrame(self.window, bg_color="white", fg_color='white')
        self.memubarframe.grid(row=0, column=0, columnspan=2,sticky="nsew", pady=0) #  rowspan=27, columnspan=2,
        self.memubarframe.grid_propagate(1)


        self.menubutton1 = tkinter.Menubutton(self.memubarframe, text='File', font=customtkinter.CTkFont("arial", size=16), background='white', width=7, height=1, pady=3, border=0) # customtkinter.CTkFont(size=15)
        self.menubutton1.pack(anchor='w', fill='y', side='left', padx=(3,0))
        self.menubutton1.pack_propagate(1)

        self.filemenu1 = tkinter.Menu(self.menubutton1, tearoff=0, border=10, borderwidth=10)
        self.filemenu1.add_command(label='Upload', font=customtkinter.CTkFont(size=15), command=self.controller.upload, image=self.image_manager.blank, compound='left')
        self.filemenu1.add_separator()
        self.filemenu1.add_command(label='Clear all', font=customtkinter.CTkFont(size=15), command=self.controller.clear_all, image=self.image_manager.blank, compound='left')
        self.menubutton1["menu"] = self.filemenu1

        
        self.menubutton2 = tkinter.Menubutton(self.memubarframe, text='Process', font=customtkinter.CTkFont("arial", size=16), background='white', width=8, height=1, pady=3, border=0) # customtkinter.CTkFont(size=15)
        self.menubutton2.pack(anchor='w', fill='y', side='left')
        self.menubutton2.pack_propagate(1)

        self.filemenu2 = tkinter.Menu(self.menubutton2, tearoff=0, border=10, borderwidth=10)
        self.filemenu2.add_command(label='Analyze', font=customtkinter.CTkFont(size=15), command=lambda: self.controller.analyze(), image=self.image_manager.blank, compound='left',
                              state='disabled')
        self.filemenu2.add_command(label='Extract', font=customtkinter.CTkFont(size=15), command=self.controller.upload, image=self.image_manager.blank, compound='left',
                              state='disabled')
        self.filemenu2.add_command(label='Export', font=customtkinter.CTkFont(size=15), command=self.controller.upload, image=self.image_manager.blank, compound='left',
                              state='disabled')
        # self.filemenu2.add_separator()
        # self.filemenu2.add_command(label='Quick export', font=customtkinter.CTkFont(size=15), command=self.controller.upload, image=self.image_manager.blank, compound='left',
        #                            state='disabled')
        self.menubutton2["menu"] = self.filemenu2


        self.menubutton3 = tkinter.Menubutton(self.memubarframe, text='Options', font=customtkinter.CTkFont("arial", size=16), background='white', width=8, height=1, pady=3, border=0) # customtkinter.CTkFont(size=15)
        self.menubutton3.pack(anchor='w', fill='y', side='left')
        self.menubutton3.pack_propagate(1)

        self.filemenu3 = tkinter.Menu(self.menubutton3, tearoff=0, border=10, borderwidth=10)

        self.nestedmenu = tkinter.Menu(self.filemenu3)
        
        self.filemenu3.add_command(label='Extraction Setting', font=customtkinter.CTkFont(size=15), image=self.image_manager.blank, compound='right', command='')
        
        self.filemenu3.add_cascade(label='   '+'Target tests', menu=self.nestedmenu, font=customtkinter.CTkFont("맑은고딕", size=15), image=self.image_manager.blank, compound='right')
        self.nestedmenu.add_checkbutton(label='   '+'시추주상도', font=customtkinter.CTkFont("맑은고딕", size=15), 
                                        variable=self.controller.option_selection['시추주상도'], image=self.image_manager.blank, compound='right')
        self.nestedmenu.add_checkbutton(label='   '+'공내재하시험', font=customtkinter.CTkFont("맑은고딕", size=15), 
                                        variable=self.controller.option_selection['공내재하시험'], image=self.image_manager.blank, compound='right')
        self.nestedmenu.add_checkbutton(label='   '+'공내전단시험', font=customtkinter.CTkFont("맑은고딕", size=15),
                                        variable=self.controller.option_selection['공내전단시험'], image=self.image_manager.blank, compound='right')
        self.nestedmenu.add_checkbutton(label='   '+'하향식탄성파시험', font=customtkinter.CTkFont("맑은고딕", size=15),
                                        variable=self.controller.option_selection['하향식탄성파시험'], image=self.image_manager.blank, compound='right')
        self.nestedmenu.add_checkbutton(label='   '+'현장투수시험', font=customtkinter.CTkFont("맑은고딕", size=15),
                                        variable=self.controller.option_selection['현장투수시험'], image=self.image_manager.blank, compound='right')
        self.nestedmenu.add_checkbutton(label='   '+'실내토질시험', font=customtkinter.CTkFont("맑은고딕", size=15),
                                        variable=self.controller.option_selection['실내토질시험'], image=self.image_manager.blank, compound='right')
        self.nestedmenu.add_checkbutton(label='   '+'암석일축압축강도시험', font=customtkinter.CTkFont("맑은고딕", size=15),
                                        variable=self.controller.option_selection['암석일축압축강도시험'], image=self.image_manager.blank, compound='right')
        self.nestedmenu.add_checkbutton(label='   '+'토질일축압축강도시험', font=customtkinter.CTkFont("맑은고딕", size=15),
                                        variable=self.controller.option_selection['토질일축압축시험'], image=self.image_manager.blank, compound='right')
        self.nestedmenu.activate(0)

        self.filemenu3.add_separator()
        var2 = self.controller.option_savelog
        self.filemenu3.add_command(label='Save Option', font=customtkinter.CTkFont(size=15), image=self.image_manager.blank, compound='right', command='')
        self.filemenu3.add_checkbutton(label='   '+'Export with log file (*.txt)', font=customtkinter.CTkFont("맑은고딕",size=15), variable=var2, 
                                       image=self.image_manager.blank, compound='right')
           
        self.menubutton3["menu"] = self.filemenu3


        self.menubutton4 = tkinter.Menubutton(self.memubarframe, text='Help', font=customtkinter.CTkFont("arial", size=16), background='white', width=8, height=1, pady=3, border=0) # customtkinter.CTkFont(size=15)
        self.menubutton4.pack(anchor='w', fill='y', side='left')
        self.menubutton4.pack_propagate(1)

        self.filemenu4 = tkinter.Menu(self.menubutton4, tearoff=0, border=10, borderwidth=10)
        self.filemenu4.add_command(label='About ...', font=customtkinter.CTkFont(size=15), command=self.controller.show_about, image=self.image_manager.blank, compound='right')
        self.menubutton4["menu"] = self.filemenu4


        # upload frame
        self.uploadframe = customtkinter.CTkFrame(self.window, corner_radius=0, bg_color="gray86", fg_color='gray86')
        self.uploadframe.grid(row=1, column=0, sticky="nsew") #  rowspan=27, columnspan=2,
        self.uploadframe.grid_propagate(False)

        # process frame
        self.processframe = customtkinter.CTkFrame(self.window, fg_color="transparent")
        self.processframe.grid_columnconfigure(0, weight=1, uniform='col')
        self.processframe.grid_columnconfigure(1, weight=1, uniform='col')
        self.processframe.grid_rowconfigure(0, weight=1, uniform='row')
        self.processframe.grid_rowconfigure(1, weight=3, uniform='row')
        self.processframe.grid_rowconfigure(2, weight=5, uniform='row')

        self.processframe.grid(row=1, column=1, sticky="nsew")
        self.processframe.grid_propagate(False)


        # uploader
        self.uploader = Uploader(master=self.uploadframe, controller=self.controller, fg_color="transparent")
        self.uploader.pack(fill='both', expand=True)
        self.uploader.pack_propagate(0)

        self.process_navigator = ProcessNavigator(master=self.processframe, controller=self.controller, corner_radius=0, fg_color="transparent")
        self.test_indexor = TestIndexor(master=self.processframe, controller=self.controller, corner_radius=0, fg_color="transparent",)
        self.data_editor =  DataEditor(master=self.processframe, controller=self.controller, corner_radius=0, fg_color="transparent", height=600)
        self.pdf_viewer = PdfViewer(master=self.processframe, controller=self.controller, corner_radius=0, fg_color="transparent")
        
        self.pdf_viewer.grid(row=0, column=1, rowspan=3, sticky="nsew")
        self.process_navigator.grid(row=0, column=0, sticky="nsew")#
        self.test_indexor.grid(row=1, column=0, sticky="nsew")
        self.data_editor.grid(row=2, column=0, sticky="nsew")


    def __on_click(self):
            pass