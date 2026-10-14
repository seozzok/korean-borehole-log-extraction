# Structured extraction from Korean-language borehole logs

Code for the article **"Integrated document processing for structured extraction from Korean-language borehole logs"** (Seo, Park, Seo and Yun, *Scientific Reports*).

The program takes a subsurface investigation report (PDF), classifies its pages, finds the borehole-log pages, segments their table layout, extracts the general information and depth-wise data, and exports them to an Excel template. Geological descriptions are classified with KoBERT in a separate module (`kobert/`), which is not part of the program interface.

## What is and is not included

| Included | Not included (confidential) |
|---|---|
| Program source (page classification, layout segmentation, extraction, interface, export) | Subsurface investigation reports, page images and extracted data |
| Hybrid classification rule (CNN probability threshold + text matching), the 27 page classes and their text variations | Trained CNN and KoBERT weights (trained on the confidential reports) |
| CNN data preparation and training code (`cnn_training/`) | Labelled sentences used for KoBERT |
| KoBERT training and evaluation notebooks (`kobert/`) | Report identities |
| KoBERT class counts per split (`splits/`) | |

The reports were provided by a construction company under a confidentiality agreement and cannot be redistributed. For this reason the trained weights, which were fitted to these reports, are not distributed either. The code runs with weights trained on other data using the scripts in `cnn_training/` and `kobert/`.

## Processing steps and where they are in the code

| Step (article section) | Module | Main settings |
|---|---|---|
| PDF pages to images and text layer | `divide/divider.py` (`Divider.preprocess`) | 200 dpi rendering (PyMuPDF), text layer read from the PDF |
| Page classification, CNN (3.3.1–3.3.2) | `divide/divider.py`, `divide/resources/CONFIG.py` | EfficientNet-b0, input resized to 354 × 250 px |
| Hybrid classification, text matching (3.3.3) | `divide/rule_based.py` (`classify_page`) | Top-1 probability ≥ 0.99: CNN label. Otherwise the text variations of the top-k labels (k = 1 … 5) are searched in the page text; the first match is assigned, and the top-1 label is kept if nothing matches |
| Layout segmentation (3.4) | `extract/drill_log/page_segmentation.py` | Grayscale page binarized with an intensity threshold (250 of 255, inverted); vertical and horizontal lines separated by erosion followed by dilation with 50-pixel line-shaped kernels; hierarchical filtering of line segments to split the general-information and depth-wise sections |
| Header–cell identification and value extraction (3.5.1) | `extract/drill_log/data_extraction.py`, `info_extraction.py`, `utils.py` | Header keyword lists (`check_variations`, key codes) |
| SPT-N post-processing (4.2) | `extract/drill_log/utils.py` (`formatting`) | N = int(30 × blow count / penetration in cm). This equals the blow count for a 300 mm penetration, and 50 × 300 / penetration (mm), rounded down, for records of 50 blows with less than 300 mm penetration. Blow count and penetration are kept in separate columns |
| Export (5) | `ui/utils.py` (`write_on_xlsx`), `assets/__template.xlsx` | One sheet per table (LOCA, WSTD, CORE, CDIA, GEOL, DISC, WETH, FRAC, ISPT) |
| Geological description classification (3.5.2) | `kobert/` | KoBERT, max length 512, batch 16, AdamW (weight decay 0.01), learning rate 5 × 10⁻⁵ with 10% warm-up followed by cosine decay, gradient clipping at 1.0, dropout 0.5, 8 epochs |

## Installation

Tested with Python 3.8 on Windows 10.

```
conda create -n borehole python=3.8
conda activate borehole
# install PyTorch and torchvision for your CUDA version (https://pytorch.org)
pip install -r requirements.txt
```

## Usage

1. Put CNN weights (a `state_dict` of EfficientNet-b0 trained with the class list in `divide/resources/class_variations.json`) at `divide/resources/CNN_TrainedModel/best_model.pt`, or set the environment variable `BLE_MODEL_PATH`.
2. Graphical interface: `python main.py`
3. Without the interface:
   ```
   python run_headless.py --pdf report.pdf --out result.xlsx
   ```
   This writes `result.xlsx` and `result_page_labels.csv` (page label and CNN top-k probabilities for every page), and prints the time of each step.

## Class list and keyword dictionary

`divide/resources/class_variations.json` holds the 27 page classes in the label-index order used for CNN training (`class_order`, alphabetical order of the class folders) and, for each class, the text variations used by the text-matching step (`class_variations`). The text variations were compiled from the training reports only. Page text and variations are compared after removing spaces and converting to upper case.

## Reproducibility

| Item | Value |
|---|---|
| Report-level split | 157 development reports and 29 test reports from sites not used for development. Report identities are confidential and are not distributed. Test reports were used only for the final evaluation. Cross-validation folds on the development reports were formed at the report level, so all pages of a report belong to one fold |
| CNN training | Adam, learning rate 0.001, batch size 16, 35 epochs, cross-entropy loss, random shift up to 15 px with white padding; random seed 42 |
| KoBERT split | Sentence-level random split 70/15/15 with `train_test_split(..., random_state=0)` (not stratified); class counts in `splits/kobert_class_counts_by_split.csv` |
| KoBERT training | Random seed 12; the checkpoint with the highest validation accuracy is kept |
| Measured environment | Windows 10, Intel Core i5-13600KF 3.5 GHz, 32 GB RAM, NVIDIA RTX 3090 (24 GB), PyTorch 2.4.1, CUDA 12.1 |

## Citation

If you use this code, please cite the article (DOI to be added on publication) and this archive (https://doi.org/10.5281/zenodo.23339843).

## License

MIT (see `LICENSE`).
