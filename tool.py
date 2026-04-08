import pandas as pd
from crewai.tools import tool
import os

def smart_read_csv(path):
    """
    Highly resilient CSV reader that handles:
    1. Multiple encodings
    2. Auto-detection of separators (, or ;)
    3. Skipping of corrupted/malformed lines
    """
    for enc in ['utf-8', 'cp1252', 'latin1']:
        try:
            # sep=None with engine='python' triggers auto-detection
            # on_bad_lines='skip' prevents the 'Expected X fields' crash
            return pd.read_csv(path, encoding=enc, sep=None, engine='python', on_bad_lines='skip')
        except Exception:
            continue
    raise ValueError("File structure or encoding not supported.")

@tool("read_csv")
def read_csv(file_path: str):
    """Reads a CSV file. Input MUST be the filename only (e.g., 'data.csv')."""
    try:
        clean_path = str(file_path).strip().replace('"', '').replace("'", "").replace("\\", "/")
        if not os.path.exists(clean_path):
            return f"Error: {clean_path} not found."
            
        df = smart_read_csv(clean_path)
        return df.head(15).to_string()
    except Exception as e:
        return f"System Error reading file: {str(e)}"

@tool("analyze_csv")
def analyze_csv(file_path: str):
    """Computes stats for a CSV. Input MUST be the filename only (e.g., 'data.csv')."""
    try:
        clean_path = str(file_path).strip().replace('"', '').replace("'", "").replace("\\", "/")
        df = smart_read_csv(clean_path)
        
        stats = {
            "summary": df.describe().to_string(),
            "nulls": df.isnull().sum().to_string(),
            "duplicates": df.duplicated().sum(),
            "types": df.dtypes.to_string(),
            "columns": list(df.columns)
        }
        return str(stats)
    except Exception as e:
        return f"System Error analyzing file: {str(e)}"