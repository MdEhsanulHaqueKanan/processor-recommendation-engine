# Processor Recommendation & Analysis Engine

This project is a web-based decision-support tool designed to help engineers and product teams analyze and select processors for smart devices. It combines a rule-based recommendation engine with machine learning models to provide both direct filtering and predictive insights.

---

## Application Screenshot

![Screenshot of the application's prediction page](<app_ss_1.png>)

![Screenshot of the application's prediction page](<app_ss_2.png>)

![Screenshot of the application's prediction page](<app_ss_3.png>)

---

## Features

This application has two main components:

1.  **Recommendation Engine:** Allows users to filter a comprehensive database of processors based on specific technical criteria, such as:
    - Designer (e.g., Qualcomm, Apple)
    - Release Year Range
    - Number of Cores
    - 5G and Wi-Fi 6 Support

2.  **Processor Analyzer (ML-Powered):** Users can input the specifications of a real or hypothetical processor to get AI-powered predictions on:
    - The processor's primary **Function** (e.g., *Multi-core Application Processor with Modem*).
    - Its likely **Wireless Capabilities** (e.g., *5G Support, Wi-Fi 6+*).

## Technology Stack

- **Backend:** Python, Flask
- **Machine Learning:** Scikit-learn, Pandas
- **Frontend:** HTML, Bootstrap (for styling)
- **Data Source:** Curated Excel dataset (`Processors.xlsx`)

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)
![Scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)

## Project Structure

The project is structured using Flask best practices (Application Factory, Blueprints) to ensure modularity and maintainability.

```
├── processor-recommendation-engine/
│   └── app/
│       ├── templates
│       ├── static
│       ├── init.py
│       ├── routes.py 
│       └── services.py 
├── data 
├── models
├── notebooks
├── config.py 
├── requirements.txt 
└── run.py 
```


## Setup and Usage

To run this application locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/processor-recommendation-engine.git
    cd processor-recommendation-engine
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    # On Windows
    .\venv\Scripts\activate
    # On Mac/Linux
    source venv/bin/activate
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**
    ```bash
    python run.py
    ```

5.  Open your web browser and navigate to `http://127.0.0.1:5000`.