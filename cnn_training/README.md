# CNN data preparation and training (page classification)

| Notebook / script | Step |
|---|---|
| `01_rotate_resize.ipynb` | Rotate landscape pages to portrait and resize page images to 250 × 354 px (one folder per class) |
| `02_image_mean_std.ipynb` | Channel mean and standard deviation of the resized images (used for normalization in `divide/resources/CONFIG.py`) |
| `03_augmentation_shift.ipynb` | Augmentation of under-represented classes by random shifts of up to 15 px in each direction with white padding |
| `04_train_cnn.py` | Five-fold cross-validation with report-level folds (`GroupKFold` on the report number at the start of each file name; shifted copies used for training only), and training of the final model on all development reports (`--final`) |

Training configuration (`04_train_cnn.py` defaults): EfficientNet-b0 with ImageNet initialization, all layers retrained, Adam (learning rate 0.001),
batch size 16, 35 epochs, cross-entropy loss, random seed 42; five-fold cross-validation with report-level folds.

Page images and trained weights are not distributed (see the main README).
