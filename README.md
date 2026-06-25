# 🔋 EV Battery Health Prediction using MLflow & MLOps

![Python](https://img.shields.io/badge/Python-3.12-blue)
![MLflow](https://img.shields.io/badge/MLflow-Experiment%20Tracking-orange)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-RandomForest-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-REST%20API-success)

## 📌 Project Overview

Electric Vehicle (EV) batteries gradually degrade with usage, making **State of Health (SOH)** prediction essential for battery maintenance and lifecycle management.

This project implements a complete **Machine Learning Operations (MLOps)** pipeline that predicts battery SOH using a **Random Forest Regressor** and categorizes battery health into practical maintenance classes.

### Health Categories

| SOH (%) | Status |
|---------|---------|
| ≥ 85% | ✅ Healthy |
| 70–84% | ⚠️ Moderate |
| < 70% | ❌ End-of-Life |

The project demonstrates an end-to-end production-style ML workflow including:

- Data Generation
- Data Cleaning
- Schema Validation
- Train/Validation/Test Split
- Model Training
- Model Evaluation
- MLflow Experiment Tracking
- FastAPI Deployment
- Docker Containerization

---

# 🚀 Features

- End-to-end MLOps pipeline
- Synthetic EV battery dataset generation
- Automated preprocessing pipeline
- Random Forest Regression model
- SOH classification into battery health buckets
- MLflow experiment tracking
- Model artifact logging
- REST API using FastAPI
- Docker support for deployment
- Modular project architecture

---

# 📂 Project Structure

```text
EV-Battery-Health-Prediction/
│
├── artifacts/
│   ├── model.pkl
│   └── feature_names.pkl
│
├── configs/
│   ├── params.yaml
│   └── schema.yaml
│
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
│
├── notebooks/
│   └── demo.ipynb
│
├── src/
│   ├── data/
│   ├── models/
│   ├── pipelines/
│   ├── serve/
│   └── utils/
│
├── requirements.txt
├── Dockerfile
├── README.md
└── .gitignore
```

---

# 🛠 Tech Stack

### Programming

- Python 3.12

### Libraries

- Pandas
- NumPy
- Scikit-Learn
- MLflow
- FastAPI
- Uvicorn

### DevOps

- Docker

### Notebook

- Jupyter Notebook

---

# ⚙ Installation

## Clone Repository

```bash
git clone https://github.com/Aayushy7777/EV-Battery-Health-Prediction.git

cd EV-Battery-Health-Prediction
```

## Create Virtual Environment

Windows

```powershell
python -m venv .venv

.venv\Scripts\activate
```

Linux / macOS

```bash
python -m venv .venv

source .venv/bin/activate
```

## Install Requirements

```bash
pip install -r requirements.txt
```

---

# ▶ Run Training Pipeline

```bash
python -m src.pipelines.train_pipeline
```

Pipeline Steps

- Generate synthetic dataset
- Clean missing values
- Validate schema
- Split dataset
- Train Random Forest model
- Evaluate performance
- Save trained model
- Log experiments into MLflow

---

# 📊 MLflow Tracking

Launch MLflow UI

```bash
mlflow ui --backend-store-uri ./mlruns --port 5000
```

Open

```
http://127.0.0.1:5000
```

MLflow logs:

- Parameters
- Metrics
- Models
- Feature Importance
- Artifacts
- Experiment History

---

# 📈 Model Performance

### Regression Metrics

| Metric | Score |
|---------|--------|
| Train RMSE | ~0.79 |
| Validation RMSE | ~2.15 |
| Test RMSE | ~2.08 |

### Classification Accuracy

Battery Health Bucket Accuracy

**≈ 95%**

Classification Report

```
Healthy

Precision : 0.943
Recall    : 0.947
F1 Score  : 0.945

Moderate

Precision : 0.903
Recall    : 0.919
F1 Score  : 0.911

End-of-Life

Precision : 0.979
Recall    : 0.967
F1 Score  : 0.973
```

---

# 🌐 Running FastAPI

Train model first

```bash
python -m src.pipelines.train_pipeline
```

Start server

```bash
uvicorn src.serve.app:app --reload
```

API Endpoints

Root

```
http://127.0.0.1:8000
```

Swagger Documentation

```
http://127.0.0.1:8000/docs
```

Health Check

```
GET /health
```

Prediction

```
POST /predict
```

Example Request

```json
{
  "cycle_count": 500,
  "avg_temperature": 30,
  "charge_rate": 1.2,
  "discharge_rate": 1.0,
  "depth_of_discharge": 70,
  "internal_resistance": 0.08
}
```

Example Response

```json
{
  "predicted_soh": 87.35,
  "health_status": "Healthy"
}
```

---

# 🐳 Docker Deployment

Build Docker Image

```bash
docker build -t ev-battery .
```

Train model

```bash
python -m src.pipelines.train_pipeline
```

Run Container

```bash
docker run --rm -p 8000:8000 \
-v "$(pwd)/artifacts:/app/artifacts:ro" \
ev-battery
```

Health Check

```bash
curl http://127.0.0.1:8000/health
```

Prediction

```bash
curl -X POST http://127.0.0.1:8000/predict \
-H "Content-Type: application/json" \
-d '{"cycle_count":500,
"avg_temperature":30,
"charge_rate":1.2,
"discharge_rate":1.0,
"depth_of_discharge":70,
"internal_resistance":0.08}'
```

---

# 📒 Notebook

The notebook demonstrates

- Exploratory Data Analysis
- Battery degradation visualization
- Feature relationships
- Model testing
- Prediction examples

```
notebooks/demo.ipynb
```

---

# 🔮 Future Improvements

- Hyperparameter tuning using Optuna
- XGBoost and LightGBM comparison
- Battery Remaining Useful Life (RUL) prediction
- CI/CD using GitHub Actions
- Cloud deployment (AWS, Azure, GCP)
- Model Registry with MLflow
- Drift Detection and Monitoring

---

# 💼 Skills Demonstrated

- Machine Learning
- MLOps
- Experiment Tracking
- Model Deployment
- API Development
- Docker
- Regression
- Data Engineering
- Feature Engineering
- REST APIs

---

# 👨‍💻 Author

## **Aayush Yadav**

**B.Tech Artificial Intelligence & Data Science**  
Thakur College of Engineering and Technology

📧 Email: **aayu.sh7777@gmail.com**

🔗 GitHub: **https://github.com/Aayushy7777**

💼 LinkedIn: **https://www.linkedin.com/in/aayush-yadav-4119b724a/**

---

## ⭐ If you found this project useful, consider giving it a Star!
