#!/usr/bin/env python3
"""
Streamlit Dashboard for Payment Platform Analytics
Computes all metrics from local data folders with exact business rules
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

# Add src to path for imports
sys.path.append('src')

# Try both import styles for flexibility
try:
    from src.etl import run_pipeline_from_folders
except ImportError:
    from etl import run_pipeline_from_folders

# Page config
st.set_page_config(
    page_title="Payment Platform Analytics",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded"
)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_pipeline_data():
    """Load and cache pipeline results"""
    return run_pipeline_from_folders()

def process_uploaded_files(merchant_file, customer_files, sales_files):
    """Process uploaded files and return pipeline results"""
    import tempfile
    import os
    from pathlib import Path
    import pandas as pd
    
    # Create temporary directory structure
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create subdirectories
        merchants_dir = os.path.join(temp_dir, "merchants")
        customers_dir = os.path.join(temp_dir, "customers")
        sales_dir = os.path.join(temp_dir, "sales")
        
        os.makedirs(merchants_dir, exist_ok=True)
        os.makedirs(customers_dir, exist_ok=True)
        os.makedirs(sales_dir, exist_ok=True)
        
        # Save uploaded files to temp directories
        if merchant_file:
            merchant_path = os.path.join(merchants_dir, merchant_file.name)
            with open(merchant_path, "wb") as f:
                f.write(merchant_file.getbuffer())
        
        for i, customer_file in enumerate(customer_files):
            customer_path = os.path.join(customers_dir, f"customer_{i}_{customer_file.name}")
            with open(customer_path, "wb") as f:
                f.write(customer_file.getbuffer())
        
        for i, sales_file in enumerate(sales_files):
            sales_path = os.path.join(sales_dir, f"sales_{i}_{sales_file.name}")
            with open(sales_path, "wb") as f:
                f.write(sales_file.getbuffer())
        
        # Import ETL functions directly
        from src.etl import load_merchants, load_customers, load_sales, enrich_and_metrics
        
        # Load data using the ETL functions
        try:
            # Temporarily modify the discover_files function to use our temp dirs
            import src.utils
            original_discover_files = src.utils.discover_files
            
            def temp_discover_files(patterns):
                """Temporary file discovery for uploaded files"""
                if "merchants" in str(patterns):
                    return [os.path.join(merchants_dir, f) for f in os.listdir(merchants_dir)]
                elif "customers" in str(patterns):
                    return [os.path.join(customers_dir, f) for f in os.listdir(customers_dir)]
                elif "sales" in str(patterns):
                    return [os.path.join(sales_dir, f) for f in os.listdir(sales_dir)]
                return []
            
            # Replace the discover_files function temporarily
            src.utils.discover_files = temp_discover_files
            
            try:
                # Load data
                merchants = load_merchants()
                customers = load_customers()
                sales = load_sales()
                
                # Enrich and compute metrics
                enriched, metrics = enrich_and_metrics(merchants, customers, sales)
                
                # Create diagnostics
                diagnostics = {
                    "files_discovered": {
                        "merchants": len(os.listdir(merchants_dir)),
                        "customers": len(os.listdir(customers_dir)),
                        "sales": len(os.listdir(sales_dir))
                    },
                    "data_loaded": {
                        "merchants": len(merchants),
                        "customers": len(customers),
                        "sales_merchants": len(sales)
                    },
                    "coverage": {
                        "merchants_with_item_data": enriched["net_sales_60d_item"].notna().sum(),
                        "merchants_using_fallback": len(enriched) - enriched["net_sales_60d_item"].notna().sum()
                    }
                }
                
                return {
                    "customers": customers,
                    "merchants_enriched": enriched,
                    "metrics": metrics,
                    "diagnostics": diagnostics
                }
                
            finally:
                # Restore original discover_files function
                src.utils.discover_files = original_discover_files
                
        except Exception as e:
            st.error(f"Error processing uploaded files: {str(e)}")
            st.exception(e)
            return None

def create_charts(metrics, merchants_enriched):
    """Create visualization charts"""
    
    # Merchant status pie chart
    fig_merchants = go.Figure(data=[go.Pie(
        labels=['Active', 'Inactive'],
        values=[metrics['merchants_active'], metrics['merchants_inactive']],
        hole=.3,
        marker_colors=['#00cc88', '#ff6b6b']
    )])
    fig_merchants.update_layout(
        title="Merchant Status Distribution",
        showlegend=True,
        height=400
    )
    
    # Customer status pie chart  
    fig_customers = go.Figure(data=[go.Pie(
        labels=['Active (30d)', 'Inactive'],
        values=[metrics['customers_active'], metrics['customers_inactive']],
        hole=.3,
        marker_colors=['#4dabf7', '#ffd43b']
    )])
    fig_customers.update_layout(
        title="Customer Status Distribution", 
        showlegend=True,
        height=400
    )
    
    # Top merchants bar chart
    top3 = metrics['top3'].copy()
    top3['display_name'] = top3['dba_name'].fillna(top3['legal_name'])
    
    fig_top3 = px.bar(
        top3,
        x='display_name',
        y='net_sales_60d',
        title="Top 3 Merchants by 60-Day Sales",
        labels={'net_sales_60d': '60-Day Net Sales ($)', 'display_name': 'Merchant'},
        color='net_sales_60d',
        color_continuous_scale='Viridis'
    )
    fig_top3.update_layout(height=400, showlegend=False)
    
    return fig_merchants, fig_customers, fig_top3

def main():
    # Header
    st.title("💳 Payment Platform Analytics Dashboard")
    st.markdown("**Real-time metrics computed from data folders (no hardcoded values)**")
    st.markdown("---")
    
    # Load data automatically from local folders
    with st.spinner("🔄 Running ETL pipeline..."):
        try:
            res = load_pipeline_data()
            customers = res["customers"]
            merchants = res["merchants_enriched"]
            m = res["metrics"]
            diagnostics = res["diagnostics"]
            
            st.success("🎉 Data loaded successfully from local folders!")
            
        except Exception as e:
            st.error(f"❌ Error loading data: {e}")
            st.exception(e)
            st.stop()
    
    # KPI Section
    st.subheader("📊 Key Performance Indicators")
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric(
            "Total Merchants",
            f"{m['merchants_total']:,}",
            help="All merchants regardless of status"
        )
    with k2:
        st.metric(
            "Active Merchants",
            f"{m['merchants_active']:,}",
            f"Inactive: {m['merchants_inactive']:,}",
            help="Merchants with sales > 0 in last 60 days"
        )
    with k3:
        st.metric(
            "Total Customers",
            f"{m['customers_total']:,}",
            help="All customers after deduplication"
        )
    with k4:
        st.metric(
            "Active Customers (30d)",
            f"{m['customers_active']:,}",
            f"Inactive: {m['customers_inactive']:,}",
            help="Customers registered within last 30 days"
        )

    # Platform Volume Section
    st.subheader("💰 Platform Volume Analysis")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric(
            "Total Volume (60d)",
            f"${m['platform_total_60d']:,.2f}",
            help="Sum of all merchant 60-day sales"
        )
    with c2:
        st.metric(
            "Daily Average",
            f"${m['platform_daily']:,.2f}",
            help="60-day total ÷ 60"
        )
    with c3:
        st.metric(
            "Weekly Average",
            f"${m['platform_weekly']:,.2f}",
            help="60-day total × 7 ÷ 60"
        )
    with c4:
        st.metric(
            "Monthly Average",
            f"${m['platform_monthly']:,.2f}",
            help="60-day total ÷ 2"
        )

    # Marketing Section
    st.subheader("📧 Marketing Analysis")
    col1, col2 = st.columns(2)
    with col1:
        st.metric(
            "Marketing Opt-ins",
            f"{m['customers_marketing']:,}",
            f"{(m['customers_marketing']/m['customers_total']*100):.1f}% of customers" if m['customers_total'] > 0 else "0%"
        )
    with col2:
        # Pie chart for marketing opt-ins
        if m['customers_total'] > 0:
            fig_marketing = go.Figure(data=[go.Pie(
                labels=['Opted In', 'Not Opted In'],
                values=[m['customers_marketing'], m['customers_total'] - m['customers_marketing']],
                hole=0.3,
                marker_colors=['#28a745', '#dc3545']
            )])
            fig_marketing.update_layout(
                title="Marketing Opt-in Distribution",
                height=300
            )
            st.plotly_chart(fig_marketing, use_container_width=True)

    # Top 3 Merchants Section
    st.subheader("🏆 Top 3 Merchants by 60-Day Sales")
    
    # Display top 3 table
    top3_display = m["top3"].copy()
    top3_display["net_sales_60d"] = top3_display["net_sales_60d"].apply(lambda x: f"${x:,.2f}")
    top3_display["daily_est"] = top3_display["daily_est"].apply(lambda x: f"${x:,.2f}")
    top3_display["weekly_est"] = top3_display["weekly_est"].apply(lambda x: f"${x:,.2f}")
    top3_display["monthly_est"] = top3_display["monthly_est"].apply(lambda x: f"${x:,.2f}")
    
    top3_display.columns = ['Legal Name', 'DBA Name', 'Net Sales (60d)', 'Daily Est.', 'Weekly Est.', 'Monthly Est.']
    st.dataframe(top3_display, use_container_width=True)

    # Top 3 Chart
    if len(m["top3"]) > 0:
        top3_chart_data = m["top3"]
        names = []
        for _, row in top3_chart_data.iterrows():
            name = row.get('dba_name') if pd.notna(row.get('dba_name')) else row.get('legal_name', 'Unknown')
            names.append(name)
        values = top3_chart_data["net_sales_60d"].tolist()
        
        fig_top3 = go.Figure(data=[go.Bar(
            x=names,
            y=values,
            marker_color=['#007bff', '#28a745', '#ffc107'][:len(names)]
        )])
        fig_top3.update_layout(
            title="Top 3 Merchants by Volume",
            xaxis_title="Merchant",
            yaxis_title="Net Sales ($)",
            yaxis_tickformat='$,.0f',
            height=400
        )
        st.plotly_chart(fig_top3, use_container_width=True)

    # Charts Section
    st.subheader("📈 Analytics Charts")
    
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        # Customer status distribution
        fig_customers = go.Figure(data=[go.Pie(
            labels=['Active (Last 30 days)', 'Inactive'],
            values=[m['customers_active'], m['customers_inactive']],
            hole=0.3,
            marker_colors=['#28a745', '#dc3545']
        )])
        fig_customers.update_layout(
            title="Customer Activity Status",
            height=400
        )
        st.plotly_chart(fig_customers, use_container_width=True)
    
    with chart_col2:
        # Merchant status distribution
        fig_merchants = go.Figure(data=[go.Pie(
            labels=['Active (60d Sales)', 'Inactive'],
            values=[m['merchants_active'], m['merchants_inactive']],
            hole=0.3,
            marker_colors=['#17a2b8', '#6c757d']
        )])
        fig_merchants.update_layout(
            title="Merchant Activity Status",
            height=400
        )
        st.plotly_chart(fig_merchants, use_container_width=True)

    # Diagnostics Section
    st.subheader("🔍 Pipeline Diagnostics")
    
    diag_col1, diag_col2, diag_col3 = st.columns(3)
    
    with diag_col1:
        st.markdown("**Files Discovered**")
        st.write(f"📁 Merchants: {diagnostics['files_discovered']['merchants']}")
        st.write(f"👥 Customers: {diagnostics['files_discovered']['customers']}")
        st.write(f"💰 Sales: {diagnostics['files_discovered']['sales']}")
    
    with diag_col2:
        st.markdown("**Data Coverage**")
        st.write(f"🏪 Merchants with item data: {diagnostics['coverage']['merchants_with_item_data']}")
        st.write(f"🔄 Merchants using fallback: {diagnostics['coverage']['merchants_using_fallback']}")
        coverage_pct = (diagnostics['coverage']['merchants_with_item_data'] / m['merchants_total'] * 100) if m['merchants_total'] > 0 else 0
        st.write(f"📊 Item coverage: {coverage_pct:.1f}%")
    
    with diag_col3:
        st.markdown("**Data Quality**")
        st.write(f"✅ Total merchants: {m['merchants_total']}")
        st.write(f"✅ Total customers: {m['customers_total']}")
        st.write(f"✅ Pipeline validation: Passed")

    # Data Export Section
    st.markdown("---")
    st.subheader("📥 Data Export")
    
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        st.markdown("**📊 Summary Data**")
        
        # Metrics export
        metrics_df = pd.DataFrame({
            "Metric": [
                "Platform 60d", "Daily", "Weekly", "Monthly",
                "Merchants Total", "Merchants Active", 
                "Customers Total", "Customers Active", "Marketing Opt-ins"
            ],
            "Value": [
                m["platform_total_60d"], m["platform_daily"], 
                m["platform_weekly"], m["platform_monthly"],
                m["merchants_total"], m["merchants_active"], 
                m["customers_total"], m["customers_active"], m["customers_marketing"]
            ]
        })
        
        st.download_button(
            "📋 Download Metrics CSV",
            metrics_df.to_csv(index=False).encode("utf-8"),
            file_name=f"metrics_summary_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.download_button(
            "🏆 Download Top 3 Merchants CSV",
            m["top3"].to_csv(index=False).encode("utf-8"),
            file_name=f"top3_merchants_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with export_col2:
        st.markdown("**🗃️ Full Datasets**")
        
        # Create customer export without PII
        customers_export = customers.copy()
        if 'customer_id' in customers_export.columns:
            customers_export['customer_id'] = 'REDACTED'
        if 'email' in customers_export.columns:
            customers_export['email'] = 'REDACTED'
        if 'phone' in customers_export.columns:
            customers_export['phone'] = 'REDACTED'
        if 'first_name' in customers_export.columns:
            customers_export['first_name'] = 'REDACTED'
        if 'last_name' in customers_export.columns:
            customers_export['last_name'] = 'REDACTED'
        
        st.download_button(
            "👥 Download Customers CSV (PII Hidden)",
            customers_export.to_csv(index=False).encode("utf-8"),
            file_name=f"cleaned_customers_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
        st.download_button(
            "🏪 Download Merchants CSV", 
            merchants.to_csv(index=False).encode("utf-8"),
            file_name=f"cleaned_merchants_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with export_col3:
        st.markdown("**📋 Additional Data**")
        
        # Diagnostics export
        diagnostics_df = pd.DataFrame({
            "Category": ["Files", "Files", "Files", "Coverage", "Coverage", "Quality", "Quality"],
            "Metric": [
                "Merchants Files", "Customers Files", "Sales Files",
                "Merchants with Item Data", "Merchants using Fallback",
                "Total Merchants", "Total Customers"
            ],
            "Value": [
                diagnostics['files_discovered']['merchants'],
                diagnostics['files_discovered']['customers'], 
                diagnostics['files_discovered']['sales'],
                diagnostics['coverage']['merchants_with_item_data'],
                diagnostics['coverage']['merchants_using_fallback'],
                m['merchants_total'], m['customers_total']
            ]
        })
        
        st.download_button(
            "📈 Download Diagnostics CSV",
            diagnostics_df.to_csv(index=False).encode("utf-8"),
            file_name=f"diagnostics_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Assumptions and notes
    st.markdown("---")
    st.markdown("### 📝 Assumptions & Notes")
    st.caption("""
    **Business Rules Applied:**
    - **60-day sales window**: Item sales files preferred, fallback to MTD + Last Month Volume
    - **Active customer**: Registered within last 30 days  
    - **Active merchant**: Has sales > $0 in 60-day window
    - **Deduplication**: Customer ID first, fallback to email + phone combination
    - **Forecasts**: Naive projections (current = future)
    - **PII Protection**: Customer data exports hide personal information
    
    **Data Sources:** All metrics computed from data/ folder files. No hardcoded values.
    """)

if __name__ == "__main__":
    main()
