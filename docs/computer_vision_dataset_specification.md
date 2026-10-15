# AGRO LIFE-AI
## Tomato Computer Vision Dataset Specification

**Project:** Produce Decay and Shelf-Life Prediction System Using Data Analytics and Machine Learning

**Module:** Computer Vision Research Module

**Produce:** Tomato

**System:** AGRO LIFE-AI

**Status:** Research Prototype

---

## 1. Purpose

The purpose of this dataset is to support the development and evaluation
of a computer vision component for AGRO LIFE-AI.

The computer vision component is intended to analyse visible characteristics
of tomatoes and classify their observable quality or decay condition.

The computer vision model will initially be developed for tomatoes because
the current AGRO LIFE-AI research system has a validated tomato shelf-life
model.

The computer vision model will not automatically be assumed to predict
food safety or actual biochemical quality.

---

## 2. Initial Image Classes

The initial tomato dataset will contain four visible-condition classes.

### 2.1 Fresh

Tomatoes showing no obvious visible signs of decay.

Typical characteristics may include:

- intact surface
- no obvious fungal growth
- no major dark or rotten areas
- relatively uniform appearance
- no extensive visible tissue deterioration

---

### 2.2 Early Decay

Tomatoes showing early visible deterioration.

Possible characteristics include:

- small discoloured areas
- early surface deterioration
- minor soft or damaged regions
- small visible decay spots

---

### 2.3 Moderate Decay

Tomatoes showing clearly visible deterioration.

Possible characteristics include:

- larger discoloured regions
- visible softening or deterioration
- multiple decay areas
- noticeable surface damage

---

### 2.4 Advanced Decay

Tomatoes showing extensive visible deterioration.

Possible characteristics include:

- large areas of visible decay
- extensive surface deterioration
- severe discolouration
- extensive tissue breakdown
- visible fungal growth where present

---

## 3. Important Labelling Rule

Images must be labelled according to visible evidence.

The labels must not be assigned only according to assumptions about
storage duration.

For example:

A tomato stored for 10 days must not automatically be labelled
"moderate_decay."

The visible condition in the image must determine the image class.

---

## 4. Dataset Directory Structure

The initial dataset will use the following structure:

data/
└── images/
    └── tomato/
        ├── fresh/
        ├── early_decay/
        ├── moderate_decay/
        └── advanced_decay/

Processed image data will be stored separately.

---

## 5. Image Requirements

Images should preferably:

- clearly show the tomato
- have sufficient lighting
- have adequate resolution
- avoid extreme blur
- avoid severe obstruction
- avoid unnecessary text or watermarks
- contain minimal irrelevant objects
- represent different tomato appearances

Images should include natural variation where possible.

Variation may include:

- different tomato sizes
- different shapes
- different orientations
- different backgrounds
- different lighting conditions
- different cameras
- different levels of visible deterioration

---

## 6. Image Source Tracking

Every image used for research must have traceable source information.

The project should maintain metadata including:

- image filename
- produce
- class
- source
- source URL where applicable
- date collected
- permission/licence information
- capture device where applicable
- notes

Random Internet images must not be treated as automatically reusable
research data.

---

## 7. Recommended Naming Convention

Images should follow a consistent naming convention.

Example:

tomato_fresh_0001.jpg

tomato_fresh_0002.jpg

tomato_early_decay_0001.jpg

tomato_moderate_decay_0001.jpg

tomato_advanced_decay_0001.jpg

---

## 8. Dataset Splitting

The dataset will be divided into:

- Training set
- Validation set
- Test set

The test set must remain separate from model development and training.

Images that are duplicates or near-duplicates must not be distributed
across different subsets.

Where multiple photographs represent the same physical tomato,
they should be treated as a group so that related images do not leak
between training and testing.

---

## 9. Initial Target

The initial research target is to collect a balanced dataset.

A preferred starting target is:

- at least 100 images per class
- 400 images minimum for the four-class prototype

A larger dataset will be preferred where reliable and properly labelled
images are available.

Dataset size will be reported honestly rather than artificially increased
through duplication.

---

## 10. Data Augmentation

Image augmentation may be used during training to improve model
generalisation.

Possible augmentation techniques include:

- small rotations
- horizontal flipping where appropriate
- controlled brightness changes
- controlled zoom
- controlled cropping

Augmentation must not change the actual decay class.

Augmented versions of an image must remain within the same dataset
partition as the original image.

---

## 11. Image Preprocessing

Before model training, images may be:

1. loaded
2. checked for corruption
3. converted to a consistent image format
4. resized to the selected model input size
5. normalised
6. inspected for class-label consistency

The original images should be preserved separately from processed images.

---

## 12. Quality Control

The dataset preparation process should identify:

- corrupted images
- unsupported formats
- duplicate filenames
- duplicate images where detectable
- extremely small images
- unreadable images
- missing class folders
- invalid class names

Invalid records must be reported before model training.

---

## 13. Computer Vision Objective

The initial computer vision objective is:

> To develop a research prototype capable of classifying visible tomato
> quality/decay conditions from images.

The model output will initially be:

- Fresh
- Early Decay
- Moderate Decay
- Advanced Decay

---

## 14. Relationship With Shelf-Life Prediction

The current AGRO LIFE-AI shelf-life model uses numerical research
measurements, including:

- Day-4 Weight Loss
- Day-4 Titratable Acidity

The computer vision model does not currently replace these measurements.

A future integrated architecture may use computer vision to estimate
appropriate visible quality characteristics and then connect those
outputs with a validated shelf-life prediction model.

This connection must only be implemented after appropriate training,
validation, and testing.

---

## 15. Validation

The computer vision model will be evaluated using appropriate
classification metrics.

These may include:

- accuracy
- precision
- recall
- F1-score
- confusion matrix

Class-specific performance will also be examined.

---

## 16. Limitations

The initial computer vision model may be affected by:

- lighting conditions
- camera quality
- background variation
- image angle
- occlusion
- tomato variety
- physical damage
- limited dataset size
- differences between research images and real-world images

These limitations must be reported in the final mini-project.

---

## 17. Research Integrity

The system must not claim that an image alone proves:

- food safety
- microbiological safety
- exact biochemical composition
- exact remaining shelf life

Such claims require appropriate evidence and validation.

AGRO LIFE-AI will therefore describe computer vision results as
research-based visual quality or decay assessment.

---

## 18. Future Expansion

After the tomato computer vision prototype is validated, the architecture
may be expanded to:

- mango
- banana
- avocado
- orange
- leafy vegetables
- other produce

Each produce type should have appropriate training data and validation.

A tomato model must not be used to predict another produce type without
appropriate produce-specific evidence.

---

## 19. Dataset Status

Current status:

[ ] Image collection completed

[ ] Image metadata completed

[ ] Dataset quality checking completed

[ ] Training dataset prepared

[ ] Validation dataset prepared

[ ] Test dataset prepared

[ ] Computer vision model trained

[ ] Computer vision model validated

[ ] Camera integration validated

---

## 20. Current Research Position

The AGRO LIFE-AI project currently has a validated research-based
numerical shelf-life model for tomatoes.

The computer vision component is now being developed as a separate
research module.

The camera interface may capture an image, but image-based quality
classification will only be described as validated after the computer
vision model has been trained and evaluated using an appropriate dataset.