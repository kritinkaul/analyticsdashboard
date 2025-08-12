# Payment Platform Analytics Dashboard

A robust Streamlit dashboard that computes payment platform metrics from local data folders with no hardcoded values. Implements exact business rules for customer/merchant activity, deduplication, and sales aggregation.

## Features

- **Real-time ETL Pipeline**: Automatically discovers and processes data files
- **Proper Deduplication**: ID-first customer deduplication with email+phone fallback
- **Business Rules**: 60-day sales window, 30-day customer activity, coalesced merchant sales
- **Interactive Dashboard**: Streamlit UI with KPIs, charts, and data exports
- **DIFF Reporting**: Tracks changes between pipeline runs
- **Data Protection**: PII hidden in customer exports

## Quick Start

### Prerequisites

- Python 3.8+
- Virtual environment (recommended)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd DashboardData
```

2. Create and activate virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Data Setup

Place your data files in the following structure:
```
data/
├── customers/          # Customer CSV/Excel files
├── merchants/          # Merchant CSV/Excel files  
└── sales/             # Revenue Item Sales reports
```

### Running the Dashboard

```bash
streamlit run app.py
```

The dashboard will be available at `http://localhost:8501`

### Running ETL Only

```python
from src.etl import run_pipeline_from_folders
result = run_pipeline_from_folders()
print(f"Customers: {result['metrics']['customers_total']}")
print(f"Merchants: {result['metrics']['merchants_total']}")
print(f"Platform Volume: ${result['metrics']['platform_total_60d']:,.2f}")
```

## Architecture

### Components

- **`src/config.py`**: Configuration constants and data discovery patterns
- **`src/utils.py`**: File discovery utilities
- **`src/etl.py`**: Complete ETL pipeline with business rules
- **`app.py`**: Streamlit dashboard application

### Business Rules

- **Customer Deduplication**: Customer ID first, fallback to email+phone (collision prevention)
- **Merchant Processing**: No status filtering, includes all merchants
- **Sales Aggregation**: Item reports preferred, fallback to MTD + Last Month
- **Activity Flags**: 30-day customers, 60-day merchants
- **Coalescing**: No double-counting of sales data

## Current Metrics

Based on the latest data (2025-08-11):

- **Merchants**: 741 total, 64 active (8.6%)
- **Customers**: 134,778 total, 2,294 active (1.7%)
- **Platform Volume**: $5,172,529.04 (60d)
- **Daily Average**: $86,208.82
- **Marketing Opt-ins**: 11,870 (8.8%)

## Configuration

### File Discovery Patterns

```python
DATA_GLOBS = {
    "merchants": ["data/merchants/**/*.[cC][sS][vV]", "data/merchants/**/*.[xX][lL][sS][xX]"],
    "customers": ["data/customers/**/*.[cC][sS][vV]", "data/customers/**/*.[xX][lL][sS][xX]"], 
    "sales": ["data/sales/**/*Revenue Item Sales*.csv"]
}
```

### Date Reference

```python
TODAY = pd.Timestamp("2025-08-11")  # Fixed for reproducibility
```

## Data Export

The dashboard provides CSV downloads for:

- **Metrics Summary**: All KPIs and platform totals
- **Top 3 Merchants**: Highest volume merchants
- **Cleaned Customers**: Deduped customer data (PII redacted)
- **Cleaned Merchants**: Processed merchant data
- **Diagnostics**: Pipeline statistics and coverage

## Development

### Testing

```bash
# Test ETL pipeline
python -c "from src.etl import run_pipeline_from_folders; run_pipeline_from_folders()"

# Test Streamlit app
streamlit run app.py --server.headless true
```

### Adding New Data Sources

1. Update `DATA_GLOBS` patterns in `src/config.py`
2. Add column mapping logic in respective load functions
3. Update business rules if needed

## Troubleshooting

### Common Issues

- **File not found**: Check data folder structure and file patterns
- **Date parsing errors**: Verify date format consistency
- **Import errors**: Ensure virtual environment is activated

### Logs and Diagnostics

The ETL pipeline prints detailed diagnostics:
- File discovery results
- Row counts and deduplication stats
- Join coverage and validation checks
- DIFF reports for change tracking

## License

This project is for internal use and analytics purposes.
