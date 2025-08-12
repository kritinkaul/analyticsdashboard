from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Demo data (since Vercel can't access local data files)
        demo_data = {
            'total_customers': 134778,
            'active_customers': 2294,
            'marketing_customers': 11870,
            'total_merchants': 741,
            'active_merchants': 64,
            'total_revenue': 5172529.04,
            'daily_avg': 86208.82,
            'weekly_avg': 603461.72,
            'monthly_avg': 2586264.52,
            'top_merchants': [
                {'name': 'POKE HANA', 'revenue': 863402.52},
                {'name': 'MARATHON LIQUORS', 'revenue': 853406.33},
                {'name': "ANTHONY'S PIZZA & PASTA", 'revenue': 198870.64}
            ]
        }
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Payment Platform Analytics - Demo</title>
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
                .demo-badge {{ background: linear-gradient(45deg, #ff6b6b, #ffa500); color: white; padding: 8px 16px; border-radius: 20px; font-size: 0.9em; font-weight: 500; display: inline-block; margin-bottom: 20px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th, td {{ padding: 15px; border-bottom: 1px solid #eee; text-align: left; }}
                th {{ background: #f8f9fa; font-weight: 600; color: #333; }}
                tr:hover {{ background: #f8f9fa; }}
                .github-link {{ background: linear-gradient(45deg, #333, #666); color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin: 8px; transition: all 0.3s ease; }}
                .github-link:hover {{ transform: translateY(-2px); box-shadow: 0 4px 16px rgba(0,0,0,0.3); }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>💳 Payment Platform Analytics</h1>
                    <p>Business Intelligence Dashboard • <span class="demo-badge">📊 DEMO VERSION</span></p>
                </div>
                
                <div class="metrics">
                    <div class="metric-card">
                        <div class="metric-value">{demo_data['total_customers']:,}</div>
                        <div class="metric-label">Total Customers</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{demo_data['active_customers']:,}</div>
                        <div class="metric-label">Active Customers</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{demo_data['marketing_customers']:,}</div>
                        <div class="metric-label">Marketing Subscribers</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{demo_data['total_merchants']:,}</div>
                        <div class="metric-label">Total Merchants</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">{demo_data['active_merchants']:,}</div>
                        <div class="metric-label">Active Merchants</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value">${demo_data['total_revenue']:,.0f}</div>
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
        
        for i, merchant in enumerate(demo_data['top_merchants'], 1):
            html_content += f"""
                            <tr>
                                <td><strong>#{i}</strong></td>
                                <td>{merchant['name']}</td>
                                <td><strong>${merchant['revenue']:,.2f}</strong></td>
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
                            <p style="font-size: 1.5em; margin: 5px 0; font-weight: bold;">${demo_data['daily_avg']:,.2f}</p>
                        </div>
                        <div>
                            <h3 style="margin: 0; color: #667eea;">Weekly Average</h3>
                            <p style="font-size: 1.5em; margin: 5px 0; font-weight: bold;">${demo_data['weekly_avg']:,.2f}</p>
                        </div>
                        <div>
                            <h3 style="margin: 0; color: #667eea;">Monthly Average</h3>
                            <p style="font-size: 1.5em; margin: 5px 0; font-weight: bold;">${demo_data['monthly_avg']:,.2f}</p>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>📈 Key Performance Indicators</h2>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
                        <div>
                            <h4>Customer Metrics</h4>
                            <p>Active Rate: <strong>{(demo_data['active_customers']/demo_data['total_customers'])*100:.1f}%</strong></p>
                            <p>Marketing Rate: <strong>{(demo_data['marketing_customers']/demo_data['total_customers'])*100:.1f}%</strong></p>
                        </div>
                        <div>
                            <h4>Merchant Metrics</h4>
                            <p>Active Rate: <strong>{(demo_data['active_merchants']/demo_data['total_merchants'])*100:.1f}%</strong></p>
                            <p>Revenue per Active: <strong>${demo_data['total_revenue']/demo_data['active_merchants']:,.0f}</strong></p>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>🚀 Full Version Available</h2>
                    <p>This is a demo version with sample data. The full analytics platform with real-time ETL processing is available on GitHub:</p>
                    <a href="https://github.com/kritinkaul/swipe-savvyintern" class="github-link" target="_blank">
                        📂 View Full Source Code on GitHub
                    </a>
                    <div style="margin-top: 20px; padding: 20px; background: #f8f9fa; border-radius: 8px;">
                        <h4>Features in Full Version:</h4>
                        <ul>
                            <li>✅ Real-time ETL pipeline processing</li>
                            <li>✅ Customer deduplication with exact business rules</li>
                            <li>✅ CSV export functionality</li>
                            <li>✅ Multiple deployment options (Streamlit, Web, CLI)</li>
                            <li>✅ Data validation and diagnostics</li>
                            <li>✅ Configurable data sources</li>
                        </ul>
                    </div>
                </div>
                
                <div style="text-align: center; margin-top: 40px; color: rgba(255,255,255,0.8);">
                    <p>⚡ Demo deployment on Vercel • 🚀 Full version available on GitHub</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Cache-Control', 'public, max-age=3600')
        self.end_headers()
        self.wfile.write(html_content.encode())
