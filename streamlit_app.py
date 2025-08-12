import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page config
st.set_page_config(
    page_title="Payment Platform Analytics",
    page_icon="💳",
    layout="wide"
)

# Title and header
st.title("💳 Payment Platform Analytics Dashboard")
st.markdown("---")

# Sample data
@st.cache_data
def load_sample_data():
    # Create realistic sample data
    merchants_data = {
        'Legal Name': ['MARATHON LIQUORS', 'Poke Hana Restaurant', 'The Stone Studio LLC', 'Quick Mart', 'Urban Cafe'],
        'DBA Name': ['Marathon Liquors', 'Poke Hana', 'Stone Studio', 'Quick Mart', 'Urban Cafe'],
        'Revenue_60d': [426703.17, 864838.21, 363752.00, 234567.89, 198432.56],
        'Status': ['Active', 'Active', 'Active', 'Active', 'Inactive'],
        'MTD_Volume': [213351.59, 432419.11, 181876.00, 117283.95, 0],
        'Last_Month_Volume': [213351.58, 432419.10, 181876.00, 117283.94, 198432.56]
    }
    
    customers_data = {
        'Total_Customers': 134778,
        'Active_Customers': 2294,
        'Marketing_OptIn': 11870,
        'New_This_Month': 567,
        'Registration_Trend': [450, 523, 601, 567, 634, 589, 612]
    }
    
    return pd.DataFrame(merchants_data), customers_data

# Load data
merchants_df, customers_data = load_sample_data()

# Key Metrics Section
st.header("📊 Key Business Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Merchants", 
        f"{len(merchants_df):,}",
        delta="+2 this month"
    )

with col2:
    active_merchants = len(merchants_df[merchants_df['Status'] == 'Active'])
    st.metric(
        "Active Merchants", 
        f"{active_merchants:,}",
        delta=f"{active_merchants/len(merchants_df)*100:.1f}% active"
    )

with col3:
    st.metric(
        "Total Customers", 
        f"{customers_data['Total_Customers']:,}",
        delta=f"+{customers_data['New_This_Month']:,} this month"
    )

with col4:
    st.metric(
        "Active Customers", 
        f"{customers_data['Active_Customers']:,}",
        delta=f"{customers_data['Active_Customers']/customers_data['Total_Customers']*100:.1f}% active"
    )

# Revenue Metrics
st.markdown("### 💰 Revenue Metrics (60-day period)")

total_revenue = merchants_df['Revenue_60d'].sum()
daily_avg = total_revenue / 60
weekly_avg = total_revenue * 7 / 60
monthly_avg = total_revenue / 2

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Revenue", f"${total_revenue:,.2f}")

with col2:
    st.metric("Daily Average", f"${daily_avg:,.2f}")

with col3:
    st.metric("Weekly Average", f"${weekly_avg:,.2f}")

with col4:
    st.metric("Monthly Average", f"${monthly_avg:,.2f}")

# Charts Section
st.markdown("---")
st.header("📈 Analytics & Visualizations")

# Two column layout for charts
col1, col2 = st.columns(2)

with col1:
    # Top merchants chart
    fig = px.bar(
        merchants_df.head(5), 
        x='Legal Name', 
        y='Revenue_60d',
        title="Top 5 Merchants by 60-Day Revenue",
        color='Revenue_60d',
        color_continuous_scale='viridis'
    )
    fig.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Customer status pie chart
    customer_status = pd.DataFrame({
        'Status': ['Active', 'Inactive'],
        'Count': [customers_data['Active_Customers'], 
                 customers_data['Total_Customers'] - customers_data['Active_Customers']]
    })
    
    fig = px.pie(
        customer_status, 
        values='Count', 
        names='Status',
        title="Customer Activity Status",
        color_discrete_map={'Active': '#00CC96', 'Inactive': '#EF553B'}
    )
    st.plotly_chart(fig, use_container_width=True)

# Second row of charts
col1, col2 = st.columns(2)

with col1:
    # Registration trend
    trend_data = pd.DataFrame({
        'Week': [f'Week {i+1}' for i in range(7)],
        'New_Registrations': customers_data['Registration_Trend']
    })
    
    fig = px.line(
        trend_data, 
        x='Week', 
        y='New_Registrations',
        title="Customer Registration Trend (Last 7 Weeks)",
        markers=True
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Revenue distribution pie chart
    fig = px.pie(
        merchants_df, 
        values='Revenue_60d', 
        names='Legal Name',
        title="Revenue Distribution by Merchant"
    )
    st.plotly_chart(fig, use_container_width=True)

# Data Tables Section
st.markdown("---")
st.header("📋 Data Tables")

# Merchant details table
st.markdown("### 🏪 Merchant Details")
st.dataframe(
    merchants_df.style.format({
        'Revenue_60d': '${:,.2f}',
        'MTD_Volume': '${:,.2f}',
        'Last_Month_Volume': '${:,.2f}'
    }),
    use_container_width=True
)

# Growth projections
st.markdown("### 🔮 Growth Projections")
current_revenue = merchants_df['Revenue_60d'].sum()

projections = pd.DataFrame({
    'Period': ['Current (60d)', 'Next 60 days', 'Same period next year'],
    'Projected_Revenue': [current_revenue, current_revenue * 1.05, current_revenue * 1.15],
    'Growth_Rate': ['0%', '+5%', '+15%']
})

st.dataframe(
    projections.style.format({
        'Projected_Revenue': '${:,.2f}'
    }),
    use_container_width=True
)

# Export Data Section
st.markdown("---")
st.header("💾 Export Data")

col1, col2, col3 = st.columns(3)

with col1:
    merchants_csv = merchants_df.to_csv(index=False)
    st.download_button(
        "📊 Download Merchants CSV",
        merchants_csv,
        "merchants_data.csv",
        "text/csv"
    )

with col2:
    customer_summary = pd.DataFrame([customers_data])
    customers_csv = customer_summary.to_csv(index=False)
    st.download_button(
        "👥 Download Customers CSV", 
        customers_csv,
        "customers_summary.csv",
        "text/csv"
    )

with col3:
    metrics_data = {
        'Metric': ['Total Revenue', 'Daily Avg', 'Weekly Avg', 'Monthly Avg'],
        'Value': [total_revenue, daily_avg, weekly_avg, monthly_avg]
    }
    metrics_csv = pd.DataFrame(metrics_data).to_csv(index=False)
    st.download_button(
        "📈 Download Metrics CSV",
        metrics_csv,
        "platform_metrics.csv", 
        "text/csv"
    )

# Footer
st.markdown("---")
st.markdown("""
### 📋 Dashboard Information
- **Data Source**: Demo data for analytics showcase
- **Last Updated**: {timestamp}
- **Refresh Rate**: Real-time
- **Business Rules**: 30-day customer activity, 60-day merchant sales window

Built with ❤️ using Streamlit, Pandas, and Plotly
""".format(timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S")))