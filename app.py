import os
os.environ["OTEL_SDK_DISABLED"] = "true"

import streamlit as st
import pandas as pd
from datetime import datetime
from crew import run_data_crew
from pdf_utils import markdown_to_pdf

st.set_page_config(
    page_title="InsightPro | AI Data Intelligence", 
    page_icon="⚖️", 
    layout="wide"
)

# UNIVERSAL UI STYLING
st.markdown("""
    <style>
    .stApp { background-color: #333333; }
    .stApp h1, .stApp h2, .stApp h3, .stApp p, .stApp label { color: #e2e8f0 !important; }
    section[data-testid="stSidebar"] { background-color: #111827 !important; }
    
    /* CSS HACK: Change "Browse files" to "Browse file" */
    [data-testid="stFileUploader"] button div::before {
        content: "Browse file";
        visibility: visible;
        position: absolute;
        left: 0;
        right: 0;
    }
    [data-testid="stFileUploader"] button div {
        visibility: hidden;
    }

    /* Universal File Uploader Visibility */
    [data-testid="stFileUploaderText"] { color: #ffffff !important; }
    [data-testid="stFileUploader"] section {
        background-color: #1e293b !important;
        border: 1px dashed #60a5fa !important;
        border-radius: 8px;
    }

    .stButton>button { 
        background-color: #2563eb; 
        color: #ffffff !important; 
        border-radius: 8px; 
        font-weight: 600; 
        border: none;
    }
    
    .quality-high { color: #22c55e !important; font-weight: bold; }
    .quality-med { color: #f59e0b !important; font-weight: bold; }
    .quality-low { color: #ef4444 !important; font-weight: bold; }
    
    .streamlit-expanderHeader { 
        background-color: #1e293b !important; 
        color: #f8fafc !important; 
        border: 1px solid #475569;
        border-radius: 8px; 
    }
    </style>
    """, unsafe_allow_html=True)

def calculate_quality_score(df):
    if df.empty: return 0
    null_ratio = df.isnull().sum().sum() / df.size
    dup_ratio = df.duplicated().sum() / len(df) if len(df) > 0 else 0
    score = 100 - (null_ratio * 50) - (dup_ratio * 50)
    return max(0, min(100, score))

def main():
    st.title("⚖️ Data Insight Agent")
    
    with st.sidebar:
        st.header("Workspace")
        uploaded_file = st.file_uploader("Upload Source CSV", type=["csv"])
        st.caption("⚠️ AI can make mistakes. Verify critical data.")
        
        st.divider()
        if st.button("Reset Environment"):
            st.session_state.clear()
            st.rerun()

    if uploaded_file is not None:
        if 'df' not in st.session_state:
            success = False
            for enc in ['utf-8-sig', 'utf-8', 'cp1252', 'latin1']:
                try:
                    uploaded_file.seek(0)
                    st.session_state.df = pd.read_csv(
                        uploaded_file, 
                        encoding=enc, 
                        sep=None, 
                        engine='python', 
                        on_bad_lines='skip',
                        encoding_errors='replace'
                    )
                    success = True
                    break
                except Exception:
                    continue
            
            if not success:
                st.error("🚨 Critical Error: Could not decode file.")
                return
        
        df = st.session_state.df
        quality_score = calculate_quality_score(df)

        m1, m2, m3 = st.columns(3)
        with m1: st.metric("Total Records", f"{df.shape[0]:,}")
        with m2: st.metric("Attributes", df.shape[1])
        with m3:
            color_class = "quality-high" if quality_score > 80 else "quality-med" if quality_score > 50 else "quality-low"
            st.markdown(f"**Data Health**")
            st.markdown(f"<span class='{color_class}'>{quality_score:.1f}% Reliable</span>", unsafe_allow_html=True)

        with st.expander("🔍 Preview Raw Ingested Data"):
            # UPDATED: width='stretch' replaces use_container_width=True
            st.dataframe(df.head(20), width='stretch')

        st.divider()

        if st.button("Run Data Analysis 🚀"):
            local_filename = "active_dataset.csv"
            df.to_csv(local_filename, index=False)

            with st.status("🔍 Analyzing Data & Generating Reports...", expanded=True) as status:
                try:
                    results = run_data_crew(local_filename)
                    st.session_state.results = results
                    status.update(label="Analysis Complete", state="complete")
                    st.balloons()
                except Exception as e:
                    st.error(f"Execution Error: {e}")
                finally:
                    if os.path.exists(local_filename): 
                        os.remove(local_filename)

        if 'results' in st.session_state:
            res = st.session_state.results
            tab1, tab2 = st.tabs(["💎 Executive Report", "⚙️ Technical Audit"])

            with tab1:
                st.markdown(res['final_report'])
                st.divider()
                pdf_data = markdown_to_pdf(res['final_report'])
                if pdf_data:
                    st.download_button("📥 Export PDF Report", pdf_data, "Report.pdf")

            with tab2:
                st.subheader("Data Quality Audit")
                col_a, col_b = st.columns(2)
                with col_a:
                    st.write("**Missing Values Per Column**")
                    # UPDATED: width='stretch'
                    st.dataframe(df.isnull().sum(), width='stretch')
                with col_b:
                    st.write("**Data Consistency**")
                    st.info(f"Duplicate Rows: {df.duplicated().sum()}")
                    st.info(f"Memory Allocation: {df.memory_usage().sum() / 1024:.1f} KB")
                
                st.divider()
                st.subheader("Raw Analyst Logs")
                st.code(res['raw_analysis'], language="text")
    else:
        st.info("📊 **Ready for your next insight?** Feed me some data to unlock intelligence.")

if __name__ == "__main__":
    main()