# Processor Recommendation & Analysis Engine: An End-to-End Machine Learning Project

[![Live App](https://img.shields.io/badge/Live_App-Open-brightgreen?style=flat-square)](https://processor-recom-engine.onrender.com)

This project demonstrates my ability to build and deploy a full-stack, end-to-end machine learning application. It's a decision-support tool that uses both rule-based filtering and ML-powered predictions to help engineers and product teams analyze and select processors for smart devices.

This repository showcases the entire lifecycle: from data cleaning and model training in a notebook to building a robust Flask API, containerizing with Docker, and deploying a scalable web service to the cloud.

---

_**Note:** This application is hosted on Render's free tier. The server may spin down after 15 minutes of inactivity. Please allow 3-6 mins for the app to "wake up" on your first visit._

## The ML Pipeline & Technical Deep Dive

This project was more than just training a model; it was about building a reliable and production-ready system. Here's a breakdown of the key technical stages:

### 1. Data Processing & Feature Engineering
-   **Data Source:** The core dataset was a manually curated Excel file (`Processors.xlsx`) containing specifications for numerous processors.
-   **Data Cleaning:** A key challenge was handling inconsistent string formats. I wrote functions to parse numeric values (e.g., number of cores) and boolean flags from text fields using regex and string manipulation in Pandas.
-   **Feature Engineering:** I created new, more useful features to improve model performance, such as `has_5g` and `has_wifi_6_or_higher`, by parsing unstructured text columns describing wireless capabilities.

### 2. Model Training & Selection
-   **Problem Framing:** The prediction task was split into two distinct ML problems:
    1.  **Function Prediction:** A **multi-class classification** problem to predict the processor's primary role (e.g., "Application Processor with Modem").
    2.  **Wireless Capabilities:** A **multi-label classification** problem to predict a set of supported features (e.g., "5G Support," "Wi-Fi 6+," "USB 3.0+").
-   **Model Choice:** I used Scikit-learn's `RandomForestClassifier` for the function prediction due to its robustness with tabular data. For the wireless features, a `MultiOutputClassifier` wrapping a base estimator was used to handle the multi-label nature of the output.
-   **Artifacts:** The trained models and the `LabelEncoder` for the function classes were serialized using `joblib` for easy loading in the Flask application. The entire process is documented in the `notebooks/` directory.

### 3. Deployment & MLOps
Putting the model into production was a critical phase that required solving real-world challenges:
-   **API Development:** I built a Flask application with a clean architecture (services, routes, blueprints) to serve the model's predictions.
-   **Containerization:** The entire application, including the Python environment and all dependencies, was containerized using **Docker**. This ensures a consistent, reproducible environment from local testing to cloud deployment.
-   **Production Server:** I used **Gunicorn** as the WSGI server, a standard for production Flask applications.
-   **Performance & Memory Optimization:** To handle multiple concurrent users efficiently on a resource-constrained platform (Render's free tier), I configured Gunicorn with multiple workers and used the `--preload` flag. This loads the models into memory once in the master process, preventing each worker from creating a separate, memory-intensive copy.
-   **Static Asset Serving:** I solved the common production issue of serving static files (CSS) by integrating the **WhiteNoise** library, which allows Gunicorn to efficiently handle these requests without needing a separate web server like Nginx.

---

## Technology Stack

| Category | Technology |
| :--- | :--- |
| **Backend** | ![Python](https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python&logoColor=white) ![Flask](https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white) |
| **Machine Learning** | ![Scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=flat-square&logo=scikit-learn&logoColor=white) ![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=flat-square&logo=pandas&logoColor=white) ![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=flat-square&logo=Jupyter&logoColor=white) |
| **Frontend** | ![HTML5](https://img.shields.io/badge/html5-%23E34F26.svg?style=flat-square&logo=html5&logoColor=white) ![CSS3](https://img.shields.io/badge/css3-%231572B6.svg?style=flat-square&logo=css3&logoColor=white) |
| **Deployment** | ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white) ![Gunicorn](https://img.shields.io/badge/Gunicorn-499848?style=flat-square&logo=gunicorn&logoColor=white) ![Render](https://img.shields.io/badge/Render-46E3B7?style=flat-square&logo=render&logoColor=white) |

---

<details>
<summary><strong>Click to view Application Features, Screenshots, & Setup Instructions</strong></summary>

### Features
This application has two main components:

1.  **Recommendation Engine:** Rule-based filtering of processors based on user-defined technical criteria.
2.  **Processor Analyzer (ML-Powered):** AI-powered predictions for a processor's function and wireless capabilities based on its specifications.

### Application Screenshots
| Recommendation Engine | Recommendation Results | Processor Analyzer |
| :---: | :---: | :---: |
| ![Screenshot 1](app_ss_1.png) | ![Screenshot 2](app_ss_2.png) | ![Screenshot 3](app_ss_3.png) |

### Project Structure
```
├── processor-recommendation-engine/
│   ├── app/                # Main Flask application
│   │   ├── static/         # CSS and other static assets
│   │   ├── templates/      # HTML templates
│   │   ├── __init__.py     # Application factory
│   │   ├── routes.py       # Application routes
│   │   └── services.py     # Business logic and data processing
│   ├── data/               # Raw dataset
│   ├── models/             # Trained ML models
│   ├── notebooks/          # Jupyter notebooks for analysis and model training
│   ├── config.py           # Configuration settings
│   ├── requirements.txt    # Python dependencies
│   ├── run.py              # Application entry point
│   └── Dockerfile          # Instructions for building the container image
└── ...
```

### Running the Application
This project can be run locally for development or with Docker to replicate the production environment.

#### Option 1: Running Locally (for Development)
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/MdEhsanulHaqueKanan/processor-recommendation-engine.git
    cd processor-recommendation-engine
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows:
    .\venv\Scripts\activate
    # On macOS/Linux:
    source venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the Flask development server:**
    ```bash
    python run.py
    ```
5.  Open your browser to `http://127.0.0.1:5000`.

#### Option 2: Running with Docker (Production Environment)
1.  **Prerequisite:** Ensure [Docker Desktop](https://www.docker.com/products/docker-desktop/) is installed and running.
2.  **Clone the repository** and `cd` into it.
3.  **Build the Docker image:** `docker build -t processor-engine .`
4.  **Run the container:** `docker run --rm -p 10000:10000 -e PORT=10000 -e SECRET_KEY='any-secret-key-for-local-testing' processor-engine`
5.  Open your browser to `http://localhost:10000`.

</details>

---
