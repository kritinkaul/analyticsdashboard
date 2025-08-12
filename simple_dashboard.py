#!/usr/bin/env python3
"""
Simplified Streamlit Dashboard - Minimal version to avoid connection issues
"""
import streamlit as st
import pandas as pd
import sys
import os

# Configure page first
st.set_page_config(
    page_title="Payment Analytics",
    page_icon="💳",
    layout="wide"
)

# Add src to path
if 'src' not in sys.path:
    sys.path.append('src')

# Cache the ETL function to avoid re-running on every interaction
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    """Load and cache the data"""
    try:
        from etl import run_pipeline_from_folders
        return run_pipeline_from_folders()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

def main():
    st.title("💳 Payment Platform Analytics")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading analytics data..."):
        result = load_data()
    
    if result is None:
        st.error("Failed to load data. Please check your data files.")
        return
    
    customers = result['customers']
    merchants = result['merchants_enriched']
    
    # Overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Customers", f"{len(customers):,}")
        
    with col2:
        active_customers = customers['active_flag'].sum()
        st.metric("Active Customers", f"{active_customers:,}")
        
    with col3:
        st.metric("Total Merchants", f"{len(merchants):,}")
        
    with col4:
        active_merchants = merchants['active_flag'].sum()
        st.metric("Active Merchants", f"{active_merchants:,}")
    
    # Revenue metrics
    st.markdown("## 💰 Revenue Overview")
    col1, col2, col3 = st.columns(3)
    
    total_revenue = merchants['net_sales_60d'].sum()
    
    with col1:
        st.metric("Platform Revenue (60d)", f"${total_revenue:,.2f}")
        
    with col2:
        daily_avg = total_revenue / 60
        st.metric("Daily Average", f"${daily_avg:,.2f}")
        
    with col3:
        monthly_avg = total_revenue / 2
        st.metric("Monthly Average", f"${monthly_avg:,.2f}")
    
    # Top merchants
    st.markdown("## 🏆 Top Merchants")
    top_merchants = merchants.nlargest(5, 'net_sales_60d')[['legal_name', 'net_sales_60d', 'active_flag']]
    top_merchants.columns = ['Merchant Name', 'Revenue (60d)', 'Active']
    top_merchants['Revenue (60d)'] = top_merchants['Revenue (60d)'].apply(lambda x: f"${x:,.2f}")
    st.dataframe(top_merchants, use_container_width=True)
    
    # Customer breakdown
    st.markdown("## 📊 Customer Analysis")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Customer Status")
        active_pct = (active_customers / len(customers)) * 100
        st.write(f"Active Rate: {active_pct:.1f}%")
        
        if 'marketing_opt_in' in customers.columns:
            marketing_customers = customers['marketing_opt_in'].sum()
            marketing_pct = (marketing_customers / len(customers)) * 100
            st.write(f"Marketing Opt-in Rate: {marketing_pct:.1f}%")
            st.metric("Marketing Subscribers", f"{marketing_customers:,}")
    
    with col2:
        st.subheader("Merchant Status")
        merchant_active_pct = (active_merchants / len(merchants)) * 100
        st.write(f"Active Rate: {merchant_active_pct:.1f}%")
    
    # Data export
    st.markdown("## 📁 Data Export")
    col1, col2 = st.columns(2)
    
    with col1:
        csv_customers = customers.to_csv(index=False)
        st.download_button(
            label="📋 Download Customers CSV",
            data=csv_customers,
            file_name="customers_export.csv",
            mime="text/csv"
        )
    
    with col2:
        csv_merchants = merchants.to_csv(index=False)
        st.download_button(
            label="🏪 Download Merchants CSV", 
            data=csv_merchants,
            file_name="merchants_export.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
