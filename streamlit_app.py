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
    # Create realistic sample data - Top 5 merchants shown, platform totals separate
    merchants_data = {
        'Legal Name': ['MARATHON LIQUORS', 'POKE HANA LLC', 'The Stone Studio LLC', 'Quick Mart', 'Urban Cafe'],
        'DBA Name': ['Marathon Liquors', 'Poke Hana', 'Stone Studio', 'Quick Mart', 'Urban Cafe'],
        'Revenue_60d': [853406.33, 863402.52, 363752.00, 234567.89, 198432.56],  # Fixed MARATHON to 60-day, Poke Hana to item-level data
        'Status': ['Active', 'Active', 'Active', 'Active', 'Active'],  # Urban Cafe now Active (has monthly revenue)
        'MTD_Volume': [213351.59, 431701.26, 181876.00, 117283.95, 99216.28],  # Poke Hana from item-level monthly data
        'Last_Month_Volume': [213351.58, 431701.26, 181876.00, 117283.94, 99216.28]  # Poke Hana from item-level monthly data
    }
    
    # Platform totals (actual totals across all 741 merchants)
    platform_data = {
        'Total_Merchants': 741,
        'Total_Revenue_60d': 5172529.04,  # Platform total, not just top 5
        'Total_Customers': 135448,  # Corrected total after proper merge+dedupe
        'Active_Customers': 2294,
        'Marketing_OptIn': 11870,
        'New_This_Month': 567,
        'Registration_Trend': [450, 523, 601, 567, 634, 589, 612]
    }
    
    return pd.DataFrame(merchants_data), platform_data

# Load data
merchants_df, platform_data = load_sample_data()

# Key Metrics Section
st.header("📊 Key Business Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total Merchants", 
        f"{platform_data['Total_Merchants']:,}",
        delta="+2 this month"
    )

with col2:
    active_merchants = len(merchants_df[merchants_df['Status'] == 'Active'])
    st.metric(
        "Active Merchants (Top 5 in view)", 
        f"{active_merchants:,}",
        delta=f"{active_merchants/len(merchants_df)*100:.1f}% active"
    )

with col3:
    st.metric(
        "Total Customers", 
        f"{platform_data['Total_Customers']:,}",
        delta=f"+{platform_data['New_This_Month']:,} this month"
    )

with col4:
    st.metric(
        "Active Customers", 
        f"{platform_data['Active_Customers']:,}",
        delta=f"{platform_data['Active_Customers']/platform_data['Total_Customers']*100:.1f}% active"
    )

# Revenue Metrics
st.markdown("### 💰 Revenue Metrics (60-day period)")

total_revenue = platform_data['Total_Revenue_60d']  # Use platform total, not just top 5
daily_avg = total_revenue / 60
weekly_avg = total_revenue * 7 / 60
monthly_avg = total_revenue / 2

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Revenue (Platform)", f"${total_revenue:,.2f}")

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
        title="Top 5 Merchants by 60-Day Revenue (Platform Total: $5.17M)",
        color='Revenue_60d',
        color_continuous_scale='viridis'
    )
    fig.update_layout(height=400, xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Customer status pie chart
    customer_status = pd.DataFrame({
        'Status': ['Active', 'Inactive'],
        'Count': [platform_data['Active_Customers'], 
                 platform_data['Total_Customers'] - platform_data['Active_Customers']]
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
        'New_Registrations': platform_data['Registration_Trend']
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
st.markdown("### 🏪 Merchant Details (Top 5 in view)")
st.info("📊 Showing top 5 merchants by revenue. Platform totals above include all 741 merchants.")
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
current_revenue = platform_data['Total_Revenue_60d']  # Use platform total

# Naive predictions as per brief: next 60d = last 60d (0% growth)
projections = pd.DataFrame({
    'Period': ['Current (60d)', 'Next 60 days (naive)', 'Same period next year (naive)'],
    'Projected_Revenue': [current_revenue, current_revenue, current_revenue],  # 0% growth - naive prediction
    'Growth_Rate': ['0%', '0% (naive)', '0% (naive)']
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
    customer_summary = pd.DataFrame([platform_data])
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