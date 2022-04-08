import os
from pathlib import Path
from datetime import datetime as dt

from arcgis.gis import GIS
from arcgis.raster.functions import RFT
from arcgis.learn import prepare_data, MaskRCNN
# from torchvision.models.detection import mask_rcnn as MaskRCNN
from fastai.vision.transform import crop, rotate, brightness, contrast, rand_zoom

# Get data
# in_raster =
# in_objects =
training_data_dir = r'C:\Users\dyera\Documents\Task 6\Atlantic Bathymetric Terrain Model\ArcGIS Deep Learning\Training Data'
output_dir = r'C:\Users\dyera\Documents\Task 6\Atlantic Bathymetric Terrain Model\ArcGIS Deep Learning\Outputs'
os.chdir(output_dir)

# set batch size
batch_size = 8

# prepare data
train_tfms = [rotate(degrees=30,  # defining a transform using rotate with degrees fixed to
                     p=0.5),  # a value, but by passing an argument p.

              crop(size=224,  # crop of the image to return image of size 224. The position
                   p=1.,  # is given by (col_pct, row_pct), with col_pct and row_pct
                   row_pct=(0, 1),  # being normalized between 0 and 1.
                   col_pct=(0, 1)),

              brightness(change=(0.4, 0.6)),  # Applying change in brightness of image.

              contrast(scale=(1.0, 1.5)),  # Applying scale to contrast of image.

              rand_zoom(scale=(1., 1.2))]  # Randomized version of zoom.

val_tfms = [crop(size=224,  # cropping the image to same size for validation datasets
                 p=1.0,  # as in training datasets.
                 row_pct=0.5,
                 col_pct=0.5)]

transforms = (train_tfms, val_tfms)  # tuple containing transformations for data augmentation
# of training and validation datasets respectively.

data = prepare_data(training_data_dir, batch_size, transforms)

# visualize a few samples from training data
data.show_batch(rows=5)

# load model architecture
model = MaskRCNN(data)

# find optimal learning rate
lr = model.lr_find()
print('Optimal learning rate: {}'.format(lr))

# fit the model
model.fit(epochs=100, lr=lr, wd=0.1)

# accuracy assessment
model.average_precision_score(detect_thresh=0.3, iou_thresh=0.3, mean=False)

# visualize results on validation set
model.show_results(rows=5, thresh=0.5)

# save the model

model.save('Scarps_ArcGIS_MaskRCNN')