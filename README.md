# 🎓 School of Dandori — Course Discovery System

## 📌 Overview

This project delivers Phase 1 of the School of Dandori platform: transforming unstructured course PDFs into a structured, searchable system with a working user interface.

The system eliminates manual PDF lookup by enabling users to discover courses through a clean and interactive interface.

---

## 🚀 What This Project Does

* Extracts structured data from 211 PDF course files
* Cleans and validates the data for consistency
* Stores the data in a structured format (CSV + SQLite)
* Provides a Streamlit-based interface for searching and filtering courses

---

## 🧠 System Architecture

The project is organised into three main layers:

### 1. Data Processing

* `extract.py` → Parses PDFs into structured data
* `clean.py` → Validates and standardises the dataset

### 2. Data Storage

* `courses.csv` → Flat structured dataset
* `database/db.sqlite` → Lightweight database
* `schema.sql` → Database schema definition

### 3. Application Layer

* `app/main.py` → Streamlit application
* Enables search, filtering, and browsing

---

## 📊 Data Model

Each course includes:

* **file** — Source PDF
* **title** — Course title
* **instructor** — Instructor name
* **location** — Course location
* **cost** — Course price (integer)

---

## 🔍 Features

### Data Pipeline

* Deterministic PDF parsing (no AI used)
* Structured extraction across all 211 files
* Data cleaning and validation
* Edge-case handling

### Search Interface

* Filter by location
* Filter by price
* Keyword search
* Instant results display

### Storage

* CSV for simplicity
* SQLite for scalability and querying

---

## 📁 Project Structure

```id="struct02"
school-of-dandori/
│
├── app/                # Streamlit application
├── data/               # PDF files
├── database/           # SQLite DB + schema
├── scripts/            # Extraction & cleaning scripts
│
├── courses.csv         # Final dataset
├── requirements.txt
└── README.md
```

---

## ▶️ How to Run

### 1. Install dependencies

```id="run11"
pip install -r requirements.txt
```

### 2. Run data extraction

```id="run12"
python scripts/extract.py
```

### 3. (Optional) Clean data

```id="run13"
python scripts/clean.py
```

### 4. Launch the app

```id="run14"
streamlit run app/main.py
```

---

## ✅ Results

* 211 / 211 PDFs successfully processed
* Clean, structured dataset with 0 missing values
* Functional search interface
* Reduced manual lookup to zero

---

## ⚠️ Constraints

* No generative AI used (fully deterministic system)
* Designed for low maintenance and low cost
* Built to support future scalability

---

## 👥 Team Contribution

This project was developed as part of a group collaboration.

Key contributions in this component:

* Data extraction pipeline
* Data validation and cleaning
* Structured dataset creation

---

## 🎯 Outcome

The system transforms a manual, time-intensive workflow into an efficient, scalable solution, enabling independent course discovery and laying the foundation for future enhancements.
