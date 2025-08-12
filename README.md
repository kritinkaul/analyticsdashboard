# Business Analytics Dashboard

This project analyzes merchant, customer, and sales data to provide comprehensive business metrics and predictions.

## Features

- **Customer Analytics**: Track total customers, active/inactive status, marketing opt-ins
- **Merchant Analytics**: Monitor merchant performance, processing volumes, active/inactive status  
- **Sales Predictions**: Forecast sales for next 2 months and same period next year
- **Interactive Dashboard**: Web-based dashboard with charts and data tables
- **Top Customer Identification**: Identify top 3 most valuable/potential customers

## Data Analysis Results

### Key Metrics (60-day period: Feb 7 - Aug 8, 2025)

#### Customer Metrics
- **Total Customers**: 21,997
- **Active Customers** (last 30 days): 1,152 (5.2%)
- **Inactive Customers**: 20,845 (94.8%)
- **Marketing Opt-ins**: 2,602 (11.8%)

#### Merchant Metrics  
- **Total Merchants**: 3
- **Active Merchants**: 3 (100%)
- **Inactive Merchants**: 0

#### Processing Volume
- **Total Volume** (60 days): $780,794.22
- **Daily Average**: $13,013.24
- **Weekly Average**: $91,092.66  
- **Monthly Average**: $390,397.11

#### Top Merchants by Volume
1. **MARATHON LIQUORS**: $426,703.17 ($213,351.58/month)
2. **POKE HANA**: $287,800.86 ($143,900.43/month)  
3. **Anthony's Pizza & Pasta**: $66,290.19 ($33,145.10/month)

#### Sales Predictions
- **Next 2 Months Platform Total**: $780,794.22
- **Same Period Next Year**: $858,873.64 (10% growth projected)

#### Top 3 Potential Customers
1. Abigail Eischen (Score: 9, Recent join)
2. Yasmin Lansiquot (Score: 9, Recent join)
3. Diane Goskie (Score: 9, Recent join)

## Files

- `data_analysis.py` - Main analysis script
- `dashboard.py` - Interactive web dashboard
- `analysis_report.json` - Detailed analysis results
- `requirements.txt` - Python dependencies

## Setup and Usage

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the analysis:
   ```bash
   python data_analysis.py
   ```

3. Start the dashboard:
   ```bash
   python dashboard.py
   ```

4. Open browser to: http://127.0.0.1:8050

## Data Sources

The analysis processes the following data files:
- Customer registration data (CSV)
- Revenue item sales reports (CSV) 
- Inventory exports (Excel)

## Analysis Methodology

### Active/Inactive Status Definitions
- **Active Customers**: Registered within last 30 days
- **Active Merchants**: Have sales revenue in the data period
- **Inactive Merchants**: No sales for >30 days (none in current dataset)

### Sales Predictions
- **Next 2 Months**: Based on current 60-day average performance
- **Same Period Next Year**: Assumes 10% annual growth rate
- **Volume Calculations**: 60-day data averaged for daily/weekly/monthly metrics

### Customer Scoring
Top customers identified based on:
- Recent registration (last 7 days): +3 points
- Marketing opt-in: +2 points  
- Complete profile (name): +2 points
- Phone number: +1 point
- Email address: +1 point

## Technical Notes

- Data period: 60 days (Feb 7, 2025 - Aug 8, 2025)
- All revenue figures are net sales after discounts/refunds
- Customer analysis based on registration timestamps
- Dashboard built with Plotly Dash and Bootstrap
