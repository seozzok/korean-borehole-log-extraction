# KoBERT classification of geological descriptions

| Notebook | Step |
|---|---|
| `01_train_kobert.ipynb` | Training for one task (`TASK = 'D'`, `'S'` or `'F'`), checkpoint selection on the validation split, test evaluation |
| `02_evaluate_kobert_roc.ipynb` | Test evaluation of the three tasks: confusion matrices, class-wise precision/recall/F1, one-vs-rest ROC curves and AUC (per class, micro-average, macro-average of the averaged ROC curve, weighted); all values and curves are written to CSV |

Three classification tasks: weathering condition (D1–D5), strength (S1–S5) and discontinuity spacing (F1–F5).

- Model: KoBERT (SK T-Brain), classification head on the pooled [CLS] output with dropout 0.5
- Max length 512, batch size 16, AdamW (weight decay 0.01; none for bias and LayerNorm), learning rate 5 × 10⁻⁵,
  10% warm-up followed by cosine decay, gradient clipping at 1.0, 8 epochs, cross-entropy loss, random seed 12
- Split: sentence-level random 70/15/15 with `train_test_split(..., random_state=0)`, not stratified
  (class counts: `../splits/kobert_class_counts_by_split.csv`)
- The checkpoint with the highest validation accuracy is evaluated once on the test split

Input: `data/Labeled_data_UTF8_{D,S,F}.csv` with columns `Text` and `Score` (1–5). The labelled sentences and trained
weights are not distributed (see the main README).
