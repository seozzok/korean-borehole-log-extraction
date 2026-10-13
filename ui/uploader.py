
import os, sys

import tkinter
from tkinter import filedialog
import tkinter.ttk
import tkinter.messagebox
import tkinter.font

import customtkinter



dir_icon = './image/dir_icon.png'
doc_icon = './image/doc_icon.png'


class Uploader(customtkinter.CTkFrame):
    def __init__(self, master, controller, *args, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.frame = master
        self.controller = controller

        self.image_manager = controller.asset_manager

        self.dir_image = self.image_manager.dir_icon
        self.doc_image = self.image_manager.doc_icon
        self.delete_icon = self.image_manager.delete_icon
        
        

        self.style = tkinter.ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("Treeview", background="gray86", foreground="black", fieldbackground="gray86", \
                        relief = 'flat', bd=0, font=('맑은 고딕', 11), rowheight=27)
        self.style.layout('Treeview', [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])



        # widgets
        top_frame = customtkinter.CTkFrame(self, bg_color='gray86', height=15, fg_color='gray86')
        top_frame.pack(fill='x')
        self.title  = customtkinter.CTkLabel(top_frame, text='Explorer', font=customtkinter.CTkFont("arial", size=16, weight='bold'), fg_color='gray86')
        self.title.pack(anchor='w', ipadx=10, padx=5, ipady=15, side='left',)#side='left', expand=True

        self.detele = customtkinter.CTkButton(top_frame, text='', image=self.delete_icon, bg_color='transparent', fg_color='gray86', width=20,
                                              hover=False, command=self.controller.delete_pdf)
        self.detele.pack(anchor='e', side='right', padx=7, pady=(10, 0))

        self.pdf_list = tkinter.ttk.Treeview(self, show='tree', selectmode='none', style='Treeview')
        self.pdf_list.column("#0",  anchor='w') # width=400,
        self.pdf_list.heading("#0",text="")
        self.pdf_list.pack(fill='both', expand=True, side='bottom')

        # scollbar attached to the treeview
        # sb_horizontal = tkinter.Scrollbar(self, orient="horizontal", command=self.pdf_list.xview)
        # self.pdf_list.configure(xscrollcommand = sb_horizontal.set)
        # sb_horizontal.pack(anchor='s', fill='x', expand=True, side='bottom')




        self.pdf_list.bind('<ButtonRelease-1>', self._on_click)
        # self.bind('<ButtonRelease-1>', self._on_click)

        # data
        self.currentPdf = tkinter.StringVar()




    def get_pdflist(self):
        children = self.pdf_list.get_children()

        pdfs = []
        for child in children:
            pdfs += self.pdf_list.get_children(child)
        return pdfs

    

    # def upload_file(self):
    #     files = filedialog.askopenfilenames(title='Upload PDF files', \
    #         filetypes=[("PDF 파일", "*.pdf")], \
    #         initialdir='C:/', multiple=True)

    #     self._update_table(files_selected=files)

        # self.controller.set_workList()

        


    def _update(self, files_selected=None):

        if not files_selected:
            return
        
        # table update
        for i, file in enumerate(files_selected):
            folder = os.path.split(os.path.dirname(file))[-1]

            if folder in self.pdf_list.get_children():
                self.pdf_list.insert(folder, 'end', text=' '+ os.path.basename(file), iid=file, tags='selectable', image=self.doc_image)

            else:
                dir = self.pdf_list.insert('', 'end', text=' '+ folder, iid=folder, open=True, tags='folder', image=self.dir_image)
                self.pdf_list.insert(dir, 'end', text=' '+ os.path.basename(file), iid=file, tags='selectable', image=self.doc_image) # values=(os.path.basename(file), ''), iid=file
                


    def _on_click(self, event, var=0, index=0, mode=0):

        # tree = event.widget
        item_name = self.pdf_list.identify_row(event.y) # iid
        if item_name:
            tags = self.pdf_list.item(item_name, 'tags')
            
            if tags and (tags[0] == 'selectable'):
                self.pdf_list.selection_set(item_name)
                
                # 파일이 선택되었을 때
                # app data currentPdf 변화
                self.currentPdf.set(self.pdf_list.focus())


            if tags and (tags[0] == 'folder'):
                self.pdf_list.selection_remove(item_name)
