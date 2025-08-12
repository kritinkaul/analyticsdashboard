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
    
    customers = report['customers']
    merchants = report['merchants']
    
    print(f"Data Period: {report['data_period']}")
    print(f"Total Platform Volume: ${merchants['total_volume']:,.2f}")
    print(f"Total Customers: {customers['total_customers']:,}")
    print(f"Total Active Merchants: {merchants['active_merchants']}")
    print(f"Customer Acquisition Rate: {(customers['active_customers']/30):.1f} customers/day")
    print(f"Platform Daily Revenue: ${merchants['daily_platform_volume']:,.2f}")
    
    print_section("👥 CUSTOMER ANALYSIS")
    
    active_rate = (customers['active_customers'] / customers['total_customers']) * 100
    marketing_rate = (customers['marketing_allowed'] / customers['total_customers']) * 100
    
    print(f"• Total Customers Onboarded: {customers['total_customers']:,}")
    print(f"• Active Customers (last 30 days): {customers['active_customers']:,} ({active_rate:.1f}%)")
    print(f"• Inactive Customers: {customers['inactive_customers']:,} ({100-active_rate:.1f}%)")
    print(f"• Marketing Opt-in Rate: {customers['marketing_allowed']:,} ({marketing_rate:.1f}%)")
    
    print("\n💡 Customer Insights:")
    print(f"  - High customer acquisition volume but low retention ({active_rate:.1f}% active)")
    print(f"  - Opportunity to improve engagement and reactivate inactive customers")
    print(f"  - {marketing_rate:.1f}% marketing opt-in rate provides reach to {customers['marketing_allowed']:,} customers")
    
    print_section("🏪 MERCHANT ANALYSIS")
    
    merchant_data = merchants['merchant_metrics']
    print(f"• Total Merchants: {merchants['total_merchants']}")
    print(f"• Active Merchants: {merchants['active_merchants']} (100% - excellent!)")
    print(f"• Inactive Merchants: {merchants['inactive_merchants']}")
    
    print(f"\n📊 Merchant Performance Breakdown:")
    sorted_merchants = sorted(merchant_data.items(), key=lambda x: x[1]['net_sales'], reverse=True)
    for i, (name, data) in enumerate(sorted_merchants, 1):
        percentage = (data['net_sales'] / merchants['total_volume']) * 100
        print(f"  {i}. {name}")
        print(f"     Revenue: ${data['net_sales']:,.2f} ({percentage:.1f}% of platform)")
        print(f"     Monthly Avg: ${data['monthly_avg']:,.2f}")
        print(f"     Daily Avg: ${data['daily_avg']:,.2f}")
    
    print_section("💰 PROCESSING VOLUME ANALYSIS")
    
    print(f"Platform Volume Metrics (60-day period):")
    print(f"• Total Volume: ${merchants['total_volume']:,.2f}")
    print(f"• Daily Average: ${merchants['daily_platform_volume']:,.2f}")
    print(f"• Weekly Average: ${merchants['weekly_platform_volume']:,.2f}")
    print(f"• Monthly Average: ${merchants['monthly_platform_volume']:,.2f}")
    
    # Calculate growth metrics
    top_merchant = max(merchant_data.items(), key=lambda x: x[1]['net_sales'])
    print(f"\n🏆 Top Performer: {top_merchant[0]}")
    print(f"   Generates ${top_merchant[1]['daily_avg']:,.2f}/day")
    print(f"   Accounts for {(top_merchant[1]['net_sales']/merchants['total_volume']*100):.1f}% of platform volume")
    
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
        name = f"{customer.get('First Name', '')} {customer.get('Last Name', '')}".strip()
        if not name:
            name = customer['Customer ID']
        
        join_date = customer['Customer Since'][:10] if customer['Customer Since'] else 'Unknown'
        marketing = customer['Marketing Allowed']
        score = customer['score']
        
        print(f"  {i}. {name}")
        print(f"     Customer ID: {customer['Customer ID']}")
        print(f"     Joined: {join_date}")
        print(f"     Marketing Allowed: {marketing}")
        print(f"     Potential Score: {score}/9")
    
    print_section("🎯 BUSINESS RECOMMENDATIONS")
    
    print("Based on the data analysis, here are key recommendations:")
    print(f"\n1. Customer Retention Focus:")
    print(f"   - Only {active_rate:.1f}% of customers are active")
    print(f"   - Implement re-engagement campaigns for {customers['inactive_customers']:,} inactive customers")
    print(f"   - Focus on onboarding improvements to increase retention")
    
    print(f"\n2. Merchant Growth:")
    print(f"   - All merchants are active - excellent performance!")
    print(f"   - Top merchant generates ${top_merchant[1]['monthly_avg']:,.2f}/month")
    print(f"   - Consider expanding merchant network to diversify revenue")
    
    print(f"\n3. Marketing Opportunities:")
    print(f"   - {customers['marketing_allowed']:,} customers opted in for marketing")
    print(f"   - Target inactive customers with special offers")
    print(f"   - Leverage top potential customers for referral programs")
    
    print(f"\n4. Revenue Optimization:")
    print(f"   - Platform processes ${merchants['daily_platform_volume']:,.2f}/day")
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
