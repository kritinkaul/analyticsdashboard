#!/usr/bin/env python3
"""
Simple web dashboard using Python's built-in HTTP server
"""
import sys
import os
import json
import pandas as pd
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import html

# Add src to path
sys.path.append('src')

# Import our ETL
from etl import run_pipeline_from_folders

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.serve_dashboard()
        elif parsed_path.path == '/data':
            self.serve_data()
        elif parsed_path.path == '/export/customers':
            self.serve_export('customers')
        elif parsed_path.path == '/export/merchants':
            self.serve_export('merchants')
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        """Serve the main dashboard HTML"""
        # Run ETL to get fresh data
        result = run_pipeline_from_folders()
        customers = result['customers']
        merchants = result['merchants_enriched']
        metrics = result['metrics']
        
        # Calculate stats
        total_customers = len(customers)
        active_customers = customers['active_flag'].sum()
        marketing_customers = customers['marketing_opt_in'].sum()
        total_merchants = len(merchants)
        active_merchants = merchants['active_flag'].sum()
        
        # Calculate total revenue directly from merchants data
        total_revenue = merchants['net_sales_60d'].sum()
        daily_avg = total_revenue / 60
        weekly_avg = total_revenue * 7 / 60
        monthly_avg = total_revenue / 2
        
        top3 = merchants.nlargest(3, 'net_sales_60d')[['legal_name', 'net_sales_60d']]
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Payment Platform Analytics</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background: #2e7bcf; color: white; padding: 20px; border-radius: 8px; text-align: center; }}
                .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
                .metric-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .metric-value {{ font-size: 2em; font-weight: bold; color: #2e7bcf; }}
                .metric-label {{ color: #666; margin-top: 5px; }}
                .section {{ background: white; margin: 20px 0; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                .export-btn {{ background: #2e7bcf; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; display: inline-block; margin: 5px; }}
                .export-btn:hover {{ background: #1e5bb8; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }}
                th {{ background: #f8f9fa; }}
                .refresh-btn {{ background: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px; margin: 10px 0; display: inline-block; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💳 Payment Platform Analytics Dashboard</h1>
                    <p>Real-time business intelligence from your data</p>
                </div>
                
                <div class="metrics">
                    <div class="metric-card">
                        <div class="metric-value">{total_customers:,}</div>
                        <div class="metric-label">Total Customers</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{active_customers:,}</div>
                        <div class="metric-label">Active Customers (30d)</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{marketing_customers:,}</div>
                        <div class="metric-label">Marketing Opt-ins</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{total_merchants:,}</div>
                        <div class="metric-label">Total Merchants</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{active_merchants:,}</div>
                        <div class="metric-label">Active Merchants</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${total_revenue:,.0f}</div>
                        <div class="metric-label">Platform Revenue (60d)</div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🏆 Top 3 Merchants</h2>
                    <table>
                        <thead>
                            <tr><th>Rank</th><th>Merchant</th><th>Revenue (60d)</th></tr>
                        </thead>
                        <tbody>
        """
        
        for i, (_, row) in enumerate(top3.iterrows(), 1):
            html_content += f"""
                            <tr>
                                <td>{i}</td>
                                <td>{html.escape(str(row['legal_name']))}</td>
                                <td>${row['net_sales_60d']:,.2f}</td>
                            </tr>
            """
        
        html_content += f"""
                        </tbody>
                    </table>
                </div>
                
                <div class="section">
                    <h2>📊 Revenue Breakdown</h2>
                    <p><strong>Daily Average:</strong> ${daily_avg:,.2f}</p>
                    <p><strong>Weekly Average:</strong> ${weekly_avg:,.2f}</p>
                    <p><strong>Monthly Average:</strong> ${monthly_avg:,.2f}</p>
                </div>
                
                <div class="section">
                    <h2>📁 Data Export</h2>
                    <p>Download your processed data:</p>
                    <a href="/export/customers" class="export-btn">📋 Export Customers CSV</a>
                    <a href="/export/merchants" class="export-btn">🏪 Export Merchants CSV</a>
                    <br><br>
                    <a href="/" class="refresh-btn">🔄 Refresh Data</a>
                </div>
                
                <div class="section">
                    <h2>📈 Data Summary</h2>
                    <p><strong>Customer Active Rate:</strong> {(active_customers/total_customers)*100:.1f}%</p>
                    <p><strong>Marketing Opt-in Rate:</strong> {(marketing_customers/total_customers)*100:.1f}%</p>
                    <p><strong>Merchant Active Rate:</strong> {(active_merchants/total_merchants)*100:.1f}%</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_content.encode())
    
    def serve_export(self, data_type):
        """Serve CSV exports"""
        result = run_pipeline_from_folders()
        
        if data_type == 'customers':
            df = result['customers']
            filename = 'customers_export.csv'
        elif data_type == 'merchants':
            df = result['merchants_enriched']
            filename = 'merchants_export.csv'
        else:
            self.send_error(404)
            return
        
        csv_data = df.to_csv(index=False)
        
        self.send_response(200)
        self.send_header('Content-type', 'text/csv')
        self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
        self.end_headers()
        self.wfile.write(csv_data.encode())

def run_web_dashboard(port=8080):
    """Run the web dashboard"""
    server = HTTPServer(('localhost', port), DashboardHandler)
    print(f"🚀 Payment Platform Analytics Dashboard")
    print(f"📊 Running at: http://localhost:{port}")
    print(f"💡 Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped")
        server.server_close()

if __name__ == "__main__":
    run_web_dashboard()
