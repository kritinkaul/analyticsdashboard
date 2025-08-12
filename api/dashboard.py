#!/usr/bin/env python3
"""
Vercel-compatible dashboard API endpoint
"""
import sys
import os
import json
import pandas as pd
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import html

# Add parent directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import our ETL
try:
    from src.etl import run_pipeline_from_folders
except ImportError:
    from etl import run_pipeline_from_folders

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/' or parsed_path.path == '/api/dashboard':
            self.serve_dashboard()
        elif parsed_path.path == '/api/data':
            self.serve_data()
        elif parsed_path.path == '/api/export/customers':
            self.serve_export('customers')
        elif parsed_path.path == '/api/export/merchants':
            self.serve_export('merchants')
        else:
            self.send_error(404)
    
    def serve_dashboard(self):
        """Serve the main dashboard HTML"""
        try:
            # Run ETL to get fresh data
            result = run_pipeline_from_folders()
            customers = result['customers']
            merchants = result['merchants_enriched']
            
            # Calculate stats
            total_customers = len(customers)
            active_customers = customers['active_flag'].sum()
            marketing_customers = customers['marketing_opt_in'].sum() if 'marketing_opt_in' in customers.columns else 0
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
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }}
                    .container {{ max-width: 1200px; margin: 0 auto; }}
                    .header {{ background: rgba(255,255,255,0.95); color: #333; padding: 30px; border-radius: 12px; text-align: center; box-shadow: 0 8px 32px rgba(0,0,0,0.1); margin-bottom: 30px; }}
                    .header h1 {{ margin: 0; font-size: 2.5em; font-weight: 300; }}
                    .header p {{ margin: 10px 0 0 0; color: #666; font-size: 1.1em; }}
                    .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0; }}
                    .metric-card {{ background: rgba(255,255,255,0.95); padding: 25px; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); text-align: center; transition: transform 0.3s ease; }}
                    .metric-card:hover {{ transform: translateY(-5px); }}
                    .metric-value {{ font-size: 2.5em; font-weight: bold; color: #667eea; margin-bottom: 10px; }}
                    .metric-label {{ color: #666; font-size: 1em; text-transform: uppercase; letter-spacing: 1px; }}
                    .section {{ background: rgba(255,255,255,0.95); margin: 30px 0; padding: 30px; border-radius: 12px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }}
                    .section h2 {{ margin-top: 0; color: #333; font-weight: 300; }}
                    .export-btn {{ background: linear-gradient(45deg, #667eea, #764ba2); color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 8px; transition: all 0.3s ease; }}
                    .export-btn:hover {{ transform: translateY(-2px); box-shadow: 0 4px 16px rgba(102,126,234,0.3); }}
                    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                    th, td {{ padding: 15px; border-bottom: 1px solid #eee; text-align: left; }}
                    th {{ background: #f8f9fa; font-weight: 600; color: #333; }}
                    tr:hover {{ background: #f8f9fa; }}
                    .refresh-btn {{ background: linear-gradient(45deg, #28a745, #20c997); color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin: 10px 0; display: inline-block; transition: all 0.3s ease; }}
                    .refresh-btn:hover {{ transform: translateY(-2px); box-shadow: 0 4px 16px rgba(40,167,69,0.3); }}
                    .status-badge {{ padding: 4px 12px; border-radius: 20px; font-size: 0.9em; font-weight: 500; }}
                    .status-active {{ background: #d4edda; color: #155724; }}
                    .status-total {{ background: #d1ecf1; color: #0c5460; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>💳 Payment Platform Analytics</h1>
                        <p>Real-time business intelligence from your data • Deployed on Vercel</p>
                    </div>
                    
                    <div class="metrics">
                        <div class="metric-card">
                            <div class="metric-value">{total_customers:,}</div>
                            <div class="metric-label">Total Customers</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{active_customers:,}</div>
                            <div class="metric-label">Active Customers</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value">{marketing_customers:,}</div>
                            <div class="metric-label">Marketing Subscribers</div>
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
                                    <td><strong>#{i}</strong></td>
                                    <td>{html.escape(str(row['legal_name']))}</td>
                                    <td><strong>${row['net_sales_60d']:,.2f}</strong></td>
                                </tr>
                """
            
            html_content += f"""
                            </tbody>
                        </table>
                    </div>
                    
                    <div class="section">
                        <h2>📊 Revenue Analytics</h2>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 20px;">
                            <div>
                                <h3 style="margin: 0; color: #667eea;">Daily Average</h3>
                                <p style="font-size: 1.5em; margin: 5px 0; font-weight: bold;">${daily_avg:,.2f}</p>
                            </div>
                            <div>
                                <h3 style="margin: 0; color: #667eea;">Weekly Average</h3>
                                <p style="font-size: 1.5em; margin: 5px 0; font-weight: bold;">${weekly_avg:,.2f}</p>
                            </div>
                            <div>
                                <h3 style="margin: 0; color: #667eea;">Monthly Average</h3>
                                <p style="font-size: 1.5em; margin: 5px 0; font-weight: bold;">${monthly_avg:,.2f}</p>
                            </div>
                        </div>
                    </div>
                    
                    <div class="section">
                        <h2>📁 Data Export</h2>
                        <p>Download your processed analytics data:</p>
                        <a href="/api/export/customers" class="export-btn">📋 Export Customers CSV</a>
                        <a href="/api/export/merchants" class="export-btn">🏪 Export Merchants CSV</a>
                        <br><br>
                        <a href="/" class="refresh-btn">🔄 Refresh Analytics</a>
                    </div>
                    
                    <div class="section">
                        <h2>📈 Key Performance Indicators</h2>
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                            <div>
                                <h4>Customer Metrics</h4>
                                <p><span class="status-badge status-active">Active Rate: {(active_customers/total_customers)*100:.1f}%</span></p>
                                <p><span class="status-badge status-total">Marketing Rate: {(marketing_customers/total_customers)*100:.1f}%</span></p>
                            </div>
                            <div>
                                <h4>Merchant Metrics</h4>
                                <p><span class="status-badge status-active">Active Rate: {(active_merchants/total_merchants)*100:.1f}%</span></p>
                                <p><span class="status-badge status-total">Revenue per Active: ${total_revenue/max(active_merchants,1):,.0f}</span></p>
                            </div>
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 40px; color: rgba(255,255,255,0.8);">
                        <p>⚡ Powered by real-time ETL pipeline • 🚀 Deployed on Vercel</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            self.wfile.write(html_content.encode())
            
        except Exception as e:
            # Error page
            error_html = f"""
            <!DOCTYPE html>
            <html>
            <head><title>Analytics Dashboard - Error</title></head>
            <body style="font-family: Arial, sans-serif; padding: 40px; text-align: center;">
                <h1>⚠️ Dashboard Temporarily Unavailable</h1>
                <p>We're experiencing technical difficulties loading the analytics data.</p>
                <p><strong>Error:</strong> {html.escape(str(e))}</p>
                <p><a href="/" style="color: #007bff;">🔄 Try Again</a></p>
            </body>
            </html>
            """
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(error_html.encode())
    
    def serve_export(self, data_type):
        """Serve CSV exports"""
        try:
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
            
        except Exception as e:
            self.send_error(500, explain=str(e))

# Vercel handler function
def handler(request, context):
    """Vercel serverless function handler"""
    return Handler(request, context)
