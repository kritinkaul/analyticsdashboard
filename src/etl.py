from __future__ import annotations
import io
import re
import numpy as np
import pandas as pd
import json
from pathlib import Path

# Handle both relative and absolute imports
try:
    from .config import TODAY, DATA_GLOBS
    from .utils import discover_files
except ImportError:
    from config import TODAY, DATA_GLOBS
    from utils import discover_files

MONEY_RE = re.compile(r"[^\d\.\-]")

def parse_currency(s: pd.Series) -> pd.Series:
    """Parse currency strings to numeric values"""
    if s is None: 
        return s
    x = (s.astype(str).str.replace(MONEY_RE, "", regex=True)
                   .replace({"": np.nan, ".": np.nan}))
    return pd.to_numeric(x, errors="coerce")

def standardize_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize column names by removing whitespace and newlines"""
    df = df.copy()
    df.columns = [c.strip().replace("\n"," ").replace("\r"," ") for c in df.columns]
    return df

def load_customers() -> pd.DataFrame:
    """Load and deduplicate customers with proper ID-first logic"""
    paths = discover_files(DATA_GLOBS["customers"])
    print(f"Loading customers from {len(paths)} files: {[Path(p).name for p in paths]}")
    
    dfs = []
    
    for p in paths:
        df = pd.read_csv(p, low_memory=False) if p.lower().endswith(".csv") else pd.read_excel(p)
        df = standardize_cols(df)
        df["__source_file"] = Path(p).name  # Track source for debugging
        dfs.append(df)
        print(f"  {Path(p).name}: {len(df)} rows")
    
    if not dfs: 
        return pd.DataFrame(columns=["customer_id","first_name","last_name","email","phone","customer_since","active_flag"])
    
    # After concatenating ALL customer files into `cust`
    cust = pd.concat(dfs, ignore_index=True, sort=False)
    print(f"Combined raw customers: {len(cust)} rows")
    
    # Print source distribution for debugging
    print("Customers — rows by source file:")
    source_counts = cust.groupby("__source_file", dropna=False).size().sort_values(ascending=False)
    for file, count in source_counts.items():
        print(f"  {file}: {count:,}")
    
    cust = cust.copy()
    cust.columns = [c.strip().lower() for c in cust.columns]

    id_col    = next((c for c in cust.columns if c in ["customer id","customerid","id"]), None)
    email_col = next((c for c in cust.columns if "email" in c), None)
    phone_col = next((c for c in cust.columns if "phone" in c), None)

    print(f"Mapped fields: ID={id_col}, Email={email_col}, Phone={phone_col}")

    with_id    = cust[cust[id_col].notna()].copy() if id_col else cust.iloc[0:0].copy()
    without_id = cust[cust[id_col].isna()].copy()  if id_col else cust.copy()

    print(f"Customers with ID: {len(with_id)}, without ID: {len(without_id)}")

    # 1) Dedup ID-present by ID
    if not with_id.empty:
        pre_dedupe = len(with_id)
        with_id = with_id.drop_duplicates(id_col)
        print(f"ID-present dedupe: {pre_dedupe} -> {len(with_id)} rows")

    # 2) Dedup ID-missing by email+phone
    if email_col and phone_col and not without_id.empty:
        without_id["__ep"] = without_id[email_col].astype(str) + "|" + without_id[phone_col].astype(str)
        pre_ep_dedupe = len(without_id)
        without_id = without_id.drop_duplicates("__ep")
        print(f"Email+phone dedupe: {pre_ep_dedupe} -> {len(without_id)} rows")

        # 3) Exclude fallback rows that collide with the ID set (by email+phone)
        if not with_id.empty:
            with_id["__ep"] = with_id[email_col].astype(str) + "|" + with_id[phone_col].astype(str)
            pre_collision = len(without_id)
            without_id = without_id[~without_id["__ep"].isin(with_id["__ep"])]
            collision_removed = pre_collision - len(without_id)
            print(f"Removed {collision_removed} fallback rows that collide with ID set")
            with_id = with_id.drop(columns="__ep", errors="ignore")

    # Final customers
    customers = pd.concat([with_id, without_id], ignore_index=True)

    # Clean up temp columns
    customers = customers.drop(columns=["__ep", "__source_file"], errors="ignore")

    # Active flag (use fixed TODAY for consistency)
    if "customer since" in customers.columns:
        try:
            customers["customer since"] = pd.to_datetime(customers["customer since"], errors="coerce")
        except (TypeError, AttributeError):
            # Fallback: strip timezone and parse
            date_series = customers["customer since"].astype(str).str.replace(r' [A-Z]{3}$', '', regex=True)
            customers["customer since"] = pd.to_datetime(date_series, errors="coerce")
        customers["active_flag"] = (TODAY - customers["customer since"]).dt.days.between(0, 30, inclusive="left")
    else:
        customers["active_flag"] = False

    print("Final customers_total:", len(customers))
    print("Active (30d):", int(customers["active_flag"].sum()))
    print("Inactive:", len(customers) - int(customers["active_flag"].sum()))

    # Sanity check prints
    if id_col:
        unique_ids = customers[id_col].nunique(dropna=True)
        print(f"Unique IDs: {unique_ids}")

    if email_col and phone_col:
        fallback_set = customers[customers[id_col].isna()] if id_col else customers
        if len(fallback_set) > 0:
            unique_ep = fallback_set[[email_col, phone_col]].astype(str).agg("|".join, axis=1).nunique()
            print(f"Unique email+phone (fallback set): {unique_ep}")

    # Create standardized output DataFrame with proper column mapping
    out = pd.DataFrame()
    
    # Map to standard column names
    fn_col = next((c for c in customers.columns if "first" in c and "name" in c), None)
    ln_col = next((c for c in customers.columns if "last" in c and "name" in c), None)
    mcol = next((c for c in customers.columns if "marketing" in c and ("allow" in c or "opt" in c or "consent" in c)), None)
    
    if id_col: out["customer_id"] = customers[id_col]
    if fn_col: out["first_name"] = customers[fn_col]
    if ln_col: out["last_name"] = customers[ln_col]
    if email_col: out["email"] = customers[email_col]
    if phone_col: out["phone"] = customers[phone_col]
    out["customer_since"] = customers.get("customer since", pd.NaT)
    out["active_flag"] = customers["active_flag"]
    
    # Marketing flag
    if mcol:
        out["marketing_opt_in"] = customers[mcol].astype(str).str.lower().isin(["true","yes","1","y","opted in"])
        print(f"Marketing opt-ins: {out['marketing_opt_in'].sum()} / {len(out)}")
    else:
        out["marketing_opt_in"] = False
        print("No marketing column found, defaulting to False")
    
    return out

def load_merchants() -> pd.DataFrame:
    """Load all merchants with no status filtering"""
    paths = discover_files(DATA_GLOBS["merchants"])
    print(f"Loading merchants from {len(paths)} files: {[Path(p).name for p in paths]}")
    
    dfs = []
    for p in paths:
        if p.lower().endswith(".csv"):
            df = pd.read_csv(p, low_memory=False)
        else:
            # pick the widest sheet if multiple
            sheets = pd.read_excel(p, sheet_name=None)
            df = max(sheets.values(), key=lambda d: (d.shape[0], d.shape[1]))
        df = standardize_cols(df)
        dfs.append(df)
        print(f"  {Path(p).name}: {len(df)} rows, {len(df.columns)} columns")
    
    if not dfs: 
        return pd.DataFrame()
    
    m = pd.concat(dfs, ignore_index=True, sort=False)
    print(f"Combined raw merchants: {len(m)} rows")

    # Map canonical fields
    ren = {}
    for c in list(m.columns):
        cl = c.lower()
        if cl == "customer id":  ren[c] = "merchant_id"
        elif "legal business name" in cl: ren[c] = "legal_name"
        elif "dba" in cl and "name" in cl: ren[c] = "dba_name"
        elif "account status" in cl:  ren[c] = "account_status"
        elif "registration date" in cl: ren[c] = "registration_date"
        elif "mtd volume" in cl: ren[c] = "mtd_volume"
        elif "last month volume" in cl: ren[c] = "last_month_volume"
        elif "mcc description" in cl: ren[c] = "mcc_description"
        elif "pci compliance" in cl: ren[c] = "pci_compliance"
    
    m = m.rename(columns=ren)
    print(f"Renamed columns: {list(ren.values())}")

    if "registration_date" in m.columns:
        m["registration_date"] = pd.to_datetime(m["registration_date"], errors="coerce")
    
    for col in ["mtd_volume","last_month_volume"]:
        if col in m.columns:
            before_sum = m[col].sum() if m[col].dtype in ['int64', 'float64'] else 0
            m[col] = parse_currency(m[col])
            after_sum = m[col].sum()
            print(f"Parsed {col}: ${before_sum:,.2f} -> ${after_sum:,.2f}")

    # Join key: prefer DBA else Legal, uppercase/trim
    dba_col = m.get("dba_name")
    legal_col = m.get("legal_name")
    
    if dba_col is not None and legal_col is not None:
        m["merchant_name_key"] = (
            dba_col.fillna("").astype(str).str.strip().replace("", np.nan)
            .fillna(legal_col.astype(str))
            .str.strip().str.upper()
        )
    elif legal_col is not None:
        m["merchant_name_key"] = legal_col.astype(str).str.strip().str.upper()
    elif dba_col is not None:
        m["merchant_name_key"] = dba_col.astype(str).str.strip().str.upper()
    else:
        # Fallback to index if no name columns found
        m["merchant_name_key"] = "MERCHANT_" + m.index.astype(str)
    
    print(f"Generated {len(m['merchant_name_key'].unique())} unique merchant keys")
    
    # Print status distribution (but don't filter)
    if "account_status" in m.columns:
        status_counts = m["account_status"].value_counts()
        print(f"Account status distribution: {status_counts.to_dict()}")
    
    return m

def parse_items_report_csv(path: str) -> pd.DataFrame | None:
    """Parse sales item report CSV, detecting header row"""
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        
        # Find header row containing "...Name,...,Net Sales,..."
        hdr = None
        for i, ln in enumerate(lines[:200]):
            if "name" in ln.lower() and "net sales" in ln.lower() and "," in ln:
                hdr = i
                break
        
        if hdr is None:
            print(f"  No header found in {Path(path).name}")
            return None
        
        df = pd.read_csv(io.StringIO("".join(lines[hdr:])), engine="python")
        df = standardize_cols(df)
        
        if "Net Sales" in df.columns:
            df["Net Sales_num"] = parse_currency(df["Net Sales"])
            net_sales_total = df["Net Sales_num"].sum()
            print(f"  Parsed {len(df)} items, Net Sales: ${net_sales_total:,.2f}")
            return df
        else:
            print(f"  No 'Net Sales' column found in {Path(path).name}")
            return None
            
    except Exception as e:
        print(f"  Error parsing {Path(path).name}: {e}")
        return None

def load_sales() -> pd.DataFrame:
    """Load and aggregate sales from item reports"""
    paths = discover_files(DATA_GLOBS["sales"])
    print(f"Loading sales from {len(paths)} files:")
    
    outs = []
    total_sales = 0
    
    for p in paths:
        df = parse_items_report_csv(p)
        if df is None or df.empty: 
            continue
        
        # Extract merchant name from filename
        merch_key = Path(p).name.split("-Revenue Item Sales")[0].strip().upper()
        sales_amount = df["Net Sales_num"].sum()
        total_sales += sales_amount
        
        print(f"  {merch_key}: ${sales_amount:,.2f}")
        outs.append(pd.DataFrame({
            "merchant_name_key": [merch_key],
            "net_sales_60d_item": [sales_amount]
        }))
    
    result = pd.concat(outs, ignore_index=True) if outs else pd.DataFrame(columns=["merchant_name_key","net_sales_60d_item"])
    print(f"Total item sales across {len(outs)} merchants: ${total_sales:,.2f}")
    
    return result

def enrich_and_metrics(merchants: pd.DataFrame, customers: pd.DataFrame, sales_agg: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Enrich merchants with sales and compute all metrics"""
    print("\n== ENRICHMENT & METRICS ==")
    
    m = merchants.copy()
    s = sales_agg.copy()
    
    # Merge sales data
    print(f"Merchants before sales merge: {len(m)}")
    print(f"Sales records to merge: {len(s)}")
    
    m = m.merge(s, on="merchant_name_key", how="left")
    merchants_with_items = m["net_sales_60d_item"].notna().sum()
    print(f"Merchants with item sales data: {merchants_with_items} / {len(m)}")

    # Fallback: use MTD + LastMonth when no item file exists
    m["mtd_volume"] = pd.to_numeric(m.get("mtd_volume"), errors="coerce").fillna(0)
    m["last_month_volume"] = pd.to_numeric(m.get("last_month_volume"), errors="coerce").fillna(0)
    fallback_60d = m["mtd_volume"] + m["last_month_volume"]
    
    fallback_total = fallback_60d.sum()
    item_total = m["net_sales_60d_item"].sum()
    print(f"Item sales total: ${item_total:,.2f}")
    print(f"Fallback (MTD+LastMonth) total: ${fallback_total:,.2f}")

    # CRITICAL: Coalesce, don't sum (avoid double-count)
    m["net_sales_60d"] = np.where(m["net_sales_60d_item"].notna(), m["net_sales_60d_item"], fallback_60d)
    
    coalesced_total = m["net_sales_60d"].sum()
    print(f"Final coalesced 60d total: ${coalesced_total:,.2f}")

    # Active merchant proxy + time windows (derive AFTER coalesce)
    m["active_flag"] = m["net_sales_60d"] > 0
    m["daily_est"] = m["net_sales_60d"] / 60.0
    m["weekly_est"] = m["net_sales_60d"] * 7.0 / 60.0
    m["monthly_est"] = m["net_sales_60d"] / 2.0

    # Platform totals
    total_60d = float(m["net_sales_60d"].sum())
    daily = total_60d / 60.0
    weekly = total_60d * 7.0 / 60.0
    monthly = total_60d / 2.0

    print(f"Platform totals - 60d: ${total_60d:,.2f}, Daily: ${daily:,.2f}, Weekly: ${weekly:,.2f}, Monthly: ${monthly:,.2f}")

    # Counts
    merchants_total = int(len(m))
    merchants_active = int(m["active_flag"].sum())
    merchants_inactive = merchants_total - merchants_active

    customers_total = int(len(customers))
    customers_active = int(customers["active_flag"].sum())
    customers_inactive = customers_total - customers_active
    customers_marketing = int(customers.get("marketing_opt_in", pd.Series(False, index=customers.index)).sum())

    print(f"Merchants: {merchants_total} total, {merchants_active} active, {merchants_inactive} inactive")
    print(f"Customers: {customers_total} total, {customers_active} active, {customers_inactive} inactive, {customers_marketing} marketing")

    # Top 3 merchants
    top3 = (m.sort_values("net_sales_60d", ascending=False)
              .loc[:, ["legal_name","dba_name","net_sales_60d","daily_est","weekly_est","monthly_est"]]
              .head(3)
              .reset_index(drop=True))
    
    print("Top 3 merchants:")
    for i, row in top3.iterrows():
        name = row["dba_name"] if pd.notna(row["dba_name"]) else row["legal_name"]
        print(f"  {i+1}. {name}: ${row['net_sales_60d']:,.2f}")

    metrics = dict(
        merchants_total=merchants_total, 
        merchants_active=merchants_active, 
        merchants_inactive=merchants_inactive,
        merchants_with_item_data=int(merchants_with_items),
        customers_total=customers_total, 
        customers_active=customers_active, 
        customers_inactive=customers_inactive,
        customers_marketing=customers_marketing,
        platform_total_60d=round(total_60d,2), 
        platform_daily=round(daily,2), 
        platform_weekly=round(weekly,2), 
        platform_monthly=round(monthly,2),
        top3=top3
    )
    return m, metrics

def load_previous_metrics() -> dict:
    """Load previous metrics for DIFF report"""
    try:
        with open("metrics_cache.json", "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_current_metrics(metrics: dict):
    """Save current metrics for future DIFF reports"""
    # Convert top3 DataFrame to dict for JSON serialization
    metrics_copy = metrics.copy()
    if "top3" in metrics_copy:
        metrics_copy["top3"] = metrics_copy["top3"].to_dict("records")
    
    with open("metrics_cache.json", "w") as f:
        json.dump(metrics_copy, f, indent=2)

def print_diff_report(current_metrics: dict, previous_metrics: dict):
    """Print DIFF report comparing current vs previous metrics"""
    if not previous_metrics:
        print("\n== DIFF REPORT ==")
        print("No previous metrics found - this is the first run")
        return
    
    print("\n== DIFF REPORT ==")
    
    # Key metrics to compare
    compare_keys = [
        ("merchants_total", "Merchants Total"),
        ("merchants_active", "Merchants Active"),
        ("merchants_with_item_data", "Merchants with Item Data"),
        ("customers_total", "Customers Total"), 
        ("customers_active", "Customers Active"),
        ("customers_marketing", "Customers Marketing"),
        ("platform_total_60d", "Platform 60d Total"),
        ("platform_daily", "Platform Daily"),
        ("platform_weekly", "Platform Weekly"),
        ("platform_monthly", "Platform Monthly")
    ]
    
    changes_found = False
    for key, label in compare_keys:
        if key in current_metrics and key in previous_metrics:
            current_val = current_metrics[key]
            previous_val = previous_metrics[key]
            
            if current_val != previous_val:
                changes_found = True
                if isinstance(current_val, (int, float)):
                    diff = current_val - previous_val
                    if key.startswith("platform_"):
                        print(f"{label}: ${previous_val:,.2f} -> ${current_val:,.2f} (${diff:+,.2f})")
                    else:
                        print(f"{label}: {previous_val:,} -> {current_val:,} ({diff:+,})")
                else:
                    print(f"{label}: {previous_val} -> {current_val}")
    
    if not changes_found:
        print("No significant changes detected in key metrics")

def run_pipeline_from_folders() -> dict:
    """Main pipeline function"""
    print("=" * 60)
    print("PAYMENT PLATFORM ANALYTICS ETL PIPELINE")
    print(f"Run date: {TODAY}")
    print("=" * 60)
    
    # Discovery
    print("\n== DISCOVERY ==")
    merch_files = discover_files(DATA_GLOBS["merchants"])
    cust_files = discover_files(DATA_GLOBS["customers"]) 
    sales_files = discover_files(DATA_GLOBS["sales"])
    
    print(f"Discovered files:")
    print(f"  merchants: {len(merch_files)} files")
    print(f"  customers: {len(cust_files)} files")
    print(f"  sales: {len(sales_files)} files")
    
    # Load data
    print(f"\n== LOADING ==")
    merch = load_merchants()
    cust = load_customers()
    sales = load_sales()
    
    print(f"\nFinal loaded data:")
    print(f"  merchants: {len(merch)} rows")
    print(f"  customers: {len(cust)} rows") 
    print(f"  sales aggregates: {len(sales)} merchants")

    # Enrich and compute metrics
    enriched, metrics = enrich_and_metrics(merch, cust, sales)

    # Sanity checks / assertions
    print(f"\n== VALIDATION ==")
    assert len(enriched) >= 700, f"Merchant count unexpectedly low ({len(enriched)}); check merchant file and sheet selection."
    
    # Check window math consistency
    daily_sum_check = float(enriched["daily_est"].sum())
    platform_daily_check = metrics["platform_total_60d"] / 60.0
    math_diff = abs(daily_sum_check - platform_daily_check)
    assert math_diff < 1e-6, f"Window math mismatch: daily sum ({daily_sum_check}) vs platform/60 ({platform_daily_check})"
    
    # Check no double counting 
    item_merchants = enriched["net_sales_60d_item"].notna().sum()
    fallback_merchants = len(enriched) - item_merchants
    print(f"Coverage: {item_merchants} merchants with item data, {fallback_merchants} using fallback (MTD+LastMonth)")
    
    print(f"Validation passed!")

    # DIFF report
    previous_metrics = load_previous_metrics()
    print_diff_report(metrics, previous_metrics)
    save_current_metrics(metrics)

    print(f"\n== PIPELINE COMPLETE ==")
    print(f"Final metrics computed from {len(merch_files + cust_files + sales_files)} data files")
    
    return {
        "customers": cust, 
        "merchants_enriched": enriched, 
        "metrics": metrics,
        "diagnostics": {
            "files_discovered": {
                "merchants": len(merch_files),
                "customers": len(cust_files), 
                "sales": len(sales_files)
            },
            "data_loaded": {
                "merchants": len(merch),
                "customers": len(cust),
                "sales_merchants": len(sales)
            },
            "coverage": {
                "merchants_with_item_data": item_merchants,
                "merchants_using_fallback": fallback_merchants
            }
        }
    }
