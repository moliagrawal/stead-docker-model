# STEAD: Spatio-Temporal Efficient Anomaly Detection for Time and Compute Sensitive Applications((Dockerized))

[![PWC](https://img.shields.io/endpoint.svg?url=https://paperswithcode.com/badge/stead-spatio-temporal-efficient-anomaly-1/anomaly-detection-in-surveillance-videos-on)](https://paperswithcode.com/sota/anomaly-detection-in-surveillance-videos-on?p=stead-spatio-temporal-efficient-anomaly-1)
This repo is the official implementation of [STEAD: Spatio-Temporal Efficient Anomaly Detection for Time and Compute Sensitive Applications](https://arxiv.org/abs/2503.07942)  
This project implements the STEAD framework to detect abnormal events in videos using spatio-temporal feature extraction and temporal modeling, packaged with Docker support for reproducible deployment.

### Pretrained models available in the saved_models folder

This project is designed to work with video anomaly detection datasets such as:

UCF-Crime
Custom surveillance datasets

Dataset split files (e.g., train/test lists) are provided in .txt format.

[**UCF-Crime X3D Features on Google drive**](https://drive.google.com/file/d/1LBTddU2mKuWvpbFOrqylJrZQ4u-U-zxG/view?usp=sharing) 

**Extracted X3D Features for UCF-Crime dataset**

Feature extraction code also available for modification  

### Local Setup
#### Create virtual environment
        python -m venv venv
        source venv/bin/activate  # Linux / Mac
        venv\Scripts\activate     # Windows
#### Prepare the environment: 
        pip install -r requirements.txt
#### Train the model
        python train.py
#### Test the model
        python test.py
#### Run the model
        python inference.py

### Docker Setup
#### Build Docker Image
        docker build -t stead-anomaly-detection .
#### Run Container
        docker run -it --rm stead-anomaly-detection

### Pretrained Models
Pretrained model weights are not stored in this repository.
You can download them from:

HuggingFace Hub

Cloud storage (Google Drive / S3)

#### After downloading, place them inside:
        saved_models/

### Git & Model Artifacts Policy
This repository follows best ML engineering practices:

No .pkl, .pth, .pt files committed

Model artifacts are ignored via .gitignore

Code-only, reproducible, and clean repository

## Citation
    @misc{gao2025steadspatiotemporalefficientanomaly,
          title={STEAD: Spatio-Temporal Efficient Anomaly Detection for Time and Compute Sensitive Applications}, 
          author={Andrew Gao and Jun Liu},
          year={2025},
          eprint={2503.07942},
          archivePrefix={arXiv},
          primaryClass={cs.CV},
          url={https://arxiv.org/abs/2503.07942}, 
    }
