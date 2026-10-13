
import fitz
import os
from PIL import Image

import threading

from pprint import pprint

from extract.utils import get_textstruct


from extract.drill_log import extractor as drill_log





class MainExtractor():
    def __init__(self, pdf_path, page_info, images=None, pages_tlines=None):
        ''' page_info {'test': [pages_id]}
        '''

        doc = fitz.open(pdf_path)
        
        self.workers = [None for i in range(1)] # worker 자리 모두 할당
        for test, page in page_info.items():

            page_nos = page

            pagesizeList = [(doc[page].rect.width, doc[page].rect.height) for page in page_nos]
            imageList = [images[page] for page in page_nos]
            textList = [get_textstruct(None, lines=pages_tlines[page]) for page in page_nos]

            if test == '시추주상도':
                  self.drill_log = drill_log.Extractor(pagesizeList, imageList, textList)
                  self.drill_log.pages = page_nos

                  self.workers[0] = self.drill_log

        self.data_extracted = {}
        self.raw_text = {}


    def extract(self):
      
        for i, worker in enumerate(self.workers):

            if worker is None: continue

            worker.start()




