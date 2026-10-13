# -*- coding: utf-8 -*-
"""Run the pipeline on one PDF report without the graphical interface.

  python run_headless.py --pdf report.pdf --out result.xlsx [--model path/to/best_model.pt]

Steps (same modules as the program in main.py):
  1. PDF pages -> images (200 dpi) and text layer          divide/divider.py  Divider.preprocess
  2. page classification: CNN + text matching (0.99, k<=5)  divide/divider.py  Divider.divide
  3. layout segmentation and data extraction of the pages
     classified as borehole logs                            extract/
  4. export to the Excel template                           ui/utils.py  write_on_xlsx
Writes <out>.xlsx and <out>_page_labels.csv (page, label, CNN top-k probabilities).
"""
import argparse
import csv
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pdf', required=True)
    ap.add_argument('--out', required=True, help='output .xlsx')
    ap.add_argument('--model', default=None, help='CNN weights (state_dict); default: CONFIG.best_model_path')
    args = ap.parse_args()
    out_dir = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(out_dir, exist_ok=True)
    if args.model:
        os.environ['BLE_MODEL_PATH'] = os.path.abspath(args.model)

    t0 = time.perf_counter()
    from settings import Settings
    from divide.resources.CONFIG import BOREHOLE_LOG_CLASS
    from divide.divider import Divider
    from extract.main import MainExtractor
    from ui.utils import write_on_xlsx
    divider = Divider(args.pdf, controller_main_path=HERE)
    t1 = time.perf_counter()

    divider.preprocess()
    t2 = time.perf_counter()
    divider.divide(Settings.TESTS_DISPLAYED, [BOREHOLE_LOG_CLASS])
    t3 = time.perf_counter()

    n_pages = len(divider.images)
    labels = [''] * n_pages
    for label, pages in divider.divided_dict.items():
        for p in pages:
            labels[p] = label
    base = os.path.splitext(args.out)[0]
    with open(base + '_page_labels.csv', 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.writer(f)
        w.writerow(['page', 'label', 'cnn_top_k'])
        for p in range(n_pages):
            topk = '; '.join('%s:%.4f' % (k, v) for k, v in divider.page_cnn_predict[p].items())
            w.writerow([p + 1, labels[p], topk])

    log_pages = divider.divided_dict.get(BOREHOLE_LOG_CLASS, [])
    data = {}
    if log_pages:
        extractor = MainExtractor(args.pdf, {BOREHOLE_LOG_CLASS: log_pages}, divider.images, divider.page_tlines)
        extractor.extract()
        worker = extractor.drill_log
        worker.join()
        data = worker.data
    t4 = time.perf_counter()
    write_on_xlsx(data=data, template=os.path.join(HERE, 'assets', '__template.xlsx'), dst_path=args.out)
    t5 = time.perf_counter()

    print('pages: %d, borehole-log pages: %d' % (n_pages, len(log_pages)))
    print('model loading %.2f s | PDF to image + text %.2f s | page classification %.2f s | '
          'segmentation + extraction %.2f s | export %.2f s' % (t1 - t0, t2 - t1, t3 - t2, t4 - t3, t5 - t4))
    print('saved:', args.out, 'and', base + '_page_labels.csv')


if __name__ == '__main__':
    main()
