# -*- coding: utf-8 -*-
"""Hybrid page classification: CNN probability threshold + rule-based text matching.

Rule (Section 3.3.3 of the article):
  1. If the top-1 CNN probability is >= PROB_THRESHOLD (0.99), the top-1 label is assigned.
  2. Otherwise, for k = 1 ... TOP_K (5), the text variations of the top-k label are searched in the
     page text. The first label whose variation is found is assigned.
  3. If no variation is found for k = 1 ... TOP_K, the top-1 label is assigned.
Page text and variations are compared after removing spaces and converting to upper case.
"""
from divide.resources.CONFIG import classes, class_variations, PROB_THRESHOLD, TOP_K


def normalize_text(text):
    return text.replace(' ', '').replace('\t', '').replace('\n', '').upper()


def classify_page(text_whole, top_k_classes, top_k_probs,
                  threshold=PROB_THRESHOLD, max_k=TOP_K):
    """text_whole: normalized page text ('' if the page has no text layer)
    top_k_classes: class indices sorted by CNN probability (descending)
    top_k_probs:   the corresponding probabilities
    returns: (label, routed) where routed is True if the text-matching step was used"""
    top1 = classes[int(top_k_classes[0])]
    if float(top_k_probs[0]) >= threshold:
        return top1, False
    if text_whole:
        for class_idx in list(top_k_classes)[:max_k]:
            label = classes[int(class_idx)]
            for variation in class_variations.get(label, []):
                if normalize_text(variation) in text_whole:
                    return label, True
    return top1, True
