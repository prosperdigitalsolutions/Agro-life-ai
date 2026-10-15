# AGRO LIFE-AI

## Computer Vision Camera Assessment Module

**Project:** Design and Development of a Produce Decay and Shelf-Life Prediction System Using Data Analytics and Machine Learning
**Software:** AGRO LIFE-AI — Produce Decay & Shelf-Life Predictor
**Project Type:** BSc Computer Science Mini Project / Research Prototype
**Student:** Prosper Chungu Mwape
**Registration Number:** 24211351051
**Programme:** BSc Computer Science
**Institution:** DMI St. Eugene University
**Campus:** Chibombo Campus
**Guide:** Mr. Jeyakumar
**Department:** Department of Computer Science

---

# 1. Introduction

The AGRO LIFE-AI project includes a computer-vision component intended to provide visual assessment of agricultural produce. The purpose of this component is to investigate how captured produce images can be processed by a machine-learning classifier to identify visible uality categories.

The current implementation focuses specifically on tomatoes and uses the original Fresh and Rotten classes contained in the selected supporting computer-vision dataset.

The camera module has been integrated into the customer-facing interface of AGRO LIFE-AI. A customer can select Tomato, capture an image using the camera interface, submit the image for analysis, and receive a visual classification together with the model probability.

The current computer-vision component is a research prototype and is deliberately separated from the validated numerical shelf-life prediction model.

---

# 2. Objective of the Camera Module

The main objective of the camera assessment module is to provide a working prototype for tomato image capture and Fresh/Rotten visual classification.

The specific objectives are:

1. To provide a camera interface for customers.
2. To capture tomato images through the AGRO LIFE-AI dashboard.
3. To preprocess captured images into the format reuired by the trained classifier.
4. To classify tomato images as Fresh or Rotten.
5. To display the model probability associated with the classification.
6. To save the captured image for research record keeping.
7. To save a structured JSON prediction record.
8. To maintain clear research boundaries between visual classification, shelf-life prediction, and food-safety assessment.

---

# 3. Camera Assessment Workflow

The implemented camera workflow is:

```text
Customer
    ↓
Camera Assessment
    ↓
Select Tomato
    ↓
Capture Tomato Image
    ↓
Image Preprocessing
    ↓
Fresh/Rotten Computer-Vision Classifier
    ↓
Predicted Class
    ↓
Model Probability
    ↓
Managed Prediction Record
    ↓
Dashboard Result
```

The captured image is stored in the project prediction-results directory, while the classification information is stored as a structured JSON record.

---

# 4. Customer Interface

The camera assessment module is available through the customer interface of AGRO LIFE-AI.

The customer navigation includes:

* Dashboard
* Camera Assessment
* Prediction
* History
* About AGRO LIFE-AI

The Camera Assessment page allows the customer to select a produce type and capture an image.

At the current development stage, camera classification is restricted to Tomato because the available computer-vision classifier was trained specifically for the original tomato Fresh/Rotten dataset classes.

Other produce types remain under model development and are not passed through the tomato classifier.

---

# 5. Computer-Vision Model

The current classifier is a binary tomato image classification model.

The two supported classes are:

* Fresh
* Rotten

The model was developed using the selected Tomato_Dataset.v5 supporting dataset while preserving its original Fresh/Rotten labels.

No automatic conversion of Fresh/Rotten images into the proposed four decay stages was performed.

The four proposed AGRO LIFE-AI decay stages are:

1. Fresh
2. Early Decay
3. Moderate Decay
4. Advanced Decay

However, the current camera classifier does not implement these four classes.

---

# 6. Image Preprocessing

The camera image is converted to RGB format and resized to:

```text
64 × 64 pixels
```

The image pixel values are normalized by dividing them by 255.

The resulting image array is flattened into a numerical feature vector before being passed to the trained classifier.

The same general preprocessing approach used during classifier training is applied to camera images to maintain consistency between training and prediction.

---

# 7. Classification Algorithm

The current tomato Fresh/Rotten classifier uses:

**Logistic Regression**

The classifier was trained using the original Fresh/Rotten classes.

The previously evaluated binary classification experiment produced the following test-set results:

| Metric    | Result |
| --------- | -----: |
| Accuracy  | 88.00% |
| Precision | 90.20% |
| Recall    | 86.79% |
| F1-score  | 88.46% |

The test set contained 200 images.

These metrics describe the binary Fresh/Rotten image-classification experiment. They do not represent shelf-life prediction accuracy.

---

# 8. Live Camera Test

The integrated customer camera interface was tested using a captured tomato image.

The camera successfully captured and processed the image.

The resulting classification was:

```text
Produce: Tomato
Predicted Class: Fresh
Model Probability: 99.63%
Classification Type: Binary Fresh/Rotten
```

The dashboard displayed:

**Camera image analysed successfully.**

The result displayed:

**Visual Classification: Fresh**

with:

**Model Probability: 99.63%**

The model probability represents the classifier output associated with the predicted class. It should not be interpreted as a guarantee that the tomato is fresh or safe to consume.

---

# 9. Image Storage Verification

The captured camera images were successfully stored in:

```text
results/
└── predictions/
    └── computer_vision/
        └── camera_captures/
```

The verified latest image was:

```text
tomato_camera_20260920_181403_644341.jpg
```

The image file was successfully created and stored in the camera-captures directory.

This confirms that the camera module does not merely process the image temporarily; the captured image can also be retained as part of the research prototype's prediction evidence.

---

# 10. Managed Prediction Record

The camera module also creates a structured JSON prediction record.

The latest verified record was:

```text
tomato_camera_20260920_181403_644341_managed_prediction.json
```

The record contains information including:

* AGRO LIFE-AI system identifier
* Computer Vision Prediction module
* research prototype status
* prediction timestamp
* produce name
* image filename
* image path
* predicted class
* model probability
* classification type
* shelf-life prediction status
* food-safety certification status
* four-stage decay prediction status
* research limitation note

The latest record contained:

```text
Produce: Tomato
Predicted Class: Fresh
Model Probability: 0.9963
Classification Type: Binary Fresh/Rotten
Shelf-Life Prediction: False
Food-Safety Certification: False
Four-Stage Decay Prediction: False
```

The value `0.9963` corresponds to a displayed model probability of 99.63%.

---

# 11. Verification of Image-to-Record Relationship

The latest JSON record references:

```text
tomato_camera_20260920_181403_644341.jpg
```

The corresponding image file was independently confirmed to exist in:

```text
results/
predictions/
computer_vision/
camera_captures/
```

This confirms that the managed prediction record correctly references an existing captured image.

Therefore, the implemented evidence chain is:

```text
Captured Image
      ↓
Stored JPG File
      ↓
Computer-Vision Classification
      ↓
Prediction Record
      ↓
Managed JSON File
```

---

# 12. Research Integrity

The camera module deliberately preserves the original dataset classes.

The current system does not automatically transform Fresh/Rotten labels into the proposed four-stage decay classes.

This decision prevents unsupported assumptions about the relationship between binary visual labels and progressive decay stages.

The current module therefore remains a binary visual-classification experiment.

A future four-stage decay classifier will reuire an appropriately labelled dataset containing defensible definitions for Fresh, Early Decay, Moderate Decay, and Advanced Decay, together with suitable validation.

---

# 13. Relationship with the Shelf-Life Prediction Model

The camera classifier and numerical shelf-life model are currently separate components.

The validated shelf-life model uses research-based uality measurements, specifically:

* Day-4 Weight Loss
* Day-4 Titratable Acidity

The shelf-life model predicts estimated total shelf life in days.

The camera classifier, on the other hand, analyses a tomato image and produces a Fresh/Rotten visual classification.

Therefore:

```text
Numerical Research Data
        ↓
Weight Loss + Titratable Acidity
        ↓
Shelf-Life Machine Learning Model
        ↓
Estimated Shelf Life
```

is separate from:

```text
Camera Image
        ↓
Tomato Computer-Vision Classifier
        ↓
Fresh / Rotten
```

The current camera module does not supply an image-derived shelf-life prediction.

---

# 14. Food-Safety Limitation

The computer-vision classification result must not be interpreted as a food-safety certification.

A classification of Fresh does not guarantee that produce is safe to consume.

Similarly, a Rotten classification represents the visual classifier's output and should not be treated as a complete microbiological or laboratory assessment.

AGRO LIFE-AI is therefore presented as a research-based decision-support prototype rather than a food-safety certification system.

---

# 15. Current Capabilities

The implemented camera module currently provides:

* Customer camera access
* Tomato selection
* Camera image capture
* Image preprocessing
* Fresh/Rotten classification
* Model probability display
* Captured-image storage
* Managed JSON prediction records
* Dashboard result display
* Research limitation messaging

---

# 16. Current Limitations

The current camera module has several limitations:

1. It supports Tomato only.
2. It uses binary Fresh/Rotten classification.
3. It does not classify four progressive decay stages.
4. It does not predict shelf life directly from photographs.
5. It does not estimate remaining shelf life from photographs.
6. It does not certify food safety.
7. The supporting dataset does not provide a validated mapping to the four proposed AGRO LIFE-AI decay stages.
8. The current classifier reuires further validation using independent images captured under realistic conditions.
9. The camera classifier and numerical shelf-life model have not yet been jointly validated as one image-to-shelf-life system.

---

# 17. Future Development

Future versions of AGRO LIFE-AI may extend the camera component through:

```text
Camera Capture
      ↓
Produce Identification
      ↓
Image Preprocessing
      ↓
Visual uality Assessment
      ↓
Decay-Stage Classification
      ↓
Produce-Specific Shelf-Life Model
      ↓
Estimated Remaining Shelf Life
      ↓
Farmer and Customer Decision Support
```

Future research may include:

* four-stage decay classification
* additional produce types
* larger image datasets
* independently captured images
* mobile camera integration
* advanced computer-vision models
* image-uality assessment
* integration of visual features with numerical uality measurements
* produce-specific shelf-life models
* independent external validation

These extensions will only be considered validated after appropriate datasets, model development, and testing have been completed.

---

# 18. Step 14 Completion Status

**STEP 14 — CUSTOMER CAMERA ASSESSMENT MODULE**

**Status: COMPLETED**

The camera assessment module was successfully integrated into the AGRO LIFE-AI customer dashboard.

The system successfully:

```text
Captured a tomato image                    ✓
Processed the image                       ✓
Classified the image                      ✓
Produced Fresh/Rotten result              ✓
Displayed model probability               ✓
Saved the captured image                  ✓
Created a managed JSON record             ✓
Linked the record to the captured image   ✓
Displayed the result to the customer      ✓
Preserved research limitations             ✓
```

### Verified Test Result

```text
Produce: Tomato
Visual Classification: Fresh
Model Probability: 99.63%
Classification Type: Binary Fresh/Rotten
```

### Final Research Statement

The completed camera module demonstrates the feasibility of integrating computer vision into the AGRO LIFE-AI research prototype for tomato Fresh/Rotten visual classification. At the current stage, the module is a separate visual-uality component and does not constitute image-based shelf-life prediction, four-stage decay classification, or food-safety certification.

The results provide a foundation for future research into the integration of computer vision, produce-uality assessment, and produce-specific shelf-life prediction.
