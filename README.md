# Chemical Equipment Parameter Visualizer

A comprehensive hybrid **Web + Desktop** application designed for uploading, analyzing, and visualizing chemical equipment data. This project provides a seamless experience for engineers and researchers to manage equipment parameters, generate reports, and visualize trends through interactive charts.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB.svg)](https://reactjs.org/)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15-41CD52.svg)](https://www.riverbankcomputing.com/software/pyqt/)

## 🚀 Overview

The system consists of three main components:
1.  **Backend (Django REST Framework)**: Manages data storage, CSV processing, and PDF report generation.
2.  **Web Frontend (React)**: A modern, glassmorphism-inspired dashboard for browser-based data analysis.
3.  **Desktop Frontend (PyQt5)**: A native desktop application with high-performance visualization using Matplotlib.

## ✨ Key Features

*   **Smart CSV Upload**: Drag-and-drop interface with automatic validation of equipment parameters.
*   **Real-time Analytics**: Instant calculation of averages (flowrate, pressure, temperature) and type distribution.
*   **Dual Visualization**: High-quality interactive charts using Chart.js (Web) and Matplotlib (Desktop).
*   **PDF Report Generation**: Download detailed professional reports with embedded visualizations.
*   **Automatic History**: Tracks the last 5 datasets for quick access and comparison.
*   **Secure Auth**: Token-based authentication across all interfaces.

## 🛠️ Quick Start Guide

Follow these steps to get the project running on your local machine.

### 1. Prerequisites
*   Python 3.10+
*   Node.js 18+
*   Git

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup Database
python manage.py migrate
python manage.py createsuperuser  # Create your admin account

# Run Server
python manage.py runserver
```
*Backend runs at: `http://localhost:8000`*

### 3. Web Frontend Setup
```bash
# Navigate to web-frontend directory
cd ../web-frontend

# Install and start
npm install
npm start
```
*Web app opens at: `http://localhost:3000`*

### 4. Desktop Frontend Setup
```bash
# Navigate to desktop-frontend directory
cd ../desktop-frontend

# Use the same venv or create a new one
# Install PyQt5 related dependencies
pip install -r requirements.txt

# Launch App
python main.py
```

## 📁 Project Structure

```text
FOSSEE Project/
├── backend/            # Django REST API (Models, Views, Reports)
├── web-frontend/       # React Application (UI/UX, Dashboards)
├── desktop-frontend/   # PyQt5 Application (Native Visualization)
└── sample_data.csv     # Use this for testing the upload
```

## 📊 API Summary

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/login/` | Get Auth Token |
| `POST` | `/api/upload/` | Upload CSV |
| `GET` | `/api/datasets/` | List History |
| `GET` | `/api/summary/<id>/` | Get Analytics |
| `GET` | `/api/report/<id>/` | Download PDF |

---

## 👤 Author
**Nihal Jagdale**  

