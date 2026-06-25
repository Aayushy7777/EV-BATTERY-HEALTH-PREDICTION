# 🚀 Setup & Demo Guide

Complete guide to set up, train, and deploy the EV Battery Health Prediction system.

---

## ✅ Prerequisites

- Python 3.12+
- Docker (optional, for containerization)
- Git

---

## 📦 Installation & Setup

### Step 1: Create Virtual Environment

```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# macOS/Linux
python -m venv .venv
source .venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🎯 Full Workflow

### Step 1: Run Training Pipeline

Generates synthetic data, cleans it, trains a RandomForest model, and logs everything to MLflow.

```bash
python -m src.pipelines.train_pipeline
```

**Output:**
- ✅ Trained model: `artifacts/random_forest.joblib`
- ✅ Feature names: `artifacts/feature_names.txt`
- ✅ MLflow experiment tracking: `mlflow.db`

---

## 📊 View Results

### Option A: Custom MLflow Dashboard

```bash
python mlflow_viewer.py
```

Then open **http://127.0.0.1:5000** in your browser.

**Features:**
- 📈 Training metrics visualization
- 📁 Experiment tracking
- 🏷️ Run parameters & artifacts
- 📊 Real-time performance metrics

### Option B: Official MLflow UI

```bash
mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5000
```

---

## 🔮 Generate Model Evaluation Report

```bash
python generate_report.py
```

**Generates:**
- 📊 Regression metrics (RMSE, MAE, R²)
- 🎯 Classification performance (per health bucket)
- 🎚️ Feature importance ranking
- 📉 Error analysis
- 📄 JSON report: `model_evaluation_report.json`

---

## 🌐 Serve Predictions via API

### Start FastAPI Server

```bash
python -m uvicorn src.serve.app:app --reload --port 8000
```

Open **http://127.0.0.1:8000/docs** for interactive API documentation.

### Endpoints

#### 1. Health Check
```bash
curl http://127.0.0.1:8000/health
```

#### 2. Make Prediction
```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "cycle_count": 1000,
    "avg_temperature": 35.5,
    "charge_rate": 2.5,
    "discharge_rate": 2.0,
    "depth_of_discharge": 75.0,
    "internal_resistance": 0.015
  }'
```

**Response:**
```json
{
  "soh": 82.3,
  "bucket": "Moderate",
  "input": {...}
}
```

#### 3. Interactive Docs
Open **http://127.0.0.1:8000/docs** to try all endpoints interactively.

---

## 🧪 Test API Predictions

Run the automated test suite:

```bash
python test_api.py
```

**Tests:**
- ✅ API health check
- ✅ Model loading verification
- ✅ Sample predictions (healthy, moderate, degraded batteries)
- ✅ Error handling

---

## 🐳 Docker Containerization

### Build Docker Image

```bash
python docker_build.py
```

Or manually:
```bash
docker build -t ev-battery-prediction:latest .
```

### Run Container

```bash
docker run -d \
  --name ev-battery-api \
  -p 8000:8000 \
  ev-battery-prediction:latest
```

### Verify Container

```bash
# Check logs
docker logs ev-battery-api

# Test API
curl http://localhost:8000/health

# Stop container
docker stop ev-battery-api
```

### Push to Registry

```bash
# Tag for your registry
docker tag ev-battery-prediction:latest your-username/ev-battery-prediction:latest

# Push to Docker Hub
docker push your-username/ev-battery-prediction:latest
```

---

## 📋 Project Structure

```
.
├── artifacts/                    # Trained models & features
│   ├── random_forest.joblib
│   └── feature_names.txt
├── configs/                      # Configuration files
│   ├── params.yaml              # Model hyperparameters
│   └── schema.yaml              # Data schema
├── data/
│   ├── raw/                     # Raw synthetic data
│   ├── interim/                 # Cleaned data
│   └── processed/               # Train/val/test splits
├── src/
│   ├── data/                    # Data generation, cleaning, validation
│   │   ├── make_synthetic.py
│   │   ├── clean.py
│   │   ├── check.py
│   │   └── split.py
│   ├── models/                  # Model training & evaluation
│   │   ├── train_regressor.py
│   │   ├── evaluate.py
│   │   └── postprocess.py
│   ├── pipelines/               # End-to-end pipeline
│   │   └── train_pipeline.py
│   ├── serve/                   # FastAPI application
│   │   └── app.py
│   └── utils/                   # Utilities
│       └── seed.py
├── mlflow_viewer.py             # Custom MLflow dashboard
├── test_api.py                  # API test suite
├── generate_report.py           # Model evaluation report
├── docker_build.py              # Docker build script
├── Dockerfile                   # Container definition
├── requirements.txt             # Python dependencies
└── README.md                    # Project documentation
```

---

## 🔧 Configuration

### Model Parameters (`configs/params.yaml`)

```yaml
model:
  n_estimators: 300        # Number of trees
  max_depth: null          # Max tree depth (None = unlimited)
  n_jobs: -1               # Use all CPU cores
  
random_seed: 42            # Reproducibility
```

### Data Schema (`configs/schema.yaml`)

Defines expected data columns and types.

---

## 📈 Model Performance

### Training Results
- **Train RMSE**: 0.793% | **Train R²**: 0.998
- **Val RMSE**: 2.151% | **Val R²**: 0.983
- **Test RMSE**: 2.081% | **Test R²**: 0.984

### Classification Performance (Health Buckets)
- **Healthy (≥85%)**: 94.3% precision, 94.7% recall
- **Moderate (70-84%)**: 90.3% precision, 91.9% recall
- **End-of-Life (<70%)**: 97.9% precision, 96.7% recall
- **Overall Accuracy**: 94.9%

---

## 🚀 Deployment Options

### 1. Docker (Recommended for Production)
```bash
docker run -p 8000:8000 ev-battery-prediction:latest
```

### 2. Kubernetes
Use the Docker image with Kubernetes deployments, services, and ingress.

### 3. AWS Lambda
Package with Mangum ASGI adapter for serverless deployment.

### 4. Heroku
```bash
heroku create your-app-name
docker push registry.heroku.com/your-app-name/web
```

### 5. Google Cloud Run
```bash
gcloud run deploy ev-battery-prediction \
  --image gcr.io/your-project/ev-battery-prediction \
  --port 8000
```

---

## 🐛 Troubleshooting

### API Connection Issues
```bash
# Verify server is running
netstat -an | grep 8000

# Check firewall
# Allow port 8000 in Windows Firewall
```

### MLflow Database Locked
```bash
# Remove lock file
rm -f mlflow.db
# Re-run training pipeline
python -m src.pipelines.train_pipeline
```

### Docker Build Fails
```bash
# Clear Docker cache
docker system prune

# Rebuild
docker build -t ev-battery-prediction:latest .
```

---

## 📚 Additional Resources

- **MLflow Docs**: https://mlflow.org/docs/
- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **Scikit-Learn**: https://scikit-learn.org/
- **Docker Docs**: https://docs.docker.com/

---

## 📝 Quick Commands Cheat Sheet

```bash
# Training
python -m src.pipelines.train_pipeline

# View Dashboard
python mlflow_viewer.py

# Start API
python -m uvicorn src.serve.app:app --reload

# Test API
python test_api.py

# Generate Report
python generate_report.py

# Docker Build
python docker_build.py

# Deactivate venv
deactivate
```

---

## 🎯 Next Steps

1. ✅ Run training pipeline
2. ✅ View metrics in MLflow dashboard
3. ✅ Test API with predictions
4. ✅ Generate evaluation report
5. ✅ Build Docker container
6. ✅ Deploy to production

---

**Happy forecasting! 🔋⚡**
