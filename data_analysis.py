#!/usr/bin/env python3
"""
Dashboard Data Analysis Script
Analyzes merchant, customer, and sales data to create comprehensive metrics
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
import glob
import os
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
import re

warnings.filterwarnings('ignore')

class DashboardAnalyzer:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.customers_df = None
        self.revenue_data = {}
        self.merchant_data = {}
        self.current_date = datetime(2025, 8, 8)  # Based on data timestamps
        
    def load_data(self):
        """Load all data files"""
        print("Loading data files...")
        
        # Load customer data
        customer_files = glob.glob(os.path.join(self.data_dir, "Customers-*.csv"))
        if customer_files:
            # Use the most recent customer file
            latest_customer_file = max(customer_files, key=os.path.getctime)
            print(f"Loading customer data from: {latest_customer_file}")
            self.customers_df = pd.read_csv(latest_customer_file)
            
        # Load revenue data
        revenue_files = glob.glob(os.path.join(self.data_dir, "*Revenue Item Sales*.csv"))
        for file in revenue_files:
            merchant_name = os.path.basename(file).split('-Revenue')[0]
            print(f"Loading revenue data for: {merchant_name}")
            self.revenue_data[merchant_name] = self.parse_revenue_file(file)
            
        # Load Excel files for merchant data
        excel_files = glob.glob(os.path.join(self.data_dir, "*.xlsx"))
        for file in excel_files:
            try:
                if 'customer_list' in file:
                    print(f"Loading additional customer data from: {file}")
                    excel_customers = pd.read_excel(file)
                    # Merge or update customer data if needed
                elif 'inventory' in file:
                    print(f"Loading inventory data from: {file}")
                    # Process inventory data if needed for merchant metrics
            except Exception as e:
                print(f"Error loading {file}: {e}")
                
    def parse_revenue_file(self, file_path):
        """Parse revenue item sales files"""
        import csv
        
        # Read the file and parse properly
        gross_sales = 0
        net_sales = 0
        date_range = ""
        
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            for i, row in enumerate(reader):
                if i > 20:  # Only check first 20 rows for summary
                    break
                    
                if len(row) >= 2:
                    if row[0].strip() == 'Gross Sales':
                        try:
                            gross_sales_str = row[1].strip().replace('"', '').replace('$', '').replace(',', '')
                            gross_sales = float(gross_sales_str)
                        except Exception as e:
                            print(f"Error parsing gross sales: {row}, error: {e}")
                    elif row[0].strip() == 'Net Sales':
                        try:
                            net_sales_str = row[1].strip().replace('"', '').replace('$', '').replace(',', '')
                            net_sales = float(net_sales_str)
                        except Exception as e:
                            print(f"Error parsing net sales: {row}, error: {e}")
                    elif 'AM -' in str(row) and 'PM' in str(row):
                        date_range = ' '.join(row).strip().replace('"', '')
                
        print(f"Parsed {os.path.basename(file_path)}: Gross=${gross_sales:,.2f}, Net=${net_sales:,.2f}")
                
        return {
            'gross_sales': gross_sales,
            'net_sales': net_sales,
            'date_range': date_range,
            'file_path': file_path
        }
    
    def analyze_customers(self):
        """Analyze customer data"""
        if self.customers_df is None:
            return {}
            
        print("Analyzing customer data...")
        
        # Clean and process customer data
        # Handle the datetime format: "07-Aug-2025 08:17 PM EDT"
        self.customers_df['Customer Since'] = pd.to_datetime(
            self.customers_df['Customer Since'].str.replace(' EDT', ''), 
            format='%d-%b-%Y %I:%M %p', 
            errors='coerce'
        )
        
        # Total customers
        total_customers = len(self.customers_df)
        
        # Active customers (registered within last 30 days)
        cutoff_date = self.current_date - timedelta(days=30)
        active_customers = len(self.customers_df[self.customers_df['Customer Since'] >= cutoff_date])
        inactive_customers = total_customers - active_customers
        
        # Customers with marketing allowed
        marketing_allowed = len(self.customers_df[self.customers_df['Marketing Allowed'] == 'Yes'])
        
        # Daily registration trend (last 30 days)
        recent_customers = self.customers_df[self.customers_df['Customer Since'] >= cutoff_date].copy()
        if not recent_customers.empty:
            recent_customers['Date'] = recent_customers['Customer Since'].dt.date
            daily_registrations = recent_customers.groupby('Date').size()
        else:
            daily_registrations = pd.Series(dtype=int)
            
        return {
            'total_customers': total_customers,
            'active_customers': active_customers,
            'inactive_customers': inactive_customers,
            'marketing_allowed': marketing_allowed,
            'daily_registrations': daily_registrations
        }
    
    def analyze_merchants(self):
        """Analyze merchant data from revenue files"""
        print("Analyzing merchant data...")
        
        total_merchants = len(self.revenue_data)
        active_merchants = 0
        inactive_merchants = 0
        
        merchant_metrics = {}
        total_volume = 0
        
        for merchant_name, data in self.revenue_data.items():
            gross_sales = data['gross_sales']
            net_sales = data['net_sales']
            date_range = data['date_range']
            
            # Extract date range to determine if merchant is active
            # Based on the data, it appears to be 60-day period data
            days_in_period = 60  # Assuming 2 months as mentioned
            
            # Calculate daily average
            daily_avg = net_sales / days_in_period if days_in_period > 0 else 0
            weekly_avg = daily_avg * 7
            monthly_avg = daily_avg * 30
            
            # Consider active if they have sales in the period
            is_active = net_sales > 0
            if is_active:
                active_merchants += 1
            else:
                inactive_merchants += 1
                
            merchant_metrics[merchant_name] = {
                'gross_sales': gross_sales,
                'net_sales': net_sales,
                'daily_avg': daily_avg,
                'weekly_avg': weekly_avg,
                'monthly_avg': monthly_avg,
                'is_active': is_active,
                'date_range': date_range
            }
            
            total_volume += net_sales
            
        return {
            'total_merchants': total_merchants,
            'active_merchants': active_merchants,
            'inactive_merchants': inactive_merchants,
            'merchant_metrics': merchant_metrics,
            'total_volume': total_volume,
            'daily_platform_volume': total_volume / 60,  # 60 days of data
            'weekly_platform_volume': (total_volume / 60) * 7,
            'monthly_platform_volume': (total_volume / 60) * 30
        }
    
    def predict_sales(self, merchant_metrics):
        """Predict sales for next 2 months and same period next year"""
        print("Generating sales predictions...")
        
        predictions = {}
        
        for merchant_name, metrics in merchant_metrics.items():
            daily_avg = metrics['daily_avg']
            
            # Simple linear trend prediction (assuming current performance continues)
            # For next 2 months (60 days)
            next_2_months = daily_avg * 60
            
            # For same period next year (assuming 10% growth)
            # This is a conservative estimate based on business growth patterns
            growth_factor = 1.10  # 10% annual growth assumption
            same_period_next_year = next_2_months * growth_factor
            
            predictions[merchant_name] = {
                'next_2_months': next_2_months,
                'same_period_next_year': same_period_next_year,
                'current_monthly_avg': metrics['monthly_avg']
            }
            
        return predictions
    
    def identify_top_customers(self):
        """Identify top 3 most valuable/potential customers based on available data"""
        print("Identifying top customers...")
        
        if self.customers_df is None:
            return []
            
        # Since we don't have transaction-level customer data, we'll identify based on:
        # 1. Recent registration (potential)
        # 2. Marketing acceptance (engagement potential)
        # 3. Complete profile information (value indicator)
        
        # Score customers
        customer_scores = self.customers_df.copy()
        customer_scores['score'] = 0
        
        # Recent customers (last 7 days) get higher potential score
        recent_cutoff = self.current_date - timedelta(days=7)
        customer_scores.loc[customer_scores['Customer Since'] >= recent_cutoff, 'score'] += 3
        
        # Marketing allowed indicates engagement potential
        customer_scores.loc[customer_scores['Marketing Allowed'] == 'Yes', 'score'] += 2
        
        # Complete profile (has name) indicates higher value
        customer_scores.loc[customer_scores['First Name'].notna() & 
                          customer_scores['Last Name'].notna(), 'score'] += 2
        
        # Has phone number
        customer_scores.loc[customer_scores['Phone Number'].notna(), 'score'] += 1
        
        # Has email
        customer_scores.loc[customer_scores['Email Address'].notna(), 'score'] += 1
        
        # Get top 3
        top_customers = customer_scores.nlargest(3, 'score')[
            ['Customer ID', 'First Name', 'Last Name', 'Customer Since', 'Marketing Allowed', 'score']
        ]
        
        return top_customers.to_dict('records')
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("Generating comprehensive report...")
        
        # Load all data
        self.load_data()
        
        # Analyze each component
        customer_analysis = self.analyze_customers()
        merchant_analysis = self.analyze_merchants()
        sales_predictions = self.predict_sales(merchant_analysis['merchant_metrics'])
        top_customers = self.identify_top_customers()
        
        # Compile report
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_period': '60 days (Feb 7, 2025 - Aug 8, 2025)',
            'customers': customer_analysis,
            'merchants': merchant_analysis,
            'predictions': sales_predictions,
            'top_customers': top_customers
        }
        
        return report
    
    def print_summary(self, report):
        """Print a summary of the analysis"""
        print("\n" + "="*60)
        print("DASHBOARD DATA ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"\nData Period: {report['data_period']}")
        print(f"Analysis Generated: {report['timestamp']}")
        
        # Customer Summary
        print(f"\n📊 CUSTOMER METRICS:")
        print(f"  • Total Customers: {report['customers']['total_customers']:,}")
        print(f"  • Active Customers (last 30 days): {report['customers']['active_customers']:,}")
        print(f"  • Inactive Customers: {report['customers']['inactive_customers']:,}")
        print(f"  • Marketing Opt-ins: {report['customers']['marketing_allowed']:,}")
        
        # Merchant Summary  
        print(f"\n🏪 MERCHANT METRICS:")
        print(f"  • Total Merchants: {report['merchants']['total_merchants']}")
        print(f"  • Active Merchants: {report['merchants']['active_merchants']}")
        print(f"  • Inactive Merchants: {report['merchants']['inactive_merchants']}")
        
        # Volume Summary
        print(f"\n💰 PROCESSING VOLUME:")
        print(f"  • Total Volume (60 days): ${report['merchants']['total_volume']:,.2f}")
        print(f"  • Daily Average: ${report['merchants']['daily_platform_volume']:,.2f}")
        print(f"  • Weekly Average: ${report['merchants']['weekly_platform_volume']:,.2f}")
        print(f"  • Monthly Average: ${report['merchants']['monthly_platform_volume']:,.2f}")
        
        # Top Merchants by Volume
        print(f"\n🏆 TOP MERCHANTS BY VOLUME:")
        sorted_merchants = sorted(
            report['merchants']['merchant_metrics'].items(),
            key=lambda x: x[1]['net_sales'],
            reverse=True
        )
        for i, (name, metrics) in enumerate(sorted_merchants[:3], 1):
            print(f"  {i}. {name}: ${metrics['net_sales']:,.2f} (${metrics['monthly_avg']:,.2f}/month)")
        
        # Sales Predictions
        print(f"\n🔮 SALES PREDICTIONS (Next 2 Months):")
        total_predicted = sum(p['next_2_months'] for p in report['predictions'].values())
        print(f"  • Platform Total: ${total_predicted:,.2f}")
        
        for name, pred in list(report['predictions'].items())[:3]:
            print(f"  • {name}: ${pred['next_2_months']:,.2f}")
        
        # Top Customers
        print(f"\n⭐ TOP 3 POTENTIAL CUSTOMERS:")
        for i, customer in enumerate(report['top_customers'], 1):
            name = f"{customer.get('First Name', '')} {customer.get('Last Name', '')}".strip()
            if not name:
                name = customer['Customer ID']
            print(f"  {i}. {name} (Score: {customer['score']}, Joined: {customer['Customer Since']})")
        
        print("\n" + "="*60)


def main():
    """Main execution function"""
    data_dir = "/Users/kritinkaul/Downloads/DashboardData (1) 2"
    
    # Initialize analyzer
    analyzer = DashboardAnalyzer(data_dir)
    
    # Generate report
    report = analyzer.generate_report()
    
    # Print summary
    analyzer.print_summary(report)    # Save detailed report to JSON
    import json
    with open(os.path.join(data_dir, 'analysis_report.json'), 'w') as f:
        # Convert datetime objects to strings for JSON serialization
        json_report = report.copy()
        if 'daily_registrations' in json_report['customers']:
            daily_reg = json_report['customers']['daily_registrations']
            if hasattr(daily_reg, 'to_dict'):
                # Convert pandas series with date index to string keys
                json_report['customers']['daily_registrations'] = {
                    str(k): v for k, v in daily_reg.to_dict().items()
                }
        
        json.dump(json_report, f, indent=2, default=str)
    
    print(f"\nDetailed report saved to: {os.path.join(data_dir, 'analysis_report.json')}")
    
    return report

if __name__ == "__main__":
    report = main()
