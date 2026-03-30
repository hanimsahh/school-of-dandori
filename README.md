# 🎓 School of Dandori — Data Pipeline & Search Interface

## 📌 Overview

This project implements Phase 1 of the School of Dandori platform, transforming 211 unstructured course PDFs into a structured, searchable system.

The solution includes:

* Deterministic data extraction from PDFs
* Data validation and cleaning
* A simple Streamlit-based search interface

The result is a fully functional pipeline that enables course discovery without manual PDF lookup.

---

## ⚙️ System Pipeline

The system follows a three-step pipeline:

**1. Extraction → 2. Validation → 3. Interface**

* PDFs are parsed into structured data
* Data is cleaned and standardised
* A user interface allows searching and filtering

---

## 📊 Extracted Data Fields

Each course includes:

* **file** — Source PDF
* **title** — Course title
* **instructor** — Instructor name
* **location** — Course location
* **cost** — Course price (numeric)

---

## 🧹 Data Validation & Cleaning

To ensure high data quality:

* All 211 PDFs successfully processed
* Missing values removed
* Cost converted to numeric format
* Multi-word locations handled correctly (e.g. *Scottish Highlands*)
* Known edge cases manually corrected
* Final dataset verified for consistency

---

## 🔍 Search Interface (Streamlit)

A lightweight Streamlit application was developed to enable:

* Filtering by **location**
* Filtering by **cost range**
* Keyword-based **search**
* Instant display of matching courses

This removes the need for manual PDF searching and enables self-service discovery.

---

## 📁 Project Structure

```id="struct01"
school-of-dandori/
│
├── data/                # PDF files
├── scripts/
│   └── extract.py       # Extraction + validation
│
├── app/
│   └── main.py          # Streamlit interface
│
├── courses.csv          # Structured dataset
├── requirements.txt
└── README.md
```

---

## ▶️ How to Run

### 1. Install dependencies

```id="run01"
pip install -r requirements.txt
```

### 2. Run extraction pipeline

```id="run02"
python scripts/extract.py
```

### 3. Launch Streamlit app

```id="run03"
streamlit run app/main.py
```

---

## ✅ Results

* 211 / 211 courses extracted
* 0 missing values in final dataset
* Fully structured and validated data
* Functional search interface for course discovery

---

## 🚧 Constraints & Design Decisions

* Fully deterministic approach (no generative AI used)
* Focus on reliability and reproducibility
* Lightweight tools to ensure low maintenance
* Designed for easy integration into future systems

---

## 👥 Contribution

This project was developed as part of a group collaboration.

Primary contributions in this component:

* Data extraction pipeline
* Data validation and cleaning
* Structured dataset generation

---

## 🎯 Outcome

The system eliminates manual PDF searching and establishes a scalable foundation for future features such as database integration and recommendation systems.
