"""
Configuration constants for the analytics pipeline
"""
import pandas as pd

# Freeze date for reproducibility
TODAY = pd.Timestamp("2025-08-11")

# Data discovery patterns
DATA_GLOBS = {
    "merchants": [
        "data/merchants/**/*.[cC][sS][vV]", 
        "data/merchants/**/*.[xX][lL][sS][xX]", 
        "data/merchants/**/*.[xX][lL][sS]"
    ],
    "customers": [
        "data/customers/**/*.[cC][sS][vV]", 
        "data/customers/**/*.[xX][lL][sS][xX]", 
        "data/customers/**/*.[xX][lL][sS]"
    ],
    "sales": [
        "data/sales/**/*Revenue Item Sales*.csv"
    ]
}
