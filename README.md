# 🚀 Oil Well Investment Analysis Platform

End-to-end Python-based system that transforms raw AFE (Authorization for Expenditure) data, geological inputs, and offset well production data into **investor-ready financial and risk analysis artifacts**.

Built to support petroleum engineers, geologists, and investors in evaluating drilling opportunities using **data-driven insights and automated analytics**.

---

## 🎯 Overview

This project automates the analysis of proposed oil well investments by integrating multiple data sources and generating structured outputs used in financial and operational decision-making.

### 🔑 Key Capabilities

- Ingests AFE budget PDFs and structured Excel datasets  
- Processes proposed and offset well data for comparative analysis  
- Generates Excel-based reports with engineering visualizations  
- Produces 2D and 3D barrel charts for production analysis  
- Automates preparation of investor-ready deliverables  

---

## 🏗️ Architecture
```
AFE Budget (PDF) + Well Data (Excel)
↓
Python Data Pipeline
(Pandas, NumPy Processing)
↓
Data Enrichment & Analysis
↓
Excel Report Generation (XlsxWriter)
↓
Investor-Ready Outputs (Charts, Tables)
```


---

## ⚙️ Technical Highlights

- Optimized data processing workflows for large well datasets (thousands of records)
- Built scalable **Python data pipelines** using Pandas and NumPy  
- Developed automated workflows to transform raw engineering data into structured datasets  
- Generated Excel reports programmatically using **XlsxWriter**, including:
  - 2D and 3D barrel charts  
  - Production comparison charts  
  - Risk analysis tables  
- Implemented geospatial and proximity analysis for offset well evaluation  
- Integrated structured (Excel) and semi-structured (PDF) data sources  
- Designed modular, reusable data processing components  
- Applied vector-based distance calculations for spatial well analysis  

---

## 💡 Business Impact

This platform reduces manual analysis effort and enables faster, more informed investment decisions by:

- Automating financial and production modeling inputs  
- Standardizing evaluation across multiple well candidates  
- Providing visual insights into production potential  
- Supporting investor-ready reporting workflows  
- Reducing time-to-analysis for engineering and finance teams  

---

## 📊 Example Outputs

- Proposed Wells Summary  
- Offset Wells Comparison  
- Production Performance Analysis  
- 2D / 3D Barrel Charts  
- Risk Assessment Tables  

#### Barrel Plot
<img src="moosehorn-3-mile/moosehorn-3-mile-barrel-plot-1.8.png" width="500"/>

##### See Github Repo directory "moosehorn-3-mile" for addition output artifacts

---

## ▶️ Getting Started
```
Prerequisites
- Python 3.9+
- pip
Installation
- git clone https://github.com/stevethomas15977/public_afe.git
- cd public_afe
- pip install -r requirements.txt
Run the Application
- python main.py
```

