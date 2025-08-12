#!/usr/bin/env python3
"""
Streamlit Cloud Dashboard for Payment Platform Analytics
Optimized for cloud deployment with file upload support
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import json
import io
from datetime import datetime
import sys
import os
import tempfile
from pathlib import Path

# Add src to path for imports
sys.path.append('src')
sys.path.append('.')

# Try both import styles for flexibility
try:
    from src.etl import run_pipeline_from_folders, run_etl_pipeline
    from src.config import DATA_GLOBS, TODAY
except ImportError:
    try:
        from etl import run_pipeline_from_folders, run_etl_pipeline
        from config import DATA_GLOBS, TODAY
    except ImportError:
        st.error("ETL modules not found. Please check the deployment.")
        st.stop()

# Page config
st.set_page_config(
    page_title="Payment Platform Analytics",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

def process_uploaded_files(uploaded_files):
    """Process uploaded files and return pipeline results"""
    if not uploaded_files:
        return None
        
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create subdirectories
        data_dir = Path(temp_dir) / "data"
        merchants_dir = data_dir / "merchants"
        customers_dir = data_dir / "customers" 
        sales_dir = data_dir / "sales"
        
        for dir_path in [merchants_dir, customers_dir, sales_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded files to appropriate directories
        for uploaded_file in uploaded_files:
            filename = uploaded_file.name.lower()
            
            # Determine file type and save to appropriate directory
            if any(keyword in filename for keyword in ['merchant', 'store']):
                save_path = merchants_dir / uploaded_file.name
            elif any(keyword in filename for keyword in ['customer', 'user']):
                save_path = customers_dir / uploaded_file.name
            elif 'revenue item sales' in filename or any(keyword in filename for keyword in ['sales', 'revenue']):
                save_path = sales_dir / uploaded_file.name
            else:
                # Default to customers if unclear
                save_path = customers_dir / uploaded_file.name
            
            # Save file
            with open(save_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        
        # Update data directory path and run pipeline
        original_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            result = run_pipeline_from_folders()
            return result
        finally:
            os.chdir(original_cwd)

def create_demo_data():
    """Create demo data for when no files are uploaded"""
    return {
        'metrics': {
            'customers_total': 134778,
            'customers_active': 2294,
            'customers_marketing': 11870,
            'merchants_total': 741,
            'merchants_active': 64,
            'platform_total_60d': 5172529.04,
            'platform_daily_avg': 86208.82,
            'platform_weekly_avg': 603461.72,
            'platform_monthly_avg': 2586264.52
        },
        'top_merchants': [
            {'name': 'POKE HANA', 'revenue_60d': 863402.52},
            {'name': 'MARATHON LIQUORS', 'revenue_60d': 853406.33},
            {'name': "ANTHONY'S PIZZA & PASTA", 'revenue_60d': 198870.64}
        ],
        'diagnostics': {
            'files_processed': 9,
            'processing_time': '2.3s',
            'last_updated': '2025-08-12 18:30:00'
        }
    }

def main():
    st.title("💳 Payment Platform Analytics")
    st.markdown("---")
    
    # Sidebar for file upload
    with st.sidebar:
        st.header("📁 Data Upload")
        st.markdown("Upload your data files to analyze:")
        
        uploaded_files = st.file_uploader(
            "Choose files",
            accept_multiple_files=True,
            type=['csv', 'xlsx', 'xls'],
            help="Upload merchant, customer, and sales data files"
        )
        
        use_demo = st.checkbox("Use Demo Data", value=True if not uploaded_files else False)
        
        if st.button("🔄 Process Data"):
            if uploaded_files:
                with st.spinner("Processing uploaded files..."):
                    result = process_uploaded_files(uploaded_files)
                    if result:
                        st.session_state['pipeline_result'] = result
                        st.success(f"✅ Processed {len(uploaded_files)} files successfully!")
                    else:
                        st.error("❌ Error processing files")
            elif use_demo:
                st.session_state['pipeline_result'] = create_demo_data()
                st.success("✅ Demo data loaded!")
    
    # Main content
    if 'pipeline_result' not in st.session_state:
        st.session_state['pipeline_result'] = create_demo_data()
    
    result = st.session_state['pipeline_result']
    metrics = result['metrics']
    
    # Display metrics
    st.header("📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Customers",
            f"{metrics['customers_total']:,}",
            help="All unique customers in the system"
        )
        st.metric(
            "Active Customers",
            f"{metrics['customers_active']:,}",
            delta=f"{(metrics['customers_active'] / metrics['customers_total'] * 100):.1f}% active",
            help="Customers with activity in the last 30 days"
        )
    
    with col2:
        st.metric(
            "Marketing Subscribers",
            f"{metrics['customers_marketing']:,}",
            delta=f"{(metrics['customers_marketing'] / metrics['customers_total'] * 100):.1f}% opted in",
            help="Customers who opted in for marketing"
        )
    
    with col3:
        st.metric(
            "Total Merchants",
            f"{metrics['merchants_total']:,}",
            help="All merchants in the platform"
        )
        st.metric(
            "Active Merchants",
            f"{metrics['merchants_active']:,}",
            delta=f"{(metrics['merchants_active'] / metrics['merchants_total'] * 100):.1f}% active",
            help="Merchants with sales in the last 60 days"
        )
    
    with col4:
        st.metric(
            "Platform Revenue (60d)",
            f"${metrics['platform_total_60d']:,.0f}",
            help="Total platform revenue in the last 60 days"
        )
        st.metric(
            "Daily Average",
            f"${metrics['platform_daily_avg']:,.0f}",
            help="Average daily platform revenue"
        )
    
    # Charts section
    st.header("📈 Analytics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Customer breakdown chart
        customer_data = {
            'Status': ['Active', 'Inactive'],
            'Count': [metrics['customers_active'], metrics['customers_total'] - metrics['customers_active']]
        }
        fig_customers = px.pie(
            customer_data, 
            values='Count', 
            names='Status',
            title="Customer Activity Breakdown",
            color_discrete_map={'Active': '#1f77b4', 'Inactive': '#ff7f0e'}
        )
        st.plotly_chart(fig_customers, use_container_width=True)
    
    with col2:
        # Merchant breakdown chart
        merchant_data = {
            'Status': ['Active', 'Inactive'],
            'Count': [metrics['merchants_active'], metrics['merchants_total'] - metrics['merchants_active']]
        }
        fig_merchants = px.pie(
            merchant_data,
            values='Count',
            names='Status', 
            title="Merchant Activity Breakdown",
            color_discrete_map={'Active': '#2ca02c', 'Inactive': '#d62728'}
        )
        st.plotly_chart(fig_merchants, use_container_width=True)
    
    # Top merchants
    if 'top_merchants' in result and result['top_merchants']:
        st.header("🏆 Top Performing Merchants")
        
        top_merchants_df = pd.DataFrame(result['top_merchants'])
        if not top_merchants_df.empty:
            fig_top = px.bar(
                top_merchants_df.head(10),
                x='name',
                y='revenue_60d',
                title="Top 10 Merchants by Revenue (60 days)",
                labels={'revenue_60d': 'Revenue ($)', 'name': 'Merchant'}
            )
            fig_top.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig_top, use_container_width=True)
            
            # Table view
            st.subheader("📋 Top Merchants Table")
            formatted_df = top_merchants_df.copy()
            formatted_df['revenue_60d'] = formatted_df['revenue_60d'].apply(lambda x: f"${x:,.2f}")
            st.dataframe(formatted_df, use_container_width=True)
    
    # Diagnostics
    if 'diagnostics' in result:
        st.header("🔍 Processing Information")
        diag = result['diagnostics']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"📁 Files Processed: {diag.get('files_processed', 'N/A')}")
        with col2:
            st.info(f"⏱️ Processing Time: {diag.get('processing_time', 'N/A')}")
        with col3:
            st.info(f"🕒 Last Updated: {diag.get('last_updated', 'N/A')}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>💳 Payment Platform Analytics Dashboard | Built with Streamlit</p>
        <p><a href="https://github.com/kritinkaul/swipe-savvyintern" target="_blank">📚 View Source Code</a></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
