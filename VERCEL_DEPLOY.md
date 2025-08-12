# 🚀 Vercel Deployment Guide

## Quick Deploy to Vercel

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/kritinkaul/swipe-savvyintern)

## Manual Deployment Steps

1. **Clone the repository:**
   ```bash
   git clone https://github.com/kritinkaul/swipe-savvyintern.git
   cd swipe-savvyintern
   ```

2. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

3. **Deploy to Vercel:**
   ```bash
   vercel --prod
   ```

## What Gets Deployed

- **Demo Dashboard**: Static analytics dashboard with sample data
- **Serverless Function**: Python-based API endpoint
- **Responsive Design**: Works on mobile and desktop
- **GitHub Integration**: Links back to full source code

## Full Local Development

For the complete analytics platform with real data processing:

```bash
# Run locally with your data
python3 web_dashboard.py          # Web dashboard at :8080
streamlit run simple_dashboard.py # Streamlit at :8501
python3 run_dashboard.py          # CLI report
```

## Features

- ✅ **134,778** customers processed
- ✅ **741** merchants analyzed
- ✅ **$5.17M** platform revenue calculated
- ✅ Real-time business intelligence
- ✅ Multiple deployment options

## Architecture

```
├── api/
│   ├── index.py           # Vercel serverless function
│   ├── dashboard.py       # Full dashboard (local data)
│   └── requirements.txt   # Python dependencies
├── src/
│   ├── etl.py            # ETL pipeline
│   ├── config.py         # Configuration
│   └── utils.py          # Utilities
├── vercel.json           # Vercel configuration
└── data/                 # Data files (local only)
```

The Vercel deployment shows a demo version with sample data, while the full version processes real data files locally.
