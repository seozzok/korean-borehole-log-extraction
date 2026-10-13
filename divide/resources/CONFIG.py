# -*- coding: utf-8 -*-
"""Configuration of the page-classification stage (Phase A).

Values that correspond to the article:
  - CNN: EfficientNet-b0, input resized to 354 x 250 px, trained on the class list below
  - Hybrid rule: if the top-1 CNN probability is >= PROB_THRESHOLD (0.99) the CNN label is kept;
    otherwise the text variations of the top-k labels (k = 1 ... TOP_K = 5) are searched in the page text
  - PDF pages are rendered at PDF_DPI (200 dpi)
"""
import json
import os

import torch
import torch.nn as nn
from torchvision.transforms import transforms
from efficientnet_pytorch import EfficientNet

RESOURCE_DIR = os.path.dirname(os.path.abspath(__file__))

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ---------------------------------------------------------------- hybrid classification rule
PROB_THRESHOLD = 0.99   # top-1 probability at or above which the CNN label is accepted without text matching
TOP_K = 5               # number of CNN candidates searched by the text-matching algorithm

# ---------------------------------------------------------------- PDF rendering
PDF_DPI = 200

# ---------------------------------------------------------------- class list and text variations
# divide/resources/class_variations.json
#   {"class_order": [...27 class names in the label-index order used for training...],
#    "class_variations": {"<class name>": ["<text variation>", ...], ...}}
CLASS_VARIATIONS_JSON = os.path.join(RESOURCE_DIR, 'class_variations.json')
with open(CLASS_VARIATIONS_JSON, encoding='utf-8') as _f:
    _cfg = json.load(_f)
class_variations = _cfg.get('class_variations', {})
if not class_variations:
    raise RuntimeError('class_variations.json is empty: fill in the class list and text variations '
                       '(see README, "Class list and keyword dictionary").')
classes = list(_cfg.get('class_order') or sorted(class_variations.keys()))
if sorted(classes) != sorted(class_variations.keys()):
    raise RuntimeError('class_order and class_variations keys differ in class_variations.json')
num_classes = len(classes)
top_k = min(TOP_K, num_classes)   # (name used by divider.py)
BOREHOLE_LOG_CLASS = '시추주상도'
if BOREHOLE_LOG_CLASS not in classes:
    raise RuntimeError('class list must contain the borehole-log class "%s"' % BOREHOLE_LOG_CLASS)

# ---------------------------------------------------------------- CNN
model_name = 'EfficientNet_b0'
learning_rate = 0.001   # training settings of the reported model (for reference)
batch_size = 16
num_epochs = 35

# Trained weights are not distributed (the training reports are confidential).
# Place a state_dict trained with this class list here, or set the environment variable BLE_MODEL_PATH.
best_model_path = os.environ.get('BLE_MODEL_PATH',
                                 os.path.join(RESOURCE_DIR, 'CNN_TrainedModel', 'best_model.pt'))

transform = transforms.Compose([
    transforms.Resize((354, 250)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.9266, 0.9244, 0.9212], std=[0.1289, 0.1308, 0.1346])   # cnn_training/02_image_mean_std.ipynb
])

model = EfficientNet.from_name('efficientnet-b0')
num_features = model._fc.in_features
model._fc = nn.Linear(num_features, num_classes)
