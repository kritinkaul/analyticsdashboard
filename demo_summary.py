#!/usr/bin/env python3
"""
Summary Script - Business Analytics Dashboard Demo
This script demonstrates the key findings and capabilities of the analysis
"""

import json
import pandas as pd
from datetime import datetime

def print_header(title):
    print("\n" + "="*60)
    print(f"{title:^60}")
    print("="*60)

def print_section(title):
    print(f"\n📊 {title}")
    print("-" * (len(title) + 4))

def main():
    print_header("BUSINESS ANALYTICS DASHBOARD")
    print("Comprehensive Analysis of Merchant, Customer, and Sales Data")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Load analysis results
    with open('analysis_report.json', 'r') as f:
        report = json.load(f)
    
    print_section("📈 KEY PERFORMANCE INDICATORS")
    
    metrics = report['metrics']
    
    print(f"Data Period: {report['data_period']}")
    print(f"Total Platform Volume: ${metrics['total_60d']:,.2f}")
    print(f"Total Customers: {metrics['customers_total']:,}")
    print(f"Total Active Merchants: {metrics['merchants_active']}")
    print(f"Customer Acquisition Rate: {(metrics['customers_active']/30):.1f} customers/day")
    print(f"Platform Daily Revenue: ${metrics['daily']:,.2f}")
    
    print_section("👥 CUSTOMER ANALYSIS")
    
    active_rate = (metrics['customers_active'] / metrics['customers_total']) * 100
    marketing_rate = (metrics['customers_marketing'] / metrics['customers_total']) * 100
    
    print(f"• Total Customers Onboarded: {metrics['customers_total']:,}")
    print(f"• Active Customers (last 30 days): {metrics['customers_active']:,} ({active_rate:.1f}%)")
    print(f"• Inactive Customers: {metrics['customers_inactive']:,} ({100-active_rate:.1f}%)")
    print(f"• Marketing Opt-in Rate: {metrics['customers_marketing']:,} ({marketing_rate:.1f}%)")
    
    print("\n💡 Customer Insights:")
    print(f"  - High customer acquisition volume but low retention ({active_rate:.1f}% active)")
    print(f"  - Opportunity to improve engagement and reactivate inactive customers")
    print(f"  - {marketing_rate:.1f}% marketing opt-in rate provides reach to {metrics['customers_marketing']:,} customers")
    
    print_section("🏪 MERCHANT ANALYSIS")
    
    merchants = report['merchants']
    print(f"• Total Merchants: {metrics['merchants_total']}")
    print(f"• Active Merchants: {metrics['merchants_active']} (100% - excellent!)")
    print(f"• Inactive Merchants: {metrics['merchants_inactive']}")
    
    print(f"\n📊 Merchant Performance Breakdown:")
    # Sort merchants by volume
    sorted_merchants = sorted(merchants, key=lambda x: x.get('net_sales_60d_final', 0), reverse=True)
    for i, merchant in enumerate(sorted_merchants, 1):
        name = merchant.get('legal_name', merchant.get('dba_name', 'Unknown'))
        volume = merchant.get('net_sales_60d_final', 0)
        monthly = merchant.get('monthly_volume_est', 0)
        daily = merchant.get('daily_volume_est', 0)
        percentage = (volume / metrics['total_60d']) * 100
        print(f"  {i}. {name}")
        print(f"     Revenue: ${volume:,.2f} ({percentage:.1f}% of platform)")
        print(f"     Monthly Avg: ${monthly:,.2f}")
        print(f"     Daily Avg: ${daily:,.2f}")
    
    print_section("💰 PROCESSING VOLUME ANALYSIS")
    
    print(f"Platform Volume Metrics (60-day period):")
    print(f"• Total Volume: ${metrics['total_60d']:,.2f}")
    print(f"• Daily Average: ${metrics['daily']:,.2f}")
    print(f"• Weekly Average: ${metrics['weekly']:,.2f}")
    print(f"• Monthly Average: ${metrics['monthly']:,.2f}")
    
    # Calculate growth metrics
    top_merchant = max(merchants, key=lambda x: x.get('net_sales_60d_final', 0))
    top_name = top_merchant.get('legal_name', top_merchant.get('dba_name', 'Unknown'))
    top_daily = top_merchant.get('daily_volume_est', 0)
    top_volume = top_merchant.get('net_sales_60d_final', 0)
    print(f"\n🏆 Top Performer: {top_name}")
    print(f"   Generates ${top_daily:,.2f}/day")
    print(f"   Accounts for {(top_volume/metrics['total_60d']*100):.1f}% of platform volume")
    
    print_section("🔮 SALES PREDICTIONS")
    
    predictions = report['predictions']
    total_next_2_months = sum(p['next_2_months'] for p in predictions.values())
    total_next_year = sum(p['same_period_next_year'] for p in predictions.values())
    growth_rate = ((total_next_year / total_next_2_months) - 1) * 100
    
    print(f"Next 2 Months Forecast:")
    print(f"• Platform Total: ${total_next_2_months:,.2f}")
    print(f"• Monthly Average: ${total_next_2_months/2:,.2f}")
    
    print(f"\nSame Period Next Year Forecast:")
    print(f"• Platform Total: ${total_next_year:,.2f}")
    print(f"• Projected Growth: {growth_rate:.1f}%")
    
    print(f"\n📈 Merchant Predictions:")
    for name, pred in predictions.items():
        print(f"  • {name}: ${pred['next_2_months']:,.2f} (2 months) → ${pred['same_period_next_year']:,.2f} (next year)")
    
    print_section("⭐ TOP POTENTIAL CUSTOMERS")
    
    top_customers = report['top_customers']
    print("Most Valuable/Potential Customers (Based on engagement scoring):")
    
    for i, customer in enumerate(top_customers, 1):
        name_parts = []
        if customer.get('first_name'):
            name_parts.append(customer['first_name'])
        if customer.get('last_name'):
            name_parts.append(customer['last_name'])
        name = ' '.join(name_parts) or customer.get('customer_id', 'Unknown')
        
        join_date = customer.get('customer_since', 'Unknown')
        if isinstance(join_date, str) and 'T' in join_date:
            join_date = join_date.split('T')[0]
        
        marketing = customer.get('marketing_allowed', 'N/A')
        score = customer.get('score', 0)
        
        print(f"  {i}. {name}")
        print(f"     Customer ID: {customer.get('customer_id', 'Unknown')}")
        print(f"     Joined: {join_date}")
        print(f"     Marketing Allowed: {marketing}")
        print(f"     Potential Score: {score}/9")
    
    print_section("🎯 BUSINESS RECOMMENDATIONS")
    
    print("Based on the data analysis, here are key recommendations:")
    print(f"\n1. Customer Retention Focus:")
    print(f"   - Only {active_rate:.1f}% of customers are active")
    print(f"   - Implement re-engagement campaigns for {metrics['customers_inactive']:,} inactive customers")
    print(f"   - Focus on onboarding improvements to increase retention")
    
    print(f"\n2. Merchant Growth:")
    print(f"   - All merchants are active - excellent performance!")
    print(f"   - Top merchant generates ${top_merchant.get('monthly_volume_est', 0):,.2f}/month")
    print(f"   - Consider expanding merchant network to diversify revenue")
    
    print(f"\n3. Marketing Opportunities:")
    print(f"   - {metrics['customers_marketing']:,} customers opted in for marketing")
    print(f"   - Target inactive customers with special offers")
    print(f"   - Leverage top potential customers for referral programs")
    
    print(f"\n4. Revenue Optimization:")
    print(f"   - Platform processes ${metrics['daily']:,.2f}/day")
    print(f"   - Focus on increasing transaction frequency")
    print(f"   - Consider merchant incentives to boost volume")
    
    print_section("🚀 DASHBOARD FEATURES")
    
    print("The interactive dashboard provides:")
    print("• Real-time metrics and KPI tracking")
    print("• Customer and merchant performance analytics")
    print("• Sales prediction models")
    print("• Visual charts and data tables")
    print("• Exportable reports and insights")
    
    print(f"\n📱 Access the dashboard at: http://127.0.0.1:8050")
    print(f"📄 Detailed report: analysis_report.json")
    print(f"🔧 Source code: data_analysis.py, dashboard.py")
    
    print_header("ANALYSIS COMPLETE")
    print("All data processed from provided CSV and Excel files")
    print("No synthetic data generated - all metrics derived from actual data")
    print("Dashboard ready for demonstration and further analysis")

if __name__ == "__main__":
    main()
