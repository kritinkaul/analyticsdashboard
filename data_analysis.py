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
import io
from pathlib import Path

warnings.filterwarnings('ignore')

# Constants
TODAY = pd.Timestamp("2025-08-11")

class DashboardAnalyzer:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.customers_df = None
        self.merchants_df = None
        self.sales_df = None
        self.current_date = TODAY
        
        # File discovery
        self.discover_files()
        
    def discover_files(self):
        """Discover all data files in the directory"""
        print("Discovering data files...")
        
        # Find merchant files (Excel)
        self.merchant_files = (glob.glob(os.path.join(self.data_dir, "**/*customer_list*.[xX][lL][sS][xX]"), recursive=True) +
                              glob.glob(os.path.join(self.data_dir, "**/*customer_list*.[xX][lL][sS]"), recursive=True) +
                              glob.glob(os.path.join(self.data_dir, "**/*merchant*.[xX][lL][sS][xX]"), recursive=True) +
                              glob.glob(os.path.join(self.data_dir, "**/*merchant*.[xX][lL][sS]"), recursive=True))
        
        # Find customer files (CSV)
        self.customer_files = glob.glob(os.path.join(self.data_dir, "**/Customers-*.[cC][sS][vV]"), recursive=True)
        
        # Find sales files (Revenue Item Sales CSV)
        self.sales_files = glob.glob(os.path.join(self.data_dir, "**/*Revenue Item Sales*.[cC][sS][vV]"), recursive=True)
        
        print(f"Found merchants: {len(self.merchant_files)}, customers: {len(self.customer_files)}, sales: {len(self.sales_files)}")
        
    def parse_currency(self, s):
        """Parse currency strings to numeric values"""
        return pd.to_numeric(pd.Series(s, dtype=str).str.replace(r"[^\d\.\-]", "", regex=True), errors="coerce")
    
    def load_customers(self):
        """Load and merge customer data with deduplication and active flag"""
        print("Loading and processing customer data...")
        
        if not self.customer_files:
            print("No customer files found")
            return pd.DataFrame()
            
        dfs = []
        for p in self.customer_files:
            print(f"  Loading: {os.path.basename(p)}")
            df = pd.read_csv(p, low_memory=False, encoding='utf-8-sig')
            df.columns = [c.strip().replace("\n", " ").replace("\r", " ") for c in df.columns]
            dfs.append(df)
            
        if not dfs:
            return pd.DataFrame()
            
        big = pd.concat(dfs, ignore_index=True, sort=False)
        
        # Find relevant columns
        idc = next((c for c in big.columns if c.lower() in ["customer id", "customerid", "id"]), None)
        fn = next((c for c in big.columns if "first" in c.lower() and "name" in c.lower()), None)
        ln = next((c for c in big.columns if "last" in c.lower() and "name" in c.lower()), None)
        em = next((c for c in big.columns if "email" in c.lower()), None)
        ph = next((c for c in big.columns if "phone" in c.lower()), None)
        cs = next((c for c in big.columns if "customer since" in c.lower() or "join" in c.lower()), None)
        ma = next((c for c in big.columns if "marketing" in c.lower() and "allow" in c.lower()), None)
        
        out = pd.DataFrame()
        if idc: out["customer_id"] = big[idc]
        if fn: out["first_name"] = big[fn]
        if ln: out["last_name"] = big[ln]
        if em: out["email"] = big[em]
        if ph: out["phone"] = big[ph]
        if ma: out["marketing_allowed"] = big[ma]
        
        # Parse customer since date
        if cs:
            # Handle the format: "07-Aug-2025 08:17 PM EDT"
            date_series = big[cs].astype(str).str.replace(' EDT', '').str.replace(' EST', '')
            out["customer_since"] = pd.to_datetime(date_series, format='%d-%b-%Y %I:%M %p', errors="coerce")
        else:
            out["customer_since"] = pd.NaT
            
        # Deduplication
        if "customer_id" in out.columns:
            out = out.drop_duplicates("customer_id")
        elif {"email", "phone"}.issubset(out.columns):
            out["__key"] = out[["email", "phone"]].astype(str).agg("|".join, axis=1)
            out = out.drop_duplicates("__key")
            out = out.drop(columns=["__key"])
        else:
            out = out.drop_duplicates()
            
        # Active flag (registered within last 30 days)
        out["active_flag"] = (TODAY - out["customer_since"]).dt.days.between(0, 30, inclusive="left")
        
        print(f"  Processed {len(out)} unique customers")
        return out
    
    def parse_items_report_csv(self, path):
        """Parse items report CSV files"""
        try:
            with open(path, "r", encoding="utf-8-sig", errors="ignore") as f:
                lines = f.readlines()
                
            # Find header line with Net Sales
            hdr = next((i for i, ln in enumerate(lines[:200]) 
                       if "Name" in ln and "Net Sales" in ln and "," in ln), None)
            
            if hdr is None:
                # Try to find summary data instead
                gross_sales = 0
                net_sales = 0
                
                import csv
                with open(path, 'r', encoding='utf-8-sig') as f:
                    reader = csv.reader(f)
                    for i, row in enumerate(reader):
                        if i > 20:  # Only check first 20 rows for summary
                            break
                            
                        if len(row) >= 2:
                            if row[0].strip() == 'Gross Sales':
                                try:
                                    gross_sales_str = row[1].strip().replace('"', '').replace('$', '').replace(',', '')
                                    gross_sales = float(gross_sales_str)
                                except:
                                    pass
                            elif row[0].strip() == 'Net Sales':
                                try:
                                    net_sales_str = row[1].strip().replace('"', '').replace('$', '').replace(',', '')
                                    net_sales = float(net_sales_str)
                                except:
                                    pass
                
                return pd.DataFrame({"Net Sales_num": [net_sales]}) if net_sales > 0 else None
                
            # Parse detailed data
            df = pd.read_csv(io.StringIO("".join(lines[hdr:])), engine="python")
            if "Net Sales" in df.columns:
                df["Net Sales_num"] = self.parse_currency(df["Net Sales"])
            return df
            
        except Exception as e:
            print(f"Error parsing {path}: {e}")
            return None
    
    def load_sales(self):
        """Load and aggregate sales data"""
        print("Loading sales data...")
        
        out = []
        for p in self.sales_files:
            print(f"  Processing: {os.path.basename(p)}")
            df = self.parse_items_report_csv(p)
            if df is not None:
                merchant_key = Path(p).name.split("-Revenue Item Sales")[0].strip().upper()
                net_sales = df["Net Sales_num"].sum() if "Net Sales_num" in df.columns else 0
                out.append(pd.DataFrame({
                    "merchant_name_key": [merchant_key],
                    "net_sales_60d": [net_sales]
                }))
                print(f"    Extracted ${net_sales:,.2f} for {merchant_key}")
                
        return pd.concat(out, ignore_index=True) if out else pd.DataFrame(columns=["merchant_name_key", "net_sales_60d"])
    
    def load_merchants(self):
        """Load merchant data from Excel files"""
        print("Loading merchant data...")
        
        if not self.merchant_files:
            print("No merchant files found, creating from sales data")
            return pd.DataFrame()
            
        dfs = []
        for p in self.merchant_files:
            try:
                print(f"  Loading: {os.path.basename(p)}")
                df = pd.read_excel(p)
                df.columns = [c.strip().replace("\n", " ").replace("\r", " ") for c in df.columns]
                dfs.append(df)
            except Exception as e:
                print(f"  Error loading {p}: {e}")
                
        if not dfs:
            return pd.DataFrame()
            
        # For now, return empty since we don't have actual merchant list files
        # We'll create merchants from sales data
        return pd.DataFrame()
    
    def coalesce_sales(self, merchants_df, sales_agg):
        """Coalesce merchant data with sales data"""
        print("Coalescing merchant and sales data...")
        
        if merchants_df.empty:
            # Create merchant records from sales data
            merchants = []
            for _, row in sales_agg.iterrows():
                merchant_name = row["merchant_name_key"]
                merchants.append({
                    "merchant_id": merchant_name,
                    "legal_name": merchant_name.title(),
                    "dba_name": merchant_name.title(),
                    "merchant_name_key": merchant_name,
                    "net_sales_60d": row["net_sales_60d"],
                    "net_sales_60d_final": row["net_sales_60d"]
                })
            m = pd.DataFrame(merchants)
        else:
            m = merchants_df.copy().rename(columns=str.lower)
            s = sales_agg.copy()
            
            # Create merchant key for matching
            name_col = next((c for c in m.columns if "name" in c.lower()), None)
            if name_col:
                m["merchant_name_key"] = m[name_col].astype(str).str.strip().str.upper()
            
            # Rename columns
            m = m.rename(columns={
                "customer id": "merchant_id", 
                "legal business name": "legal_name",
                "dba name": "dba_name", 
                "mtd volume": "mtd_volume", 
                "last month volume": "last_month_volume"
            })
            
            for c in ["mtd_volume", "last_month_volume"]:
                if c in m.columns: 
                    m[c] = self.parse_currency(m[c])
            
            m = m.merge(s, on="merchant_name_key", how="left")
            fallback = m.get("mtd_volume", 0).fillna(0) + m.get("last_month_volume", 0).fillna(0)
            m["net_sales_60d_final"] = np.where(m["net_sales_60d"].notna(), m["net_sales_60d"], fallback)
        
        # Calculate derived metrics
        m["active_flag"] = m["net_sales_60d_final"] > 0
        m["daily_volume_est"] = m["net_sales_60d_final"] / 60.0
        m["weekly_volume_est"] = m["net_sales_60d_final"] * 7.0 / 60.0
        m["monthly_volume_est"] = m["net_sales_60d_final"] / 2.0
        
        print(f"  Processed {len(m)} merchants")
        return m
    
    def compute_metrics(self, merchants_enriched, customers):
        """Compute comprehensive business metrics"""
        print("Computing business metrics...")
        
        total_60d = float(merchants_enriched["net_sales_60d_final"].sum())
        daily, weekly, monthly = total_60d/60.0, total_60d*7/60.0, total_60d/2.0
        
        # Customer metrics
        customers_marketing = customers["marketing_allowed"].eq("Yes").sum() if "marketing_allowed" in customers.columns else 0
        
        # Top 3 merchants
        top3 = (merchants_enriched.sort_values("net_sales_60d_final", ascending=False)
                [["legal_name", "dba_name", "net_sales_60d_final"]].head(3)
                .rename(columns={"net_sales_60d_final": "net_sales_60d"}))
        
        return {
            "merchants_total": int(len(merchants_enriched)),
            "merchants_active": int(merchants_enriched["active_flag"].sum()),
            "merchants_inactive": int(len(merchants_enriched) - merchants_enriched["active_flag"].sum()),
            "customers_total": int(len(customers)),
            "customers_active": int(customers["active_flag"].sum()),
            "customers_inactive": int(len(customers) - customers["active_flag"].sum()),
            "customers_marketing": int(customers_marketing),
            "total_60d": round(total_60d, 2),
            "daily": round(daily, 2),
            "weekly": round(weekly, 2),
            "monthly": round(monthly, 2),
            "top3": top3
        }
    
    def predict_sales(self, merchants_enriched):
        """Predict sales for next 2 months and same period next year"""
        print("Generating sales predictions...")
        
        predictions = {}
        
        for _, merchant in merchants_enriched.iterrows():
            merchant_name = merchant.get("legal_name", merchant.get("dba_name", "Unknown"))
            daily_avg = merchant["daily_volume_est"]
            
            # For next 2 months (60 days)
            next_2_months = daily_avg * 60
            
            # For same period next year (assuming 10% growth)
            growth_factor = 1.10  # 10% annual growth assumption
            same_period_next_year = next_2_months * growth_factor
            
            predictions[merchant_name] = {
                'next_2_months': next_2_months,
                'same_period_next_year': same_period_next_year,
                'current_monthly_avg': merchant["monthly_volume_est"]
            }
            
        return predictions
    
    def identify_top_customers(self, customers):
        """Identify top 3 most valuable/potential customers"""
        print("Identifying top customers...")
        
        if customers.empty:
            return []
            
        # Score customers
        customer_scores = customers.copy()
        customer_scores['score'] = 0
        
        # Recent customers (last 7 days) get higher potential score
        recent_cutoff = TODAY - timedelta(days=7)
        customer_scores.loc[customer_scores['customer_since'] >= recent_cutoff, 'score'] += 3
        
        # Marketing allowed indicates engagement potential
        if "marketing_allowed" in customer_scores.columns:
            customer_scores.loc[customer_scores['marketing_allowed'] == 'Yes', 'score'] += 2
        
        # Complete profile (has name) indicates higher value
        if "first_name" in customer_scores.columns and "last_name" in customer_scores.columns:
            customer_scores.loc[customer_scores['first_name'].notna() & 
                              customer_scores['last_name'].notna(), 'score'] += 2
        
        # Has phone number
        if "phone" in customer_scores.columns:
            customer_scores.loc[customer_scores['phone'].notna(), 'score'] += 1
        
        # Has email
        if "email" in customer_scores.columns:
            customer_scores.loc[customer_scores['email'].notna(), 'score'] += 1
        
        # Get top 3
        cols_to_select = ['customer_id', 'score']
        if "first_name" in customer_scores.columns:
            cols_to_select.append('first_name')
        if "last_name" in customer_scores.columns:
            cols_to_select.append('last_name')
        if "customer_since" in customer_scores.columns:
            cols_to_select.append('customer_since')
        if "marketing_allowed" in customer_scores.columns:
            cols_to_select.append('marketing_allowed')
            
        top_customers = customer_scores.nlargest(3, 'score')[cols_to_select]
        
        return top_customers.to_dict('records')
    
    def generate_report(self):
        """Generate comprehensive analysis report"""
        print("Generating comprehensive report...")
        
        # Load all data using improved methods
        customers = self.load_customers()
        sales_agg = self.load_sales()
        merchants_raw = self.load_merchants()
        merchants_enriched = self.coalesce_sales(merchants_raw, sales_agg)
        
        # Compute metrics
        metrics = self.compute_metrics(merchants_enriched, customers)
        sales_predictions = self.predict_sales(merchants_enriched)
        top_customers = self.identify_top_customers(customers)
        
        # Compile report
        report = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_period': '60 days (Feb 7, 2025 - Aug 8, 2025)',
            'metrics': metrics,
            'merchants': merchants_enriched.to_dict('records'),
            'predictions': sales_predictions,
            'top_customers': top_customers,
            'raw_customer_count': len(customers),
            'customer_sample': customers.head(10).to_dict('records') if not customers.empty else []
        }
        
        return report
    
    def print_summary(self, report):
        """Print a summary of the analysis"""
        print("\n" + "="*60)
        print("DASHBOARD DATA ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"\nData Period: {report['data_period']}")
        print(f"Analysis Generated: {report['timestamp']}")
        
        metrics = report['metrics']
        
        # Customer Summary
        print(f"\n📊 CUSTOMER METRICS:")
        print(f"  • Total Customers: {metrics['customers_total']:,}")
        print(f"  • Active Customers (last 30 days): {metrics['customers_active']:,}")
        print(f"  • Inactive Customers: {metrics['customers_inactive']:,}")
        print(f"  • Marketing Opt-ins: {metrics['customers_marketing']:,}")
        
        # Merchant Summary  
        print(f"\n🏪 MERCHANT METRICS:")
        print(f"  • Total Merchants: {metrics['merchants_total']}")
        print(f"  • Active Merchants: {metrics['merchants_active']}")
        print(f"  • Inactive Merchants: {metrics['merchants_inactive']}")
        
        # Volume Summary
        print(f"\n💰 PROCESSING VOLUME:")
        print(f"  • Total Volume (60 days): ${metrics['total_60d']:,.2f}")
        print(f"  • Daily Average: ${metrics['daily']:,.2f}")
        print(f"  • Weekly Average: ${metrics['weekly']:,.2f}")
        print(f"  • Monthly Average: ${metrics['monthly']:,.2f}")
        
        # Top Merchants by Volume
        print(f"\n🏆 TOP MERCHANTS BY VOLUME:")
        if not metrics['top3'].empty:
            for i, (_, row) in enumerate(metrics['top3'].iterrows(), 1):
                name = row.get('legal_name', row.get('dba_name', 'Unknown'))
                volume = row['net_sales_60d']
                monthly = volume / 2  # 60 days = 2 months
                print(f"  {i}. {name}: ${volume:,.2f} (${monthly:,.2f}/month)")
        
        # Sales Predictions
        print(f"\n🔮 SALES PREDICTIONS (Next 2 Months):")
        total_predicted = sum(p['next_2_months'] for p in report['predictions'].values())
        print(f"  • Platform Total: ${total_predicted:,.2f}")
        
        for name, pred in list(report['predictions'].items())[:3]:
            print(f"  • {name}: ${pred['next_2_months']:,.2f}")
        
        # Top Customers
        print(f"\n⭐ TOP 3 POTENTIAL CUSTOMERS:")
        for i, customer in enumerate(report['top_customers'], 1):
            name_parts = []
            if customer.get('first_name'):
                name_parts.append(customer['first_name'])
            if customer.get('last_name'):
                name_parts.append(customer['last_name'])
            name = ' '.join(name_parts) or customer.get('customer_id', 'Unknown')
            
            join_date = customer.get('customer_since', 'Unknown')
            if isinstance(join_date, str) and 'T' in join_date:
                join_date = join_date.split('T')[0]
            
            print(f"  {i}. {name} (Score: {customer['score']}, Joined: {join_date})")
        
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
        
        # Handle pandas DataFrame serialization
        if 'top3' in json_report['metrics'] and hasattr(json_report['metrics']['top3'], 'to_dict'):
            json_report['metrics']['top3'] = json_report['metrics']['top3'].to_dict('records')
        
        json.dump(json_report, f, indent=2, default=str)
    
    print(f"\nDetailed report saved to: {os.path.join(data_dir, 'analysis_report.json')}")
    
    return report

if __name__ == "__main__":
    report = main()
