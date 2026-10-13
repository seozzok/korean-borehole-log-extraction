
import os, sys

import tkinter
from tkinter import filedialog
import tkinter.ttk
import tkinter.messagebox
import tkinter.font

import customtkinter

from PIL import ImageTk, Image

customtkinter.set_appearance_mode("Dark")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("dark-blue")  # Themes: "blue" (standard), "green", "dark-blue"

green_icon = './image/greenlight.png'
red_icon = './image/redlight.png'
gray_icon = './image/graylight.png'

def _resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


green_icon = _resource_path('./image/greenlight.png')
red_icon = _resource_path('./image/redlight.png')
gray_icon = _resource_path('./image/graylight.png')



class ProcessNavigator(customtkinter.CTkFrame):
    def __init__(self, master, controller, *args, **kwargs):


        super().__init__(master, **kwargs)

        # widgets
        self.frame = master
        self.controller = controller
        self.image_manager = controller.asset_manager

        self.green_light = self.image_manager.greenlight
        self.gray_light = self.image_manager.graylight
        self.red_light = self.image_manager.redlight

        

        self.window = self
        self.window.grid_columnconfigure((0,1,2,3,4,5,6,7,8,9), weight=3, uniform='a')
        self.window.grid_rowconfigure((0,1), weight=3, uniform='b')


        self.uploadBtn = customtkinter.CTkButton(master=self.window, fg_color="transparent", border_width=0, text_color=('black'),
                                                 text='Upload', font=customtkinter.CTkFont(size=15), command=self.controller.upload, 
                                                 hover_color='white')
        self.divideBtn = customtkinter.CTkButton(master=self.window, fg_color="transparent", border_width=0, text_color=('gray60'),
                                                 text='Analyze',font=customtkinter.CTkFont(size=15),
                                                 hover=False) #  command=self.controller.analyze,
        self.extractBtn = customtkinter.CTkButton(master=self.window, fg_color="transparent", border_width=0, text_color=('gray60'),
                                                 text='Extract', font=customtkinter.CTkFont(size=15),
                                                 hover=False) #  command=self.controller.extract,
        self.editBtn = customtkinter.CTkButton(master=self.window, fg_color="transparent", border_width=0, text_color=('gray60'),
                                                 text='Edit', font=customtkinter.CTkFont(size=15),
                                                 hover=False) #  command=self.controller.save_edit, 
        self.exportBtn = customtkinter.CTkButton(master=self.window, fg_color="transparent", border_width=0, text_color=('gray60'),
                                                 text='Export', font=customtkinter.CTkFont(size=15),
                                                 hover=False) #  command=self.controller.export,
        

        self.uploadBtn.grid(row=0, column=0, sticky="s", columnspan=2)
        self.divideBtn.grid(row=0, column=2, sticky="s", columnspan=2)
        self.extractBtn.grid(row=0, column=4, sticky="s", columnspan=2)
        self.editBtn.grid(row=0, column=6, sticky="s", columnspan=2)
        self.exportBtn.grid(row=0, column=8, sticky="s", columnspan=2)
        

        __frame = customtkinter.CTkFrame(master=self.window, height=28, fg_color='transparent') # fg_color='transparent'
        __frame.grid(row=1, column=0, sticky="n")
        __frame.grid_propagate(0)
        __frame = customtkinter.CTkFrame(master=self.window, height=28, fg_color='transparent') # fg_color='transparent'
        __frame.grid(row=1, column=9, sticky="n")
        __frame.grid_propagate(0)


        progress1Frame = customtkinter.CTkFrame(master=self.window, height=28, fg_color='transparent') # fg_color='transparent'
        progress1Frame.grid_columnconfigure((0), weight=1, uniform='c')
        progress1Frame.grid_rowconfigure((0,1,2), weight=1, uniform='d')
        progress1Frame.grid(row=1, column=1, sticky="n", columnspan=2)
        progress1Frame.grid_propagate(0)
        customtkinter.CTkFrame(master=progress1Frame, fg_color='transparent').grid(row=0, column=0)
        self.process1 = customtkinter.CTkFrame(master=progress1Frame, fg_color='gray83') # gray70
        self.process1.grid(row=1, column=0) # , sticky='nswe'
        customtkinter.CTkFrame(master=progress1Frame, fg_color='transparent').grid(row=2, column=0)

        progress2Frame = customtkinter.CTkFrame(master=self.window, height=28, fg_color='transparent') # fg_color='transparent'
        progress2Frame.grid_columnconfigure((0), weight=1, uniform='c')
        progress2Frame.grid_rowconfigure((0,1,2), weight=1, uniform='d')
        progress2Frame.grid(row=1, column=3, sticky="n", columnspan=2)
        progress2Frame.grid_propagate(0)
        customtkinter.CTkFrame(master=progress2Frame, fg_color='transparent').grid(row=0, column=0)
        self.process2 = customtkinter.CTkFrame(master=progress2Frame, fg_color='gray83') # gray70
        self.process2.grid(row=1, column=0) # , sticky='nswe'
        customtkinter.CTkFrame(master=progress2Frame, fg_color='transparent').grid(row=2, column=0)

        progress3Frame = customtkinter.CTkFrame(master=self.window, height=28, fg_color='transparent') # fg_color='transparent'
        progress3Frame.grid_columnconfigure((0), weight=1, uniform='c')
        progress3Frame.grid_rowconfigure((0,1,2), weight=1, uniform='d')
        progress3Frame.grid(row=1, column=5, sticky="n", columnspan=2)
        progress3Frame.grid_propagate(0)
        customtkinter.CTkFrame(master=progress3Frame, fg_color='transparent').grid(row=0, column=0)
        self.process3 = customtkinter.CTkFrame(master=progress3Frame, fg_color='gray83') # gray70
        self.process3.grid(row=1, column=0) # , sticky='nswe'
        customtkinter.CTkFrame(master=progress3Frame, fg_color='transparent').grid(row=2, column=0)

        progress4Frame = customtkinter.CTkFrame(master=self.window, height=28, fg_color='transparent') # fg_color='transparent'
        progress4Frame.grid_columnconfigure((0), weight=1, uniform='c')
        progress4Frame.grid_rowconfigure((0,1,2), weight=1, uniform='d')
        progress4Frame.grid(row=1, column=7, sticky="n", columnspan=2)
        progress4Frame.grid_propagate(0)
        customtkinter.CTkFrame(master=progress4Frame, fg_color='transparent').grid(row=0, column=0)
        self.process4 = customtkinter.CTkFrame(master=progress4Frame, fg_color='gray83') # gray70
        self.process4.grid(row=1, column=0) # , sticky='nswe'
        customtkinter.CTkFrame(master=progress4Frame, fg_color='transparent').grid(row=2, column=0)



        self.upload_light = customtkinter.CTkLabel(master=self.window, fg_color="transparent", text_color=("gray10", "#DCE4EE"),
                                                 text='',font=customtkinter.CTkFont(size=15),
                                                 image = self.gray_light)
        self.divide_light = customtkinter.CTkLabel(master=self.window, fg_color="transparent", text_color=("gray10", "#DCE4EE"),
                                                 text='',font=customtkinter.CTkFont(size=15),
                                                 image = self.gray_light)
        self.extract_light = customtkinter.CTkLabel(master=self.window, fg_color="transparent", text_color=("gray10", "#DCE4EE"),
                                                 text='',font=customtkinter.CTkFont(size=15),
                                                 image = self.gray_light)
        self.edit_light = customtkinter.CTkLabel(master=self.window, fg_color="transparent", text_color=("gray10", "#DCE4EE"),
                                                 text='',font=customtkinter.CTkFont(size=15),
                                                 image = self.gray_light)
        self.export_light = customtkinter.CTkLabel(master=self.window, fg_color="transparent", text_color=("gray10", "#DCE4EE"),
                                                 text='',font=customtkinter.CTkFont(size=15),
                                                 image = self.gray_light)


        

        self.upload_light.grid(row=1, column=0, sticky="n", columnspan=2)
        self.divide_light.grid(row=1, column=2, sticky="n", columnspan=2)
        self.extract_light.grid(row=1, column=4, sticky="n", columnspan=2)
        self.edit_light.grid(row=1, column=6, sticky="n", columnspan=2)
        self.export_light.grid(row=1, column=8, sticky="n", columnspan=2)


        self.upload_light.lift()
        self.divide_light.lift()
        self.extract_light.lift()
        self.edit_light.lift()
        self.export_light.lift()




    def _update(self, process):

        if process == 0:
            self.uploadBtn.configure(text_color=("black"), command=self.controller.upload, hover=True, hover_color='white')
            self.divideBtn.configure(text_color=("gray60"), command=None, hover=False)
            self.extractBtn.configure(text_color=('gray60'), command=None, hover=False)
            self.editBtn.configure(text_color=('gray60'), command=None, hover=False)
            self.exportBtn.configure(text_color=('gray60'), command=None, hover=False)

            self.upload_light.configure(image = self.gray_light)
            self.divide_light.configure(image = self.gray_light)
            self.extract_light.configure(image = self.gray_light)
            self.edit_light.configure(image = self.gray_light)
            self.export_light.configure(image = self.gray_light)

            self.process1.configure(fg_color='gray70')
            self.process2.configure(fg_color='gray83')
            self.process3.configure(fg_color='gray83')
            self.process4.configure(fg_color='gray83')


        elif process == 0.2:
            self.uploadBtn.configure(text_color=("forest green"), command=None, hover=False)
            self.divideBtn.configure(text_color=("black"), command=self.controller.analyze, hover=True, hover_color='white')
            self.extractBtn.configure(text_color=('gray60'), command=None, hover=False)
            self.editBtn.configure(text_color=('gray60'), command=None, hover=False)
            self.exportBtn.configure(text_color=('gray60'), command=None, hover=False)

            self.upload_light.configure(image = self.green_light)
            self.divide_light.configure(image = self.gray_light)
            self.extract_light.configure(image = self.gray_light)
            self.edit_light.configure(image = self.gray_light)
            self.export_light.configure(image = self.gray_light)

            self.process1.configure(fg_color='gray70')
            self.process2.configure(fg_color='gray83')
            self.process3.configure(fg_color='gray83')
            self.process4.configure(fg_color='gray83')

        elif process == 0.4:
            self.uploadBtn.configure(text_color=("forest green"), command=None, hover=False)
            self.divideBtn.configure(text_color=("forest green"), command=None, hover=False)
            self.extractBtn.configure(text_color=("black"), command=self.controller.extract, hover=True, hover_color='white')
            self.editBtn.configure(text_color=('gray60'), command=None, hover=False)
            self.exportBtn.configure(text_color=('gray60'), command=None, hover=False)

            self.upload_light.configure(image = self.green_light)
            self.divide_light.configure(image = self.green_light)
            self.extract_light.configure(image = self.gray_light)
            self.edit_light.configure(image = self.gray_light)
            self.export_light.configure(image = self.gray_light)

            self.process1.configure(fg_color='springgreen3')
            self.process2.configure(fg_color='gray70')
            self.process3.configure(fg_color='gray83')
            self.process4.configure(fg_color='gray83')

        elif process == 0.6:
            self.uploadBtn.configure(text_color=("forest green"), command=None, hover=False)
            self.divideBtn.configure(text_color=("forest green"), command=None, hover=False)
            self.extractBtn.configure(text_color=("forest green"), command=self.controller.extract, hover=True, hover_color='white')
            self.editBtn.configure(text_color=("black"), command=self.controller.save_edit, hover=True, hover_color='white')
            self.exportBtn.configure(text_color=('gray60'), command=self.controller.export, hover=True, hover_color='white')

            self.upload_light.configure(image = self.green_light)
            self.divide_light.configure(image = self.green_light)
            self.extract_light.configure(image = self.green_light)
            self.edit_light.configure(image = self.gray_light)
            self.export_light.configure(image = self.gray_light)

            self.process1.configure(fg_color='springgreen3')
            self.process2.configure(fg_color='springgreen3')
            self.process3.configure(fg_color='gray70')
            self.process4.configure(fg_color='gray70')

        elif process == 0.8:
            self.uploadBtn.configure(text_color=("forest green"), command=None, hover=False)
            self.divideBtn.configure(text_color=("forest green"), command=None, hover=False)
            self.extractBtn.configure(text_color=("forest green"), command=None, hover=False)
            self.editBtn.configure(text_color=("forest green"), command=None, hover=False)
            self.exportBtn.configure(text_color=("black"), command=self.controller.export, hover=True, hover_color='white')

            self.upload_light.configure(image = self.green_light)
            self.divide_light.configure(image = self.green_light)
            self.extract_light.configure(image = self.green_light)
            self.edit_light.configure(image = self.green_light)
            self.export_light.configure(image = self.gray_light)

            self.process1.configure(fg_color='springgreen3')
            self.process2.configure(fg_color='springgreen3')
            self.process3.configure(fg_color='springgreen3')
            self.process4.configure(fg_color='gray70')
            

        elif process == 1.0:
            self.uploadBtn.configure(text_color=("forest green"), command=None, hover=False)
            self.divideBtn.configure(text_color=("forest green"), command=None, hover=False)
            self.extractBtn.configure(text_color=("forest green"), command=None, hover=False)
            self.editBtn.configure(text_color=("forest green"), command=None, hover=False)
            self.exportBtn.configure(text_color=("forest green"), command=self.controller.export, hover=False)

            self.upload_light.configure(image = self.green_light)
            self.divide_light.configure(image = self.green_light)
            self.extract_light.configure(image = self.green_light)
            self.edit_light.configure(image = self.green_light)
            self.export_light.configure(image = self.green_light)

            self.process1.configure(fg_color='springgreen3')
            self.process2.configure(fg_color='springgreen3')
            self.process3.configure(fg_color='springgreen3')
            self.process4.configure(fg_color='springgreen3')
