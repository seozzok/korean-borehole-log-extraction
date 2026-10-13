
import os
import tkinter
from PIL import Image

import customtkinter

class AssetManager:
    def __init__(self, main_path):

        ## image
        # main window
        self.blank = tkinter.PhotoImage(file=os.path.join(main_path, 'assets', 'blank.png'))

        self.blank2 = tkinter.PhotoImage(file=os.path.join(main_path, 'assets', 'blank2.png'))

        self.dir_icon = tkinter.PhotoImage(file=os.path.join(main_path, 'assets', 'dir_icon.png'))

        self.doc_icon = tkinter.PhotoImage(file=os.path.join(main_path, 'assets', 'doc_icon.png'))

        self.delete_icon = tkinter.PhotoImage(file=os.path.join(main_path, 'assets', 'delete.png'))

        self.greenlight = tkinter.PhotoImage(file=os.path.join(main_path, 'assets', 'greenlight.png'))

        self.graylight = tkinter.PhotoImage(file=os.path.join(main_path, 'assets', 'graylight.png'))

        self.redlight = tkinter.PhotoImage(file=os.path.join(main_path, 'assets', 'redlight.png'))


        self.selected_icon = tkinter.PhotoImage(file=os.path.join(main_path, 'assets', 'selected.png'))

        self.unselected_icon = tkinter.PhotoImage(file=os.path.join(main_path, 'assets', 'unselected.png'))

        self.inactive_icon = tkinter.PhotoImage(file=os.path.join(main_path, 'assets', 'inactive.png'))



        self.nb_greenlight = tkinter.PhotoImage(file=os.path.join(main_path, 'assets', 'nb_greenlight.png'))

        self.nb_yellowlight = tkinter.PhotoImage(file=os.path.join(main_path, 'assets', 'nb_yellowlight.png'))

        self.download_icon = tkinter.PhotoImage(file=os.path.join(main_path, 'assets', 'download.png'))


        self.arrowLeft_icon = tkinter.PhotoImage(file=os.path.join(main_path, 'assets', 'arrowLeft.png'))

        self.arrowRight_icon = tkinter.PhotoImage(file=os.path.join(main_path, 'assets', 'arrowRight.png'))


        ## excel
        self.result_template = os.path.join(main_path, 'assets', '__template.xlsx')




