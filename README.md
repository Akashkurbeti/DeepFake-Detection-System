# DeepFake-Detection-System
# Deepfake Detection System

A production-grade Deepfake Detection System designed to identify AI-generated and manipulated facial images using **EfficientNet-B3** and **Elastic Weight Consolidation (EWC) Continual Learning**. The system uses progressive multi-phase training to improve generalization across different types of image manipulations and provides a real-time web interface using Streamlit.

---

## Project Overview

Deepfake technology has rapidly evolved and can generate highly realistic fake images and videos. These manipulated contents can be used for:

- Fake news spreading
- Identity theft
- Financial fraud
- Social media misinformation
- Privacy and security attacks

This project aims to build an intelligent detection system capable of distinguishing authentic and manipulated images with high accuracy.

---

## Features

- EfficientNet-B3 based deep learning model
- Elastic Weight Consolidation (EWC) continual learning
- Multi-phase training pipeline
- Real-time image analysis
- Streamlit web interface
- Confidence score visualization
- Risk level analysis
- Grad-CAM heatmap visualization
- Session history tracking
- Support for multiple deepfake datasets

---

## Technology Stack

### Frontend
- Streamlit

### Backend
- Python 3.10

### Deep Learning Framework
- PyTorch 2.x

### Libraries
- TorchVision
- NumPy
- Pandas
- OpenCV
- Matplotlib

### Hardware
- NVIDIA RTX 5060 (8GB VRAM)

---

## System Architecture

Input Image

↓  

Image Preprocessing

↓  

EfficientNet-B3 Model

↓  

Feature Extraction

↓  

Sigmoid Classification

↓  

Real/Fake Prediction

↓  

Result Visualization

---

## Dataset Information

Datasets used:

- FaceForensics++
- StyleGAN
- FaceShifter
- FFHQ-FaceFusion

Dataset statistics:

| Category | Count |
|-----------|--------|
| Real Images | 41,000 |
| Fake Images | 61,800 |
| Total Images | 102,800+ |

---

## Model Details

### EfficientNet-B3 Configuration

- Total Parameters: 10.7 Million
- Input Size: 224 × 224
- Output Layer: Single Sigmoid Output
- Model Size: 42 MB

### Training Configuration

| Parameter | Value |
|------------|--------|
| Epochs | 5 |
| Batch Size | 48 |
| Learning Rate | 0.0002 |
| Optimizer | Adam |
| Loss Function | BCEWithLogitsLoss |
| Weight Decay | 1e-5 |

---

## Project Structure
