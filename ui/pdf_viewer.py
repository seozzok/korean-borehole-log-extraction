
import os, sys
import time

import tkinter
from tkinter import filedialog
import tkinter.ttk
import tkinter.messagebox
import tkinter.font

import customtkinter

import threading


# from image_zoomer import ImageZoomer
# from upload import Upload

from ui.image_zoomer import ImageZoomer
# from zooming import ImageZoomer

from PIL import ImageTk, Image





class PdfViewer(customtkinter.CTkFrame):
    def __init__(self, master, controller, *args, **kwargs):
        # tk.Frame.__init__(self, parent, *args, **kwargs)


        super().__init__(master, *args, **kwargs)


        self.frame = master
        self.controller = controller
        self.image_manager = controller.asset_manager

        
        self.arrowLeft_icon = self.image_manager.arrowLeft_icon
        self.arrowRight_icon = self.image_manager.arrowRight_icon
        
    

        # widgets
        self.title = customtkinter.CTkLabel(self, text='Viewer', font=customtkinter.CTkFont(size=15, weight='bold'))

        # zoomer_frame
        self.frames = (customtkinter.CTkFrame(self, border_color='ivory4', border_width=1, corner_radius=0, fg_color='gray90'), # , border_color='green', border_width=1,
                      customtkinter.CTkFrame(self,  border_color='ivory4', border_width=1, corner_radius=0, fg_color='gray90')) #fg_color="transparent", 
        for form in self.frames:
            # column
            form.grid_columnconfigure(0, weight=1)
            # row
            form.grid_rowconfigure(0, weight=1)
        self.zoomer_frame = self.frames[1]


        
        # page_slider
        # if self.images:
        #     self.page_slider = customtkinter.CTkSlider(self, from_=0, to=len(self.images)-1, number_of_steps=len(self.images)-1, 
        #                                            command = self.slider_event, height=25)
        #     self.page_slider.set(self.cur_imageId)
        # else:
        self.page_slider = customtkinter.CTkSlider(self, height=25, state="disabled",
                                                    button_color='gray60', button_hover_color='gray30', progress_color='dodgerblue4',
                                                    fg_color='snow3')
        self.page_slider.set(0)
            
         # to=len(self.images)-1, number_of_steps=len(self.images)-1,
        # number_of_steps=5,
        
        # self.slider_1.grid(row=3, column=0, padx=(20, 10), pady=(10, 10), sticky="we")

        
        # page_frame
        self.page_frame = customtkinter.CTkFrame(self,  fg_color='transparent')
        self.page_entry = customtkinter.CTkEntry(self.page_frame, width=50, font=customtkinter.CTkFont(size=14), justify='center')
        self.page_entry.bind("<Return>", (lambda event: self.entry_event(self.page_entry.get())))
        # self.page_entry.insert(0, '1')
        self.whole_page_label = customtkinter.CTkLabel(self.page_frame, text='  / ' + '     ',
                                                 font=customtkinter.CTkFont(size=16))




        tkinter.ttk.Separator(self, orient='vertical').pack(side='left', anchor='w', fill='y', pady=(40, 10), padx=10)
        # self.btn1.pack()
        
        # self.btn4 = customtkinter.CTkButton(self, text='test', command=self.test)
        # self.btn4.pack()
        


        # initial settings: grid
        # tkinter.Frame(self, height=15).pack()
        # self.title.grid(sticky="nsew")
        self.title.pack(fill='x', pady=(25, 0))

        # self.zoom_btn.pack(anchor='w')
        # self.zoomer_frame.grid(sticky="nsew")
        self.zoomer_frame.pack(fill='both', expand=True, padx=(10, 20))
        self.zoomer_frame.pack_propagate(0)

        self.zoomer = None


        # self.zoomer = ImageZoom(self.zoomer_frame, controller, image=image)
        # self.zoomer.grid(sticky="nsew")
        # self.zoomer.pack(fill='both', expand=True)
        # zoomer frame 안에
        # self.zoomer.grid(row=0, column=0, sticky="nsew")

        # self.slider_1.grid(sticky="nsew")
        # self.page_entry.grid(sticky="nsew")


        self.page_slider.pack(fill='x', pady=10, padx=(10, 20))
        
        # self.btn2.pack(side='left', anchor='e', pady=(0, 30), padx=(0, 20), expand=True) # , padx=(100,0)
        # self.btn3.pack(side='right', anchor='w', pady=(0, 30), padx=(20,0), expand=True)
        self.page_frame.pack(side='top', pady=(2, 30), anchor='center')
        

        
        self.page_entry.pack(side='left')
        self.whole_page_label.pack(side='right')


        self.zoomer_frame.bind("<MouseWheel>", (lambda event: self.__wheel(event)))
        # self.zoomer_frame.bind('<Control-MouseWheel>', lambda event: self.zooming(event))

        # self.btntest = customtkinter.CTkButton(self, text='test', command=lambda:self.test()).pack()


        # data
        self.images = None
        self.currentImageId = tkinter.IntVar()
        self.imscale = 1


    def test(self):
        self._update(images, 0)


    def zooming(self, event):

        if not self.zoomer:
            return
        
        widget = self.zoomer_frame.winfo_children()[0]
        if isinstance(widget, customtkinter.CTkLabel):
            widget.destroy()

            self.zoomer = ImageZoomer(self.zoomer_frame, image=self.images[self.currentImageId.get()], imscale=self.imscale)
            self.zoomer.grid(row=0, column=0, sticky="nsew")

            self.zoomer.canvas.bind("<MouseWheel>", (lambda event: self.__wheel(event)))
            print('ok')


        

    def startThread(self, func):
        thread = threading.Thread(target=func)
        thread.daemon = True
        thread.start()
        

    def __wheel(self, event):
        """ Zoom with mouse wheel """

        if not self.images:
            return

        # Respond to Linux (event.num) or Windows (event.delta) wheel event
        if event.num == 5 or event.delta == -120:  # scroll down, smaller
            self.next_image()

        if event.num == 4 or event.delta == 120:  # scroll up, bigger
            self.back_image()



    def switch_form(self):
        for form in self.frames:
            if form is not self.zoomer_frame:
                self.zoomer_frame = form
                break


    # def _set_images(self):



    def _update(self, *args, images, image_id):

        if not images:

            for child in self.zoomer_frame.winfo_children():
                child.destroy()

            self.page_entry.delete(0, 'end')

            self.page_slider.set(0)
            self.whole_page_label.configure(text='  / ' + '  ' + '   ')
            return


        self.images = images
        self.page_slider.configure(to=len(self.images)-1, number_of_steps=len(self.images)-1, 
                                                   command = self.slider_event, state='normal')
        self.whole_page_label.configure(text='  / ' + '  ' + str(len(self.images)))


        self.currentImageId.set(image_id)
        image = self.images[self.currentImageId.get()]

        self.imwidth, self.imheight = image.size
        self.update_idletasks()
        imratio = min((self.zoomer_frame.winfo_width()-5)/self.imwidth, (self.zoomer_frame.winfo_height()-5)/self.imheight)
        self._change_size = 0 if self.imscale==imratio else 1
        self.imscale = imratio
        if self.zoomer_frame.winfo_children():
            # 이미 이미지/zoomer 있을 때
            self.zoomer = self.zoomer_frame.winfo_children()[0]

            if (isinstance(self.zoomer, customtkinter.CTkLabel)) and (not self._change_size):
                self.zoomer.configure(image=customtkinter.CTkImage(image, image, size=(self.imwidth*imratio,self.imheight*imratio)))
                # return
            else:
                for child in self.zoomer_frame.winfo_children():
                    child.destroy()

                self.zoomer = customtkinter.CTkLabel(self.zoomer_frame, image=customtkinter.CTkImage(image, image, size=(self.imwidth*imratio,self.imheight*imratio)), text='')
                self.zoomer.grid(row=0, column=0) # , sticky="nsew"
                self.zoomer.bind("<MouseWheel>", (lambda event: self.__wheel(event)))

        else:
            self.zoomer = customtkinter.CTkLabel(self.zoomer_frame, image=customtkinter.CTkImage(image, image, size=(self.imwidth*imratio,self.imheight*imratio)), text='')
            self.zoomer.grid(row=0, column=0) # , sticky="nsew"
            self.zoomer.bind("<MouseWheel>", (lambda event: self.__wheel(event)))



        # # slider
        self.page_slider.set(self.currentImageId.get())
        # # entry
        self.page_entry.delete(0, 'end')
        self.page_entry.insert(0, str(self.currentImageId.get()+1))


        self.update_idletasks()
        self.zoomer_frame.tkraise()

        self.zoomer.bind('<Control-MouseWheel>', lambda event: self.zooming(event))


        # file = self.controller.uploader.file_list.focus()
        # self.controller.workList[file]['cur_imageId'] = self.image_id

        
        


    
    def back_image(self):
        if self.currentImageId.get() == 0:
            return
        else:
            self.currentImageId.set(self.currentImageId.get()-1)
            self._update(images=self.images, image_id=self.currentImageId.get())


    def next_image(self):
        if self.currentImageId.get() == len(self.images)-1:
            return
        else:
            self.currentImageId.set(self.currentImageId.get()+1)
            self._update(images=self.images, image_id=self.currentImageId.get())



    def slider_event(self, value):
        if self.currentImageId.get() != int(value):
            self.currentImageId.set(value)
            self._update(images=self.images, image_id=self.currentImageId.get())
        
        # print(value)


    def entry_event(self, value):
        self.page_slider.set(int(value)-1)

        self.slider_event(int(value)-1)


    # def test(self):
    #     # self.page_slider.set(int(value)-1)

    #     print(self.zoomer.canvas.canvas.winfo_width(), self.zoomer.canvas.canvas.winfo_height())
