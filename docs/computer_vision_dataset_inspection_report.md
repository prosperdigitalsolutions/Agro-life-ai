\# AGRO LIFE-AI

\## Computer Vision Dataset Inspection Report



\### 1. Dataset Identification



Dataset Name:

Tomato\_Dataset V5



Provider:

Roboflow user dataset



Source:

https://universe.roboflow.com/arafatislam1811-gmail-com/tomato\_dataset-ku7jj



License:

CC BY 4.0



Produce:

Tomato



Dataset Type:

YOLO object-detection dataset



\### 2. Purpose in AGRO LIFE-AI



The dataset is being investigated as an external supporting dataset

for the computer-vision component of the AGRO LIFE-AI research

prototype.



It is not used as a direct source of shelf-life targets because the

dataset does not contain the verified research measurements used by

the current AGRO LIFE-AI shelf-life prediction model.



\### 3. Verified Annotation Format



The extracted dataset contains YOLO-format object annotations.



The annotation structure follows:



class\_id x\_center y\_center width height



The coordinate values are normalized relative to image dimensions.



\### 4. Verified Classes



The extracted annotation files were inspected to determine the

active class IDs.



Class 0:

Fresh



Class 1:

Rotten



Class 2:

No annotated objects were found.



\### 5. Annotation Object Counts



Class 0 – Fresh:

817 annotated objects



Class 1 – Rotten:

3,409 annotated objects



Class 2:

0 annotated objects



These values represent annotated objects/bounding boxes and must not

be interpreted as the number of independent tomato samples.



\### 6. Verified Test Split



The test split contains:



Total images: 200



Fresh images: 94



Rotten images: 106



\### 7. Important Dataset Limitation



The external dataset provides Fresh and Rotten visual categories.



It does not provide validated intermediate decay stages corresponding

to:



1\. Fresh

2\. Early Decay

3\. Moderate Decay

4\. Advanced Decay



Therefore, Rotten images must not automatically be relabelled into

Early Decay, Moderate Decay, and Advanced Decay.



Such relabelling would introduce unsupported labels and could reduce

the scientific validity of the computer-vision research.



\### 8. Relationship with the Current Shelf-Life Model



The current validated AGRO LIFE-AI shelf-life model uses:



\- Day-4 Weight Loss

\- Day-4 Titratable Acidity



to estimate total shelf life.



The Roboflow dataset does not replace these research measurements.



Therefore, the external image dataset should be treated as supporting

computer-vision data rather than as a replacement for the validated

shelf-life research dataset.



\### 9. Research Integrity



The dataset is retained in its original form.



Original annotations should not be modified.



The original ZIP archive is preserved as a source copy.



Any future preprocessing or transformation must be performed on a

separate working copy.



\### 10. Current Status



Dataset downloaded:

YES



Dataset extracted:

YES



YOLO annotations verified:

YES



Fresh class verified:

YES



Rotten class verified:

YES



Four-stage decay labels available:

NO



Direct shelf-life target available:

NO



Suitable for immediate four-stage decay training:

NO



Suitable as supporting computer-vision research data:

YES



\### 11. Future Development



Future AGRO LIFE-AI computer-vision development should use a properly

labelled dataset capable of distinguishing meaningful stages of

produce deterioration.



Additional research images should be collected or obtained from

legitimate sources and documented with their source, licence,

capture conditions, and labelling criteria.



Future validated models may combine visual quality information with

appropriate produce-specific shelf-life models.

