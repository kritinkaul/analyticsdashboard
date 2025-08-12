#!/usr/bin/env python3
"""
Interactive Dashboard for Business Metrics
"""

import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import dash_bootstrap_components as dbc

# Load the analysis report
report_path = 'analysis_report.json'
with open(report_path, 'r') as f:
    report = json.load(f)

# Initialize Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Business Dashboard - Merchant & Customer Analytics"

# Extract data for dashboard
metrics = report['metrics']
merchants = report['merchants']
predictions = report['predictions']
top_customers = report['top_customers']

# Create summary cards
def create_metric_card(title, value, subtitle="", color="primary"):
    return dbc.Card([
        dbc.CardBody([
            html.H4(title, className="card-title"),
            html.H2(value, className=f"text-{color}"),
            html.P(subtitle, className="card-text")
        ])
    ], className="mb-3")

# Create charts
def create_customer_chart():
    """Create customer breakdown chart"""
    labels = ['Active (Last 30 days)', 'Inactive']
    values = [metrics['customers_active'], metrics['customers_inactive']]
    colors = ['#28a745', '#dc3545']
    
    fig = go.Figure(data=[go.Pie(
        labels=labels, 
        values=values,
        hole=0.3,
        marker_colors=colors
    )])
    fig.update_layout(
        title="Customer Status Distribution",
        height=400
    )
    return fig

def create_merchant_volume_chart():
    """Create merchant volume comparison chart"""
    # Extract merchant data from the merchants list
    names = []
    volumes = []
    for merchant in merchants:
        name = merchant.get('legal_name', merchant.get('dba_name', 'Unknown'))
        volume = merchant.get('net_sales_60d_final', 0)
        names.append(name)
        volumes.append(volume)
    
    fig = go.Figure(data=[go.Bar(
        x=names,
        y=volumes,
        marker_color=['#007bff', '#28a745', '#ffc107']
    )])
    fig.update_layout(
        title="Net Sales by Merchant (60 days)",
        xaxis_title="Merchant",
        yaxis_title="Net Sales ($)",
        yaxis_tickformat='$,.0f',
        height=400
    )
    return fig

def create_predictions_chart():
    """Create sales predictions chart"""
    merchant_names = list(predictions.keys())
    current = [predictions[name]['current_monthly_avg'] for name in merchant_names]
    next_2_months = [predictions[name]['next_2_months'] for name in merchant_names]
    next_year = [predictions[name]['same_period_next_year'] for name in merchant_names]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Current Monthly Average',
        x=merchant_names,
        y=current,
        marker_color='#007bff'
    ))
    fig.add_trace(go.Bar(
        name='Next 2 Months (Projected)',
        x=merchant_names,
        y=next_2_months,
        marker_color='#28a745'
    ))
    fig.add_trace(go.Bar(
        name='Same Period Next Year',
        x=merchant_names,
        y=next_year,
        marker_color='#ffc107'
    ))
    
    fig.update_layout(
        title="Sales Predictions by Merchant",
        xaxis_title="Merchant",
        yaxis_title="Sales ($)",
        yaxis_tickformat='$,.0f',
        barmode='group',
        height=400
    )
    return fig

def create_volume_timeline_chart():
    """Create volume timeline chart"""
    # Create data for daily/weekly/monthly view
    periods = ['Daily Average', 'Weekly Average', 'Monthly Average']
    total_volumes = [
        metrics['daily'],
        metrics['weekly'],
        metrics['monthly']
    ]
    
    fig = go.Figure(data=[go.Bar(
        x=periods,
        y=total_volumes,
        marker_color=['#17a2b8', '#6f42c1', '#e83e8c']
    )])
    fig.update_layout(
        title="Platform Processing Volume Overview",
        xaxis_title="Time Period",
        yaxis_title="Volume ($)",
        yaxis_tickformat='$,.0f',
        height=400
    )
    return fig

# Layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H1("Business Analytics Dashboard", className="text-center mb-4"),
            html.Hr(),
            html.P(f"Data Period: {report['data_period']}", className="text-center text-muted"),
            html.P(f"Last Updated: {report['timestamp']}", className="text-center text-muted mb-4"),
        ], width=12)
    ]),
    
    # Summary Cards Row
    dbc.Row([
        dbc.Col([
            create_metric_card(
                "Total Customers",
                f"{metrics['customers_total']:,}",
                f"Active: {metrics['customers_active']:,} | Inactive: {metrics['customers_inactive']:,}",
                "info"
            )
        ], width=3),
        dbc.Col([
            create_metric_card(
                "Total Merchants",
                f"{metrics['merchants_total']}",
                f"Active: {metrics['merchants_active']} | Inactive: {metrics['merchants_inactive']}",
                "success"
            )
        ], width=3),
        dbc.Col([
            create_metric_card(
                "Total Volume (60 days)",
                f"${metrics['total_60d']:,.0f}",
                f"Monthly Avg: ${metrics['monthly']:,.0f}",
                "warning"
            )
        ], width=3),
        dbc.Col([
            create_metric_card(
                "Marketing Opt-ins",
                f"{metrics['customers_marketing']:,}",
                f"{(metrics['customers_marketing']/metrics['customers_total']*100):.1f}% of customers",
                "danger"
            )
        ], width=3),
    ], className="mb-4"),
    
    # Charts Row 1
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=create_customer_chart())
        ], width=6),
        dbc.Col([
            dcc.Graph(figure=create_merchant_volume_chart())
        ], width=6),
    ], className="mb-4"),
    
    # Charts Row 2
    dbc.Row([
        dbc.Col([
            dcc.Graph(figure=create_volume_timeline_chart())
        ], width=6),
        dbc.Col([
            dcc.Graph(figure=create_predictions_chart())
        ], width=6),
    ], className="mb-4"),
    
    # Detailed Tables Row
    dbc.Row([
        dbc.Col([
            html.H4("Top Merchants by Volume"),
            dash_table.DataTable(
                data=[
                    {
                        'Merchant': merchant.get('legal_name', merchant.get('dba_name', 'Unknown')),
                        'Net Sales (60 days)': f"${merchant.get('net_sales_60d_final', 0):,.2f}",
                        'Monthly Average': f"${merchant.get('monthly_volume_est', 0):,.2f}",
                        'Daily Average': f"${merchant.get('daily_volume_est', 0):,.2f}",
                        'Status': 'Active' if merchant.get('active_flag', False) else 'Inactive'
                    }
                    for merchant in merchants
                ],
                columns=[
                    {'name': 'Merchant', 'id': 'Merchant'},
                    {'name': 'Net Sales (60 days)', 'id': 'Net Sales (60 days)'},
                    {'name': 'Monthly Average', 'id': 'Monthly Average'},
                    {'name': 'Daily Average', 'id': 'Daily Average'},
                    {'name': 'Status', 'id': 'Status'}
                ],
                style_cell={'textAlign': 'left'},
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{Status} = Active'},
                        'backgroundColor': '#d4edda',
                        'color': 'black',
                    }
                ]
            )
        ], width=12)
    ], className="mb-4"),
    
    dbc.Row([
        dbc.Col([
            html.H4("Top 3 Potential Customers"),
            dash_table.DataTable(
                data=[
                    {
                        'Customer ID': customer['customer_id'],
                        'Name': f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip() or 'N/A',
                        'Joined Date': str(customer['customer_since'])[:10] if customer.get('customer_since') else 'N/A',
                        'Marketing Allowed': customer.get('marketing_allowed', 'N/A'),
                        'Potential Score': customer['score']
                    }
                    for customer in top_customers
                ],
                columns=[
                    {'name': 'Customer ID', 'id': 'Customer ID'},
                    {'name': 'Name', 'id': 'Name'},
                    {'name': 'Joined Date', 'id': 'Joined Date'},
                    {'name': 'Marketing Allowed', 'id': 'Marketing Allowed'},
                    {'name': 'Potential Score', 'id': 'Potential Score'}
                ],
                style_cell={'textAlign': 'left'},
                style_data_conditional=[
                    {
                        'if': {'filter_query': '{Marketing Allowed} = Yes'},
                        'backgroundColor': '#d4edda',
                        'color': 'black',
                    }
                ]
            )
        ], width=12)
    ], className="mb-4"),
    
    # Sales Predictions Table
    dbc.Row([
        dbc.Col([
            html.H4("Sales Predictions"),
            dash_table.DataTable(
                data=[
                    {
                        'Merchant': name,
                        'Current Monthly Avg': f"${pred['current_monthly_avg']:,.2f}",
                        'Next 2 Months Prediction': f"${pred['next_2_months']:,.2f}",
                        'Same Period Next Year': f"${pred['same_period_next_year']:,.2f}",
                        'Growth %': f"{((pred['same_period_next_year']/pred['next_2_months'])-1)*100:.1f}%"
                    }
                    for name, pred in predictions.items()
                ],
                columns=[
                    {'name': 'Merchant', 'id': 'Merchant'},
                    {'name': 'Current Monthly Avg', 'id': 'Current Monthly Avg'},
                    {'name': 'Next 2 Months Prediction', 'id': 'Next 2 Months Prediction'},
                    {'name': 'Same Period Next Year', 'id': 'Same Period Next Year'},
                    {'name': 'Growth %', 'id': 'Growth %'}
                ],
                style_cell={'textAlign': 'left'}
            )
        ], width=12)
    ], className="mb-4"),
    
    # Footer
    dbc.Row([
        dbc.Col([
            html.Hr(),
            html.P("Dashboard generated from provided business data", className="text-center text-muted"),
            html.P("Data includes customer registrations, merchant revenue, and platform metrics", className="text-center text-muted")
        ], width=12)
    ])
    
], fluid=True)

if __name__ == "__main__":
    print("Starting Dashboard Server...")
    print("Dashboard will be available at: http://127.0.0.1:8050")
    print("Press Ctrl+C to stop the server")
    app.run(debug=True, host='127.0.0.1', port=8050)
