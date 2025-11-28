# WealthPath: AI-Powered Personal Finance Dashboard

**WealthPath** is a private, local-first financial planning tool designed to last. It helps you control your financial future by using AI to categorize transactions, detect anomalies, and forecast your future balance—all without sending your data to the cloud.

## 🌟 Features
* **Privacy First:** All data lives in a local SQLite database on your laptop.
* **AI Auto-Categorization:** Learns from your descriptions (e.g., "Uber" -> "Transport") using Machine Learning.
* **Cash Flow Forecasting:** Predicts next month's balance based on spending habits.
* **Guided Mode:** Built-in tutorials for non-technical users.
* **Excel & Power BI Ready:** One-click export for deep analysis.

---

## 🚀 Quick Start (VS Code)

### 1. Setup Environment
Open this folder in VS Code. Open a Terminal (`Ctrl+` `) and run:

```bash
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt