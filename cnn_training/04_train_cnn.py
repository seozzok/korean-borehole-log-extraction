# -*- coding: utf-8 -*-
"""Train and cross-validate the EfficientNet-b0 page classifier.

Configuration (article, Section 3.3.2 and Table 2):
  EfficientNet-b0, ImageNet initialization, all layers retrained
  Adam, learning rate 0.001, batch size 16, 35 epochs, cross-entropy loss, random seed 42
  five-fold cross-validation on the development reports with report-level folds

Input folder: one sub-folder per class (27 classes) with the resized page images (01_rotate_resize.ipynb)
and their shifted copies (03_augmentation_shift.ipynb). File names start with the report number,
e.g. "072_pagenumber182.png"; shifted copies end with "_augmented_<k>.png".
  - all pages of a report are assigned to the same fold
  - shifted copies are used for training only; validation uses the original pages

usage:
  python 04_train_cnn.py --data data/page_images_augmented --out runs/cv
  python 04_train_cnn.py --data data/page_images_augmented --out runs/final --final
  (optional) --exclude-reports test_reports.txt   report numbers held out from development, one per line
"""
import argparse
import csv
import json
import os
import random
import time

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset
from torchvision import datasets
from torchvision.transforms import transforms
from sklearn.model_selection import GroupKFold
from sklearn.metrics import f1_score
from efficientnet_pytorch import EfficientNet

HERE = os.path.dirname(os.path.abspath(__file__))
CLASS_JSON = os.path.join(HERE, '..', 'divide', 'resources', 'class_variations.json')

MEAN = [0.9266, 0.9244, 0.9212]   # 02_image_mean_std.ipynb
STD = [0.1289, 0.1308, 0.1346]


def fix_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    np.random.seed(seed)
    random.seed(seed)


def report_id(path):
    return os.path.basename(path).split('_')[0]


def is_augmented(path):
    return '_augmented_' in os.path.basename(path)


def build_model(num_classes, init):
    if init == 'imagenet':
        model = EfficientNet.from_pretrained('efficientnet-b0')
    else:
        model = EfficientNet.from_name('efficientnet-b0')
    model._fc = nn.Linear(model._fc.in_features, num_classes)
    return model


def run_epoch(model, loader, device, criterion, optimizer=None):
    train = optimizer is not None
    model.train(train)
    total, correct, loss_sum = 0, 0, 0.0
    y_true, y_pred = [], []
    with torch.set_grad_enabled(train):
        for images, labels in loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            loss = criterion(outputs, labels)
            if train:
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            pred = outputs.argmax(1)
            loss_sum += loss.item() * images.size(0)
            correct += (pred == labels).sum().item()
            total += images.size(0)
            y_true += labels.cpu().tolist()
            y_pred += pred.cpu().tolist()
    return loss_sum / total, correct, total, y_true, y_pred


def train(model, train_set, val_set, args, device, log_rows, tag):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=args.lr)
    g = torch.Generator()
    g.manual_seed(args.seed)
    train_loader = DataLoader(train_set, batch_size=args.batch_size, shuffle=True, num_workers=args.workers,
                              generator=g)
    val_loader = DataLoader(val_set, batch_size=args.batch_size, shuffle=False,
                            num_workers=args.workers) if val_set is not None else None
    result = None
    for epoch in range(1, args.epochs + 1):
        t0 = time.time()
        tr_loss, tr_c, tr_n, _, _ = run_epoch(model, train_loader, device, criterion, optimizer)
        row = {'run': tag, 'epoch': epoch, 'train_loss': tr_loss, 'train_correct': tr_c, 'train_n': tr_n}
        if val_loader is not None:
            va_loss, va_c, va_n, yt, yp = run_epoch(model, val_loader, device, criterion)
            row.update({'val_loss': va_loss, 'val_correct': va_c, 'val_n': va_n, 'val_accuracy': va_c / va_n,
                        'val_macro_f1': f1_score(yt, yp, average='macro', labels=sorted(set(yt)))})
            result = row
        row['seconds'] = time.time() - t0
        log_rows.append(row)
        print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in row.items()})
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--exclude-reports', default=None)
    ap.add_argument('--final', action='store_true', help='train one model on all development reports')
    ap.add_argument('--folds', type=int, default=5)
    ap.add_argument('--epochs', type=int, default=35)
    ap.add_argument('--batch-size', type=int, default=16)
    ap.add_argument('--lr', type=float, default=0.001)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--workers', type=int, default=0)
    ap.add_argument('--init', choices=['imagenet', 'random'], default='imagenet')
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    fix_seed(args.seed)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    tf = transforms.Compose([transforms.Resize((354, 250)), transforms.ToTensor(),
                             transforms.Normalize(mean=MEAN, std=STD)])
    ds = datasets.ImageFolder(args.data, transform=tf)
    folder_classes = [c[:-len('_resized')] if c.endswith('_resized') else c for c in ds.classes]
    with open(CLASS_JSON, encoding='utf-8') as f:
        class_order = json.load(f)['class_order']
    if folder_classes != class_order:
        raise SystemExit('class folders differ from class_order in class_variations.json:\n%s' % folder_classes)

    excluded = set()
    if args.exclude_reports:
        with open(args.exclude_reports, encoding='utf-8') as f:
            excluded = {line.strip() for line in f if line.strip()}
    paths = [p for p, _ in ds.samples]
    dev_idx = [i for i, p in enumerate(paths) if report_id(p) not in excluded]
    log_rows = []

    if args.final:
        model = build_model(len(class_order), args.init).to(device)
        train(model, Subset(ds, dev_idx), None, args, device, log_rows, 'final')
        torch.save(model.state_dict(), os.path.join(args.out, 'best_model.pt'))
    else:
        groups = [report_id(paths[i]) for i in dev_idx]
        summary = []
        for k, (tr, va) in enumerate(GroupKFold(n_splits=args.folds).split(dev_idx, groups=groups), start=1):
            fix_seed(args.seed)
            tr_idx = [dev_idx[i] for i in tr]
            va_idx = [dev_idx[i] for i in va if not is_augmented(paths[dev_idx[i]])]
            tr_reports = {report_id(paths[i]) for i in tr_idx}
            va_reports = {report_id(paths[i]) for i in va_idx}
            assert not tr_reports & va_reports, 'a report appears in both training and validation'
            model = build_model(len(class_order), args.init).to(device)
            res = train(model, Subset(ds, tr_idx), Subset(ds, va_idx), args, device, log_rows, 'fold%d' % k)
            torch.save(model.state_dict(), os.path.join(args.out, 'fold%d.pt' % k))
            summary.append({'fold': k, 'val_reports': len(va_reports), 'val_pages': res['val_n'],
                            'val_correct': res['val_correct'], 'val_accuracy': res['val_accuracy'],
                            'val_macro_f1': res['val_macro_f1']})
        with open(os.path.join(args.out, 'cv_summary.csv'), 'w', newline='', encoding='utf-8') as f:
            w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
            w.writeheader()
            w.writerows(summary)
        acc = [s['val_accuracy'] for s in summary]
        f1 = [s['val_macro_f1'] for s in summary]
        print('accuracy %.4f +/- %.4f, macro-F1 %.4f +/- %.4f' % (np.mean(acc), np.std(acc, ddof=1),
                                                                  np.mean(f1), np.std(f1, ddof=1)))
    with open(os.path.join(args.out, 'training_log.csv'), 'w', newline='', encoding='utf-8') as f:
        keys = []
        for r in log_rows:
            keys += [k for k in r if k not in keys]
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(log_rows)


if __name__ == '__main__':
    main()
