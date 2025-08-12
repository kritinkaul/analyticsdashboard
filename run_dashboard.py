#!/usr/bin/env python3
"""
Alternative way to run the dashboard without Streamlit connection issues
"""
import sys
import os
import pandas as pd
from pathlib import Path

# Add src to path
sys.path.append('src')

# Import our ETL
from etl import run_pipeline_from_folders

def print_analytics_report():
    """Generate a static analytics report"""
    print("="*60)
    print("PAYMENT PLATFORM ANALYTICS REPORT")
    print("="*60)
    
    # Run the ETL pipeline
    result = run_pipeline_from_folders()
    
    customers = result['customers']
    merchants = result['merchants_enriched']
    metrics = result['metrics']
    
    print(f"\n📊 OVERVIEW:")
    print(f"  • Total Customers: {len(customers):,}")
    print(f"  • Active Customers (30d): {customers['active_flag'].sum():,}")
    print(f"  • Marketing Opt-ins: {customers['marketing_opt_in'].sum():,}")
    print(f"  • Total Merchants: {len(merchants):,}")
    print(f"  • Active Merchants: {merchants['active_flag'].sum():,}")
    
    print(f"\n💰 FINANCIAL METRICS:")
    print(f"  • Total Platform Revenue (60d): ${metrics['total_60d']:,.2f}")
    print(f"  • Daily Average: ${metrics['daily_avg']:,.2f}")
    print(f"  • Weekly Average: ${metrics['weekly_avg']:,.2f}")
    print(f"  • Monthly Average: ${metrics['monthly_avg']:,.2f}")
    
    print(f"\n🏆 TOP 3 MERCHANTS:")
    top3 = merchants.nlargest(3, 'net_sales_60d')[['legal_name', 'net_sales_60d']]
    for i, (_, row) in enumerate(top3.iterrows(), 1):
        print(f"  {i}. {row['legal_name']}: ${row['net_sales_60d']:,.2f}")
    
    print(f"\n📈 CUSTOMER BREAKDOWN:")
    active_pct = (customers['active_flag'].sum() / len(customers)) * 100
    marketing_pct = (customers['marketing_opt_in'].sum() / len(customers)) * 100
    print(f"  • Active Rate: {active_pct:.1f}%")
    print(f"  • Marketing Opt-in Rate: {marketing_pct:.1f}%")
    
    print(f"\n🏪 MERCHANT BREAKDOWN:")
    active_merchant_pct = (merchants['active_flag'].sum() / len(merchants)) * 100
    print(f"  • Active Rate: {active_merchant_pct:.1f}%")
    
    # Export data
    print(f"\n📁 EXPORTING DATA:")
    customers.to_csv('customers_export.csv', index=False)
    merchants.to_csv('merchants_export.csv', index=False)
    print(f"  • customers_export.csv: {len(customers):,} rows")
    print(f"  • merchants_export.csv: {len(merchants):,} rows")
    
    print("="*60)

if __name__ == "__main__":
    print_analytics_report()
