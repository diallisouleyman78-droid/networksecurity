# 🔐 Network Security - Phishing Detection System

An end-to-end MLOps pipeline for detecting phishing websites using machine learning. The system ingests network/URL features from MongoDB, trains classification models, and serves real-time predictions via a REST API.

![Python](https://img.shields.io/badge/Python-3.10-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green.svg)
![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-orange.svg)
![MLflow](https://img.shields.io/badge/MLflow-2.8+-purple.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#-features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Dataset](#dataset)
- [Deployment](#deployment)
- [CI/CD Pipeline](#cicd-pipeline)

## 📖 Overview

This project implements a production-ready machine learning system for detecting phishing websites. It uses 31 URL/network-based features to classify websites as legitimate or malicious, with a complete MLOps pipeline including experiment tracking, model versioning, and automated deployment.

### The Problem
Phishing attacks are one of the most common and costly cybersecurity threats. Traditional rule-based detection systems fail to catch novel attack patterns.

### The Solution
An ML-powered system that learns from historical phishing data and continuously improves its detection capabilities through automated retraining and data drift monitoring.

## ✨ Features

- **Complete ML Pipeline**: Data ingestion → Validation → Transformation → Training → Evaluation
- **Model Comparison**: Evaluates 6 classifiers (Logistic Regression, Random Forest, Gradient Boosting, AdaBoost, Decision Tree, KNN)
- **Experiment Tracking**: MLflow integration with DagsHub for remote logging
- **Data Validation**: Schema validation and data drift detection using Kolmogorov-Smirnov test
- **REST API**: FastAPI-based prediction endpoint with batch CSV support
- **Containerized Deployment**: Docker-ready with GitHub Actions CI/CD
- **Artifact Management**: S3 sync for model backup and versioning

## Tech Stack

| Category | Technologies |
|----------|--------------|
| **Language** | Python 3.10 |
| **ML Framework** | scikit-learn |
| **Experiment Tracking** | MLflow, DagsHub |
| **Database** | MongoDB |
| **API Framework** | FastAPI, Uvicorn |
| **Infrastructure** | Docker, AWS (ECR, S3), GitHub Actions |
| **Data Processing** | Pandas, NumPy |

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           TRAINING PIPELINE                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [MongoDB] ──> [DataIngestion] ──> [DataValidation] ──> [DataTransformation]│
│                                                                             │
│                                           │                                 │
│                                           v                                 │
│                                    [ModelTrainer]                           │
│                                    (6 classifiers)                          │
│                                           │                                 │
│                                           v                                 │
│                              [Artifacts + S3 Sync]                          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           API ENDPOINTS                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  GET /train ──> Triggers full training pipeline                            │
│  POST /predict ──> Batch prediction from CSV upload                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
NetworkSecurity/
├── app.py                          # FastAPI application entry point
├── main.py                         # CLI training script
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker container configuration
├── setup.py                        # Package installation
│
├── networksecurity/
│   ├── components/                 # ML pipeline components
│   │   ├── data_ingestion.py       # MongoDB data loading
│   │   ├── data_validation.py      # Schema & drift validation
│   │   ├── data_transformation.py  # KNN imputation
│   │   └── model_trainer.py        # Model training & selection
│   │
│   ├── pipeline/
│   │   └── training_pipeline.py    # Pipeline orchestration
│   │
│   ├── entity/
│   │   ├── config_entity.py        # Configuration dataclasses
│   │   └── artifact_entity.py      # Artifact dataclasses
│   │
│   ├── utils/
│   │   ├── main_utils/            # I/O utilities
│   │   └── ml_utils/              # ML utilities & metrics
│   │
│   ├── cloud/
│   │   └── s3_syncer.py           # AWS S3 operations
│   │
│   ├── constants/                  # Configuration constants
│   ├── exception/                  # Custom exceptions
│   ├── logging/                    # Logging configuration
│   └── data_schema/
│       └── schema.yaml             # Data schema definition
│
├── templates/                      # HTML templates for API responses
├── final_model/                    # Production model artifacts
├── prediction_output/              # Batch prediction outputs
├── logs/                           # Application logs
├── Artifact/                       # Pipeline artifacts
└── Network_Data/                   # Dataset files
```

## Getting Started

### Prerequisites

- Python 3.10+
- MongoDB instance (local or Atlas)
- AWS account (for S3 sync)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/diallisouleyman78/networksecurity.git
cd networksecurity
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials:
# - MONGO_DB_URL
# - MLFLOW_TRACKING_URI
# - AWS credentials
```

5. **Push data to MongoDB**
```bash
python push_data.py
```

### Running the Application

**Start the API server:**
```bash
python app.py
# Runs on http://localhost:8000
```

**Or trigger training via CLI:**
```bash
python main.py
```

## Usage

### API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Train the Model

```bash
# Via API
curl -X GET http://localhost:8000/train

# Or via CLI
python main.py
```

### Make Predictions

```bash
curl -X POST "http://localhost:8000/predict" \
  -F "file=@your_data.csv"
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Redirects to API documentation |
| `/train` | GET | Triggers the full ML training pipeline |
| `/predict` | POST | Batch prediction from CSV file upload |

## Dataset

The model uses 31 features extracted from URLs and network characteristics:

### URL-Based Features
- `having_IP_Address` - IP address presence
- `URL_Length` - URL character count
- `Shortining_Service` - Short URL service usage
- `having_At_Symbol` - @ symbol presence
- `Prefix_Suffix` - Hyphen in domain

### SSL/HTTPS Features
- `SSLfinal_State` - SSL certificate state
- `HTTPS_token` - HTTPS in subdomain

### Domain Features
- `Domain_registeration_length` - Domain age
- `age_of_domain` - Years since registration
- `DNSRecord` - DNS record existence

### Content Features
- `Request_URL` - External resource requests
- `URL_of_Anchor` - Anchor URL patterns
- `Links_in_tags` - Link distribution
- `Iframe` - Iframe presence

### External Features
- `Page_Rank` - Google PageRank
- `Google_Index` - Google indexing status
- `web_traffic` - Site traffic rank

**Target Variable:** `Result` (1 = legitimate, -1 = phishing)

## Deployment

### Docker

```bash
# Build the image
docker build -t networksecurity:latest .

# Run the container
docker run -p 8000:8000 \
  --env-file .env \
  networksecurity:latest
```

### AWS (ECR)

The project includes GitHub Actions workflow for:
1. Building and pushing to Amazon ECR
2. Pulling on self-hosted runner
3. Zero-downtime deployment

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/main.yml`) includes:

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  Lint/Test  │───>│  Build/Push │───>│   Deploy    │
│   (Ubuntu)  │    │   (ECR)     │    │  (Runner)   │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Model Training Details

### Classifiers Evaluated
- Logistic Regression
- Random Forest
- Gradient Boosting
- AdaBoost
- Decision Tree
- K-Nearest Neighbors

### Hyperparameter Tuning
Grid search over key parameters:
- `n_estimators`: [8, 16, 32, 64, 128, 256]
- `learning_rate`: [0.1, 0.01, 0.05]
- `n_neighbors`: [5, 7, 9, 11, 13, 15]
- `criterion`: ['gini', 'entropy', 'log_loss']

### Model Selection
Best model selected based on **F1 Score** from test set evaluation.

## Experiment Tracking

Access MLflow experiments at your configured DagsHub repository. Each run logs:
- Model parameters
- Training metrics (F1, Precision, Recall)
- Model artifacts

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License.

## Author

**Diallo Souleyman**

---

⭐ Star this repo if you found it useful!
