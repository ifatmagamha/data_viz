from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from typing import List, Dict, Optional
import json
from datetime import datetime

from src.logging_setup import setup_logging
from src.config import settings
from src.services.dataset_service import prepare_dataset
from src.services.cleaning_service import auto_clean_dataset, get_data_quality_report, detect_column_types
from src.services.claude_service import generate_visualization_code
from src.services.execution_service import execute_visualization_code, format_code_for_display
from src.services.profiling_service import quick_profile, profile_to_text
from src.services.export_service import create_dashboard_html

setup_logging()

# Initialize session state essentials
if 'dataset_info' not in st.session_state:
    st.session_state.dataset_info = None
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = []
if 'analysis_requested' not in st.session_state:
    st.session_state.analysis_requested = False
if 'analysis_proposals' not in st.session_state:
    st.session_state.analysis_proposals = []

# Page configuration
st.set_page_config(
    page_title="Auto DataViz",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    :root {
        --primary-blue: #2563eb;
        --secondary-blue: #1e40af;
        --light-blue: #60a5fa;
        --dark-blue: #1e3a8a;
        --silver: #94a3b8;
        --light-silver: #cbd5e1;
        --dark-bg: #0f172a;
        --card-bg: #1e293b;
        --glass-bg: rgba(30, 41, 59, 0.7);
    }
    
    /* Main background */
    .stApp {
        background: #0f172a;
        background-attachment: fixed;
    }
    
    /* Header - More Minimalist */
    .main-header {
        padding: 4rem 2rem;
        border-radius: 0;
        color: white;
        text-align: left;
        margin-bottom: 3rem;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        background: transparent;
    }
    
    .main-header h1 {
        font-size: 3.5rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 0.5rem;
        background: linear-gradient(to right, #fff, #94a3b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.6;
        font-weight: 300;
        max-width: 600px;
    }
    
    /* Transparent Minimalist Cards */
    .analysis-card {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border-radius: 4px; /* More edgy/rectangular */
        padding: 2rem;
        margin: 1.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.05);
        box-shadow: none;
        transition: border-color 0.3s ease;
    }
    
    .analysis-card:hover {
        border-color: rgba(37, 99, 235, 0.5);
    }
    
    /* Section Headers - Clean & Typographic */
    .section-header {
        color: white;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.2em;
        margin: 4rem 0 1.5rem 0;
        opacity: 0.5;
    }
    
    /* Buttons - Minimalist Silver/Blue */
    .stButton>button {
        background: white;
        color: #0f172a !important;
        border: none;
        border-radius: 2px;
        padding: 0.8rem 2.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.2s ease;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    .stButton>button:hover {
        background: #60a5fa;
        color: white !important;
    }
    
    /* Metrics - Clean Grid */
    .metric-container {
        padding: 1.5rem 0;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: white;
    }
    
    .metric-label {
        font-size: 0.75rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    /* Sidebar - Minimal */
    [data-testid="stSidebar"] {
        background: #0d121f;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    [data-testid="stSidebar"] .stMarkdown {
        color: #e2e8f0;
    }
    
    /* Expanders */
    .streamlit-expanderHeader {
        background: var(--glass-bg);
        backdrop-filter: blur(10px);
        border-radius: 4px;
        font-weight: 600;
        color: #e2e8f0;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .streamlit-expanderHeader:hover {
        border-color: rgba(37, 99, 235, 0.5);
    }
    
    /* Code blocks */
    .stCodeBlock {
        background: #0f172a;
        border-radius: 4px;
        border-left: 4px solid #2563eb;
    }
    
    /* Dataframe */
    .stDataFrame {
        border-radius: 4px;
        overflow: hidden;
        box-shadow: none;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Progress indicators */
    .stProgress > div > div {
        background: linear-gradient(90deg, #2563eb 0%, #3b82f6 100%);
    }
    
    /* Animations */
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0%, 100% {
            opacity: 1;
        }
        50% {
            opacity: 0.7;
        }
    }
    
    .pulse {
        animation: pulse 2s ease-in-out infinite;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .status-success {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: white;
    }
    
    .status-info {
        background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        margin: 3rem 0 1rem 0;
    }
    
    /* Action Cards */
    .stFileUploader {
        border: 2px dashed #e2e8f0;
        border-radius: 12px;
        padding: 2rem;
        background: white;
    }
    
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 2rem;
    }
    
    /* Analysis Results Cards */
    .analysis-card {
        background: white;
        border-radius: 12px;
        padding: 2rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
</style>
""", unsafe_allow_html=True)

# Main Entrance
st.markdown("""
<div class="hero-section">
    <h1 class="hero-title">
        Analyzing <span class="insights">insights</span>, 
        <span class="visualizations">visualizations</span> and 
        <span class="reports">reports</span>
    </h1>
    <p class="hero-subtitle">
        Upload your data and let AI generate meaningful insights instantly. No coding required.
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("<div class='section-header'>Data Source</div>", unsafe_allow_html=True)
    data_source = st.radio(
        "Source",
        ["📤 CSV", "🤗 HuggingFace", "Example"],
        label_visibility="collapsed"
    )

# Main content
col_main = st.container()

with col_main:
    # Data Loading Section
    dataset_info = None
    
    if data_source == "📤 CSV":
        uploaded_file = st.file_uploader(
            "Upload CSV",
            type=["csv"],
            help="Upload a CSV file to begin analysis"
        )
        
        if uploaded_file:
            with st.spinner("Loading dataset..."):
                try:
                    dataset_info = prepare_dataset(uploaded_file, source_type="csv")
                    st.session_state.dataset_info = dataset_info
                    st.success(f"Ready: {dataset_info.name}")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    elif data_source == "🤗 HuggingFace":
        col1, col2 = st.columns([4, 1])
        with col1:
            hf_dataset = st.text_input(
                "Dataset name",
                value="maharshipandya/spotify-tracks-dataset",
                placeholder="username/dataset-name"
            )
        with col2:
            hf_split = st.selectbox("Split", ["train", "test"], index=0)
        
        if st.button("Load Dataset", width="stretch"):
            with st.spinner(f"Loading {hf_dataset}..."):
                try:
                    dataset_info = prepare_dataset(hf_dataset, source_type="huggingface")
                    st.session_state.dataset_info = dataset_info
                    st.success(f"Ready: {dataset_info.name}")
                except Exception as e:
                    st.error(f"Error: {e}")
    
    else:  
        example_choice = st.selectbox(
            "Choose example:",
            ["Spotify Tracks", "Movies", "Housing", "Sales"]
        )
        
        if st.button("Load Example", width="stretch"):
            example_map = {
                "Movies": "examples/movies.csv",
                "Housing": "examples/housing.csv",
                "Sales": "examples/sales.csv"
            }
            
            if example_choice == "Spotify Tracks":
                with st.spinner("Loading Spotify dataset..."):
                    try:
                        dataset_info = prepare_dataset(
                            "maharshipandya/spotify-tracks-dataset",
                            source_type="huggingface"
                        )
                        st.session_state.dataset_info = dataset_info
                        st.success("Ready: Spotify Tracks")
                    except:
                        st.error("Error loading example.")
            else:
                try:
                    with open(example_map[example_choice], 'rb') as f:
                        dataset_info = prepare_dataset(f, source_type="csv", dataset_name=example_choice)
                        st.session_state.dataset_info = dataset_info
                        st.success(f"Ready: {example_choice}")
                except:
                    st.warning("File not found.")
    
    # If dataset is loaded
    if st.session_state.get('dataset_info'):
        dataset_info = st.session_state.dataset_info
        
        st.markdown("---")
        
        # Data Quality Dashboard
        st.markdown('<div class="section-header">Data Quality Dashboard</div>', unsafe_allow_html=True)
        
        quality_report = get_data_quality_report(dataset_info.df)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Rows</div>
                <div class="metric-value">{quality_report['n_rows']:,}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Columns</div>
                <div class="metric-value">{quality_report['n_columns']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Duplicates</div>
                <div class="metric-value">{quality_report['duplicates']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-container">
                <div class="metric-label">Memory</div>
                <div class="metric-value">{quality_report['memory_usage_mb']:.1f}<span style="font-size:1rem;">MB</span></div>
            </div>
            """, unsafe_allow_html=True)
        
        # Dataset Preview
        with st.expander("Dataset Preview", expanded=False):
            st.dataframe(
                dataset_info.df.head(settings.max_rows_preview),
                width="stretch",
                height=350
            )
        
        # Column Analysis
        with st.expander("Column Analysis", expanded=False):
            col_types = detect_column_types(dataset_info.df)
            
            type_counts = {}
            for dtype in col_types.values():
                type_counts[dtype] = type_counts.get(dtype, 0) + 1
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**Column Types Distribution:**")
                for dtype, count in type_counts.items():
                    st.markdown(f"- **{dtype.capitalize()}**: {count} columns")
            
            with col2:
                st.markdown("**Detected Types:**")
                for col, dtype in list(col_types.items())[:10]:
                    st.markdown(f"- `{col}`: {dtype}")
        
        st.markdown("---")
        
        # AI Analysis Section
        st.markdown('<div class="section-header">AI-Powered Analysis</div>', unsafe_allow_html=True)
        
        analysis_context = st.text_area(
            "📝 Provide context about your data (optional but recommended)",
            placeholder="e.g., This is music streaming data. I want to understand user preferences and track characteristics that drive popularity.",
            height=100
        )
        
        if st.button("Generate Comprehensive Analysis", type="primary", width='stretch'):
            with st.spinner("AI Senior Analyst is exploring your data patterns..."):
                try:
                    # Refresh dataset_info from state
                    dataset_info = st.session_state.dataset_info
                    
                    # Detect column types
                    col_types = detect_column_types(dataset_info.df)
                    
                    # Get profiling data for context
                    profile = quick_profile(dataset_info.df)
                    profile_text = profile_to_text(profile)
                    
                    # Generate multi-graph proposals using the router (handles fallbacks)
                    from src.services.llm_router import generate_analysis_proposals
                    proposals = generate_analysis_proposals(
                        dataset_context=analysis_context,
                        schema=dataset_info.schema_summary,
                        sample_data=dataset_info.sample_data,
                        column_types=col_types,
                        stats_summary=profile_text[:1000]
                    )
                    
                    st.session_state.analysis_proposals = proposals
                    st.session_state.analysis_requested = True
                    st.success(f"Generated {len(proposals)} professional visualization proposals!")
                except Exception as e:
                    st.error(f"Analysis Error: {e}")
        
        # Show analysis results
        if st.session_state.get('analysis_requested') and st.session_state.get('analysis_proposals'):
            proposals = st.session_state.analysis_proposals
            
            st.markdown('<div class="section-header">Strategic Insights & Visualizations</div>', unsafe_allow_html=True)
            
            # Successful figures list for export
            successful_figures = []
            successful_titles = []
            successful_interps = []
            successful_recs = []
            
            for i, prop in enumerate(proposals):
                with st.container():
                    st.markdown(f"""
                    <div class="analysis-card">
                        <h3 style='color: #0f172a; margin-top: 0;'>{i+1}. {prop['title']}</h3>
                        <div style='margin-bottom: 1rem;'>
                            <span style='background: #e2e8f0; color: #475569; padding: 0.2rem 0.8rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;'>{prop['chart_type']}</span>
                        </div>
                        <p style='color: #334155;'><strong>Business Purpose:</strong> {prop['purpose']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Execute code
                    fig, stdout, error = execute_visualization_code(prop['code'], dataset_info.df)
                    
                    if error:
                        st.error(f"Error generating graph: {error}")
                    elif fig:
                        st.plotly_chart(fig, width='stretch', key=f"analysis_viz_{i}")
                        successful_figures.append(fig)
                        successful_titles.append(prop['title'])
                        successful_interps.append(prop['interpretation'])
                        successful_recs.append(prop['recommendations'])
                        
                        # Interpretation
                        st.markdown(f"""
                        <div style='background: #f8fafc; padding: 1.5rem; border-radius: 12px; border-left: 4px solid #3b82f6; margin-top: 1rem;'>
                            <h4 style='color: #1e3a8a; margin-top: 0;'>Senior Analyst Interpretation</h4>
                            <p style='color: #334155;'>{prop['interpretation']}</p>
                            <h4 style='color: #1e3a8a; margin-top: 1rem;'>Actionable Recommendations</h4>
                            <p style='color: #334155;'>{prop['recommendations']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
            
            # Comprehensive Report Export
            if successful_figures:
                st.markdown("---")
                st.markdown("<div class='section-header'>Document Export</div>", unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    # Generate HTML Report
                    if st.button("Generate Full HTML Report", width='stretch'):
                        try:
                            report_html = create_dashboard_html(
                                figures=successful_figures,
                                titles=successful_titles,
                                interpretations=successful_interps,
                                recommendations=successful_recs,
                                question=st.session_state.get('analysis_context', "General Data Analysis"),
                                dataset_name=dataset_info.name
                            )
                            
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            st.download_button(
                                "Download Analysis Report (HTML)",
                                data=report_html,
                                file_name=f"analysis_report_{timestamp}.html",
                                mime="text/html",
                                width='stretch'
                            )
                        except Exception as e:
                            st.error(f"Failed to generate report: {e}")
                
                with col2:
                    st.info("The HTML report contains all visualizations above with full interactive capabilities and analysis text.")
    
    else:
        # Welcome screen
        st.markdown("""
        <div style='text-align: center; padding: 4rem 2rem; color: #cbd5e1;'>
            <h2 style='color: #60a5fa; margin-bottom: 1rem;'>👋 Welcome to Auto DataViz</h2>
            <p style='font-size: 1.2rem; margin-bottom: 2rem;'>
                Your AI-powered data analysis platform with senior analyst insights
            </p>
            <div style='display: flex; justify-content: center; gap: 2rem; flex-wrap: wrap; margin-top: 2rem;'>
                <div class='analysis-card' style='max-width: 300px;'>
                    <h3 style='color: #60a5fa;'>📤 Upload Data</h3>
                    <p>Start with your own CSV file</p>
                </div>
                <div class='analysis-card' style='max-width: 300px;'>
                    <h3 style='color: #60a5fa;'>🤗 HuggingFace</h3>
                    <p>Load from public datasets</p>
                </div>
                <div class='analysis-card' style='max-width: 300px;'>
                    <h3 style='color: #60a5fa;'>📊 Examples</h3>
                    <p>Try pre-loaded datasets</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
