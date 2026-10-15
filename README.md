# AGRO LIFE-AI
## Agricultural Intelligence and Shelf-Life Prediction System

### 1. Project Overview
AGRO LIFE-AI is an agricultural intelligence application developed to support produce management, quality assessment, shelf-life prediction, and marketplace activities.

### 2. Project Objectives
- Manage farmer and customer records.
- Record produce batches and quality measurements.
- Manage storage records and marketplace listings.
- Estimate produce shelf life using machine learning.
- Classify tomato images as Fresh or Rotten.
- Provide customer decision support.
- Support role-based access for administrators, farmers, and customers.

### 3. Main Modules
- Administrator: manages farmers, buyers, produce, predictions, marketplace listings, and customer assessments.
- Farmer: manages produce batches, quality records, storage, predictions, market listings, and buyers.
- Customer: supports customer registration, decision support, and camera-based quality assessment.

### 4. Technologies
- Python
- Streamlit
- SQLite
- Scikit-learn
- Pandas and NumPy
- Joblib
- Image-processing libraries
- Python unittest framework

### 5. Project Structure
- `app.py` - Main application entry point.
- `src/` - Application source code.
- `database/` - Database files.
- `models/` - Machine-learning models and metadata.
- `assets/` - Images and branding.
- `tests/` - Automated tests.
- `results/reports/` - Research and testing reports.
- `requirements.txt` - Python dependencies.

### 6. Installation
Open PowerShell in the project directory. Activate the existing virtual environment using:

`.\.venv\Scripts\Activate.ps1`

Install dependencies if required:

`python -m pip install -r requirements.txt`

### 7. Running the Application
Run:

`python -m streamlit run .\app.py --server.port 8503`

Open `http://localhost:8503` in your browser. If port 8503 is already serving the application, use the existing session.

### 8. Demonstration Accounts
- Administrator username: `admin`
- Farmer username: `farmer`
- Customer username: `customer`

Use the passwords configured for these accounts. Passwords are not included in this document.

### 9. Machine-Learning Research
The research prototype uses a Random Forest Regressor to estimate produce shelf life.

Selected features:
- Day 4 weight loss.
- Day 4 titratable acidity (TA).

Reported model configuration:
- Training observations: 48.
- Number of trees: 200.
- Random state: 42.
- Maximum tree depth: 4.
- Minimum samples per leaf: 2.

Model path: `models/final_research_shelf_life_model.joblib`

The research error-analysis report records:
- Mean Absolute Error (MAE): approximately 0.7954 days.
- Root Mean Squared Error (RMSE): approximately 1.6198 days.
- R-squared: approximately 0.3692.

A separate four-fold GroupKFold model-selection report records a mean MAE of approximately 0.7422 days. These are results from separate evaluations and should not be treated as results from the same evaluation run.

The dataset contains only 48 observations. Independent validation with additional data is required before practical deployment.

The tomato image classifier distinguishes Fresh and Rotten classes. It does not certify food safety.

### 10. Testing and Validation
Completed checks include:
- Python syntax checks across 26 Python files.
- Five prediction-workflow unit tests passed.
- Five prediction-system test scenarios passed.
- Database integrity check returned `ok`.
- No foreign-key violations were reported.
- Invalid numerical prediction inputs were tested.
- Administrator, farmer, and customer dashboards were checked.
- Login, logout, and role-based access were checked.
- Camera-based customer assessment was tested.

Not every marketplace operation has been exhaustively tested. Additional end-to-end testing is recommended.

### 11. Limitations and Future Improvements
- The research dataset is relatively small.
- Prediction performance varies across validation groups.
- Additional independent produce measurements are required.
- Image classification needs testing with more samples and lighting conditions.
- Marketplace operations require further end-to-end validation.
- The application is an academic research prototype, not a production-grade food-safety system.

### 12. Database and Backup
The primary database is located at `database/agro_life_ai.db`.

Keep backups of the source code, database, trained models, assets, and research reports. Do not distribute passwords or sensitive account information.

### 13. Conclusion
AGRO LIFE-AI demonstrates how software engineering, database management, and machine learning can support agricultural produce management and shelf-life research.

The application provides administrator, farmer, and customer modules alongside a research prediction workflow. Further independent model validation and comprehensive end-to-end testing are recommended before real-world deployment.
