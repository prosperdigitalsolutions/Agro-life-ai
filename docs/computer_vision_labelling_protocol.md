# AGRO LIFE-AI
## Tomato Computer Vision Image Sources and Labelling Protocol

**Project:** Design and Development of a Produce Decay and Shelf-Life Prediction System Using Data Analytics and Machine Learning

**Module:** Computer Vision Research Module

**Produce:** Tomato

**System:** AGRO LIFE-AI

**Status:** Research Prototype

---

## 1. Purpose

This protocol defines how tomato images will be collected, labelled,
verified, documented, and prepared for the AGRO LIFE-AI computer vision
research module.

The purpose is to ensure that the image dataset is consistent,
traceable, and suitable for machine learning research.

---

## 2. Image Sources

Tomato images may be obtained from the following sources:

### 2.1 Original Photographs

Original photographs captured by the project researcher may be used.

These images provide control over:

- camera/device
- lighting conditions
- background
- image angle
- distance
- tomato condition
- capture date

Original photographs should be accompanied by appropriate metadata.

---

### 2.2 Public Research Datasets

Publicly available research datasets may be used where their licensing
or usage conditions permit research use.

For every external dataset, the project should record:

- dataset name
- dataset provider
- source URL
- licence
- date accessed
- relevant publication where available
- original class definitions

The original dataset documentation must be retained.

---

### 2.3 Other Licensed Sources

Images from other sources may only be used when appropriate permission
or licensing allows their use.

Images must not be copied from websites simply because they are publicly
visible.

---

## 3. Source Metadata

Each image should have traceable information.

The metadata registry contains:

- image ID
- filename
- produce
- class
- source
- source URL
- licence/permission
- capture date
- notes

Example:

TOM-0001
tomato_fresh_0001.jpg
Tomato
Fresh
Original Photograph
N/A
Researcher Captured
2026-09-20
Clear whole tomato

---

## 4. Image Labelling Principle

The image class must represent the visible condition of the tomato.

The label must not be assigned only from:

- storage duration
- expected shelf life
- assumptions
- treatment group
- image filename
- prediction result

Visible evidence must be considered first.

---

# 5. Tomato Quality Classes

## 5.1 Fresh

A tomato may be classified as Fresh when it shows no obvious visible
decay.

Typical characteristics:

- intact surface
- no obvious fungal growth
- no major rotten regions
- no extensive dark lesions
- relatively normal appearance

Minor natural variation or superficial marks should not automatically
be classified as decay.

---

## 5.2 Early Decay

A tomato may be classified as Early Decay when early visible deterioration
is present.

Possible indicators include:

- small discoloured areas
- small decay spots
- minor surface deterioration
- early soft-looking regions
- limited visible deterioration

The deterioration should be clearly visible but not extensive.

---

## 5.3 Moderate Decay

A tomato may be classified as Moderate Decay when visible deterioration
is clearly established.

Possible indicators include:

- several visible decay regions
- larger discoloured areas
- noticeable surface deterioration
- visible soft or collapsed regions
- more extensive damage than the Early Decay class

---

## 5.4 Advanced Decay

A tomato may be classified as Advanced Decay when extensive visible
deterioration is present.

Possible indicators include:

- extensive rotten regions
- severe discolouration
- substantial tissue breakdown
- extensive surface deterioration
- visible fungal growth where present
- severe physical deterioration

---

# 6. Labelling Decision Rules

The following rules should be followed:

### Rule 1

Visible condition takes priority over assumed storage duration.

### Rule 2

Images showing the same physical tomato from different angles should
not automatically be treated as independent samples.

### Rule 3

Near-duplicate photographs should be identified and handled carefully.

### Rule 4

If an image is too unclear to assign a reliable class, it should be
placed in a review category rather than forcing a label.

### Rule 5

If there is disagreement about a label, the image should be reviewed
before inclusion in the final training dataset.

### Rule 6

A model prediction must never be used to determine the original ground
truth label.

---

# 7. Image Quality Requirements

Images should preferably:

- clearly show the tomato
- have adequate lighting
- have sufficient resolution
- be reasonably focused
- avoid excessive blur
- avoid severe obstruction
- contain enough visible surface area
- avoid unnecessary text
- avoid watermarks where licensing prohibits them

Images that do not meet minimum quality requirements should be reviewed
before inclusion.

---

# 8. Variation in the Dataset

The dataset should contain realistic variation.

Where possible, images should vary in:

- tomato size
- tomato shape
- orientation
- background
- lighting
- camera/device
- distance
- visible condition

This is intended to reduce over-dependence on one specific image
environment.

---

# 9. Avoiding Data Leakage

Data leakage must be avoided during dataset preparation.

If several images show the same physical tomato, those images should be
treated as a group.

Images from the same physical sample should not be distributed between
training and test sets.

For example:

Tomato A
- front image
- side image
- rear image

All three images should remain in the same dataset partition.

---

# 10. Dataset Splitting

The final dataset will be divided into:

- Training set
- Validation set
- Test set

The test set will remain isolated until final model evaluation.

The exact split ratio will be selected after the final dataset size is
known.

---

# 11. Class Balance

The project will attempt to maintain reasonable balance between:

- Fresh
- Early Decay
- Moderate Decay
- Advanced Decay

Class balance will be reported using actual image counts.

Images must not be duplicated merely to make class counts appear equal.

---

# 12. Image Augmentation

Data augmentation may be applied to the training set.

Possible techniques include:

- small rotations
- horizontal flipping where appropriate
- controlled brightness changes
- controlled zoom
- controlled cropping

Augmentation must preserve the original class.

Validation and test images must not be artificially augmented in a way
that compromises independent evaluation.

---

# 13. Dataset Quality Control

Before training, the dataset preparation process should check for:

- missing class directories
- unsupported image formats
- corrupted images
- duplicate filenames
- duplicate images
- extremely small images
- unreadable images
- incorrect class folders
- missing metadata

---

# 14. Metadata Integrity

Every image included in the research dataset should have a corresponding
metadata record.

The metadata file is:

data/processed/images/tomato_image_metadata.csv

An image should not be considered part of the final research dataset
until its metadata has been recorded.

---

# 15. Relationship With Existing Shelf-Life Research

The existing AGRO LIFE-AI tomato shelf-life research model uses numerical
measurements including:

- Day-4 Weight Loss
- Day-4 Titratable Acidity

The image dataset is a separate computer vision dataset.

Images should not be linked to the existing numerical research records
unless there is reliable evidence that they represent the same research
sample or a properly documented experimental relationship.

No artificial relationship should be created between unrelated images
and shelf-life measurements.

---

# 16. Computer Vision Objective

The initial computer vision objective is:

> To develop a research prototype capable of classifying visible tomato
> quality/decay conditions from images.

The initial classes are:

1. Fresh
2. Early Decay
3. Moderate Decay
4. Advanced Decay

---

# 17. Evaluation

The computer vision model may be evaluated using:

- accuracy
- precision
- recall
- F1-score
- confusion matrix

Performance should be reported for individual classes where appropriate.

---

# 18. Research Limitations

Potential limitations include:

- limited dataset size
- differences in camera quality
- lighting variation
- background variation
- tomato variety
- physical damage unrelated to decay
- difficulty distinguishing some decay stages
- differences between controlled and real-world photographs

These limitations must be acknowledged in the final report.

---

# 19. Food Safety Limitation

The computer vision model is intended for visible quality/decay
assessment.

It must not be presented as a laboratory test for:

- microbiological safety
- chemical contamination
- pesticide residues
- exact biochemical composition
- food safety certification

Visible appearance alone does not establish food safety.

---

# 20. Future Integration

After adequate validation, the computer vision module may be connected
to the broader AGRO LIFE-AI architecture.

Potential workflow:

Camera Capture
      ↓
Tomato Identification
      ↓
Visible Quality/Decay Classification
      ↓
Quality Assessment
      ↓
Appropriate Shelf-Life Model
      ↓
Estimated Remaining Shelf Life
      ↓
Farmer Decision Support
      ↓
Customer Decision Support

The integration will only be considered validated after appropriate
testing.

---

# 21. Dataset Approval Checklist

Before model training:

[ ] Image sources documented

[ ] Licences/permissions checked

[ ] Class definitions established

[ ] Images labelled

[ ] Image quality checked

[ ] Duplicate images checked

[ ] Related images grouped

[ ] Metadata completed

[ ] Dataset balance reviewed

[ ] Training/validation/test strategy defined

[ ] Test set isolated

[ ] Dataset preparation completed

---

# 22. Current Status

Current stage:

**Computer Vision Dataset Architecture and Labelling Protocol**

The image dataset has not yet been populated.

The next stage is controlled image collection and metadata registration.