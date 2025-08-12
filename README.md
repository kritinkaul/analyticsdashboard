# 💳 Payment Platform Analytics Dashboard

A modern, interactive Streamlit dashboard for payment platform business intelligence and analytics.

## 🚀 Live Demo

**Streamlit Cloud**: [Coming Soon - Deploy from this repository]

## 📊 Features

- **Multi-View Interface**: Overview, Merchants, Customers, Advanced Analytics
- **Interactive Charts**: Plotly-powered visualizations with hover effects
- **Key Metrics**: Real-time business KPIs and performance indicators
- **Data Export**: CSV download functionality for all datasets
- **Responsive Design**: Optimized for desktop and mobile viewing

## 📈 Dashboard Views

### 1. 📈 Overview
- Total merchants: 5 (4 active)
- Total customers: 134,778 (2,294 active)
- Revenue metrics with daily/weekly/monthly breakdowns
- Activity percentages and growth indicators

### 2. 🏪 Merchants
- Top 5 merchants by 60-day revenue
- Interactive bar charts with revenue visualization
- Detailed merchant table with MTD and last month volumes
- Revenue formatting with currency display

### 3. 👥 Customers
- Customer activity status pie chart
- 7-week registration trend analysis
- Active vs inactive customer breakdown
- Marketing opt-in statistics

### 4. 📊 Analytics
- Revenue distribution by merchant
- Growth projections for next periods
- Advanced business intelligence metrics
- Forecasting with percentage growth rates

## 🛠️ Local Development

### Prerequisites
- Python 3.8+
- pip package manager

### Installation
```bash
# Clone the repository
git clone https://github.com/kritinkaul/analyticsdashboard.git
cd analyticsdashboard

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run streamlit_app.py
```

### Access
- **Local URL**: http://localhost:8501
- **Network URL**: Available for LAN access

## 📦 Dependencies

The dashboard uses minimal, lightweight dependencies:
- **streamlit**: Web app framework
- **pandas**: Data manipulation and analysis
- **plotly**: Interactive visualizations
- **numpy**: Numerical computing support

## 🎯 Sample Data

The dashboard includes realistic sample data:
- **Merchants**: MARATHON LIQUORS, Poke Hana, Stone Studio, Quick Mart, Urban Cafe
- **Revenue**: $2.1M+ total 60-day platform volume
- **Customers**: 134K+ registered users with activity tracking
- **Trends**: Weekly registration patterns and growth metrics

## 📋 Business Rules

- **Active Customer**: Activity within last 30 days
- **Active Merchant**: Sales volume > $0 in last 60 days  
- **Revenue Window**: 60-day rolling period for calculations
- **Data Refresh**: Real-time updates on page interactions

## 🚀 Deployment

### Streamlit Cloud
1. Fork this repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repository
5. Set main file: `streamlit_app.py`
6. Deploy!

### Local Server
```bash
streamlit run streamlit_app.py --server.port 8501
```

## 📊 Key Metrics Displayed

- **$2,087,255.86** - Total 60-day platform revenue
- **$34,787.60** - Daily revenue average
- **$243,513.19** - Weekly revenue average  
- **$1,043,627.93** - Monthly revenue average
- **80%** - Merchant activity rate (4/5 active)
- **1.7%** - Customer activity rate (2,294/134,778)

## 💾 Export Capabilities

- **Merchants CSV**: Complete merchant data with revenue metrics
- **Customers CSV**: Customer summary statistics and counts
- **Metrics CSV**: Platform performance metrics and calculations

## 🎨 UI Features

- **Professional Design**: Clean, modern interface with intuitive navigation
- **Color-Coded Charts**: Consistent color schemes for data visualization
- **Responsive Layout**: Adaptive columns and mobile-friendly design
- **Real-Time Updates**: Dynamic timestamps and live data refresh

Built with ❤️ using Streamlit, Pandas, and Plotly

---

**Repository**: https://github.com/kritinkaul/analyticsdashboard
**License**: MIT
**Last Updated**: August 12, 2025
