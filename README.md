# 📊 Auto DataViz - Where Data Meets Storytelling

> An AI-powered data visualization application that transforms your questions into stunning, interactive visualizations

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31+-FF4B4B.svg)](https://streamlit.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- ** AI-Powered Code Generation**: Uses Claude 3.5 Sonnet to generate Python visualization code
- ** Multiple Data Sources**: Upload CSV, load from HuggingFace, or use example datasets
- ** Automatic Data Cleaning**: Smart detection and handling of missing values, duplicates
- ** Intelligent Insights**: AI-generated interpretations and recommendations
- ** Beautiful Design**: Flourish-inspired modern UI with gradient themes
- ** Multiple Export Formats**: PNG and HTML exports
- ** Data Quality Reports**: Comprehensive analysis of your dataset
- ** Interactive**: Real-time visualization generation and exploration

##⚡Quick Start

### Prerequisites

- Python 3.10 or higher
- Claude API key (get one from [Anthropic](https://console.anthropic.com/))

### Installation

```bash
# Accéder au dossier du projet
cd "data_viz"

# Installer les dépendances
pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env and add your CLAUDE_API_KEY
```

### Lancement Local

```bash
# Toujours lancer depuis le dossier data_viz
streamlit run app.py
```

L'application sera accessible sur `http://localhost:8501`

## Deployment

### Streamlit Cloud

To deploy this application to Streamlit Cloud:

1. Push your code to a GitHub repository.
2. Connect your GitHub account to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Create a new app and point it to your `app.py` file.
4. **Important**: In the app settings, go to the **Secrets** section and add your API keys:

```toml
CLAUDE_API_KEY = "your-api-key-here"
GEMINI_API_KEY = "your-api-key-here"
# Optional:
OPENAI_API_KEY = "your-api-key-here"
```

The application is configured to automatically check both Streamlit Secrets and `.env` variables, prioritizing Secrets for cloud deployment.

## 📖 Usage

### 1. Load Your Data

Choose from three options:
- **Upload CSV**: Drag and drop your CSV file
- **HuggingFace Dataset**: Load from HuggingFace datasets (e.g., `maharshipandya/spotify-tracks-dataset`)
- **Example Dataset**: Try pre-loaded examples (Movies, Housing, Sales, Spotify)

### 2. Explore Your Data

- View data quality metrics
- Check for missing values and duplicates
- Preview your dataset
- Review schema and column types

### 3. Ask Questions

Type natural language questions about your data:
- "What is the relationship between popularity and danceability?"
- "Which artists have the most tracks?"
- "How has music evolved over time?"
- "What factors influence house prices?"

### 4. Get Visualizations

The AI will:
1. Analyze your question and dataset
2. Generate Python code using Plotly
3. Execute the code safely
4. Display the interactive visualization
5. Provide insights and interpretations

### 5. Export Results

Download your visualizations as:
- **PNG**: High-quality static images
- **HTML**: Interactive standalone files

## 🎨 Example Use Cases

### Spotify Tracks Analysis

```python
# Load Spotify dataset
dataset = "maharshipandya/spotify-tracks-dataset"

# Ask questions like:
"Which genres have the highest average energy?"
"How does danceability correlate with popularity?"
"What are the trends in music characteristics over decades?"
```

### Real Estate Analysis

```python
# Upload housing.csv

# Ask questions like:
"What factors most influence house prices?"
"How does location affect property values?"
"What is the relationship between size and price?"
```

## LLM Scaffolding: Senior analyst Engine

This project implements advanced **LLM Scaffolding** to ensure Claude 3.5 Sonnet behaves as a reliable, professional software component rather than a generic chatbot.

### Scaffolding Principles Applied

1. **Persona Scaffolding (Identity)**
   - **Concept**: Defining a strict role-play boundary for the LLM.
   - **Implementation**: We define Claude as a "Senior Data Analyst with 15+ years of experience." This forces professional terminology and a focus on business value.

2. **Context Scaffolding (Grounding)**
   - **Concept**: Providing external "ground truth" to prevent hallucinations.
   - **Implementation**: Every prompt is scaffolded with:
     - **Schema Metadata**: Exact column names and data types.
     - **Sample Data**: Real-world examples of row entries.
     - **Statistical Profiling**: Distribution, missing values, and cardinality stats.

3. **Output Railing (Structural Consistency)**
   - **Concept**: Forcing the model to adhere to a machine-readable format.
   - **Implementation**: We use **JSON Scaffolding**. Claude is instructed to return only valid JSON blocks. Our backend includes a robust extraction logic to parse these blocks and feed them into the Python execution engine.

4. **Safety Scaffolding (Security Architecture)**
   - **Concept**: Validating AI outputs before they interact with the system.
   - **Implementation**: Every line of AI-generated Python code passes through a **Security Filter** that blocks dangerous imports (`os`, `sys`, `subprocess`) and forbidden operations (`eval`, `exec` on user strings) before execution.

5. **Retry & Repair Logic**
   - **Concept**: Handling the probabilistic nature of LLMs.
   - **Implementation**: If the LLM generates malformed JSON or invalid code, the application automatically retries the generation up to 3 times, refining the prompt based on the previous failure.

---

## Architecture

```
src/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration management
├── services/
│   ├── dataset_service.py      # Data loading (CSV, HuggingFace)
│   ├── cleaning_service.py     # Automatic data cleaning
│   ├── claude_service.py       # Claude API integration
│   ├── execution_service.py    # Safe code execution
│   ├── profiling_service.py    # Data profiling
│   └── export_service.py       # Export functionality
└── models/
    └── viz_spec.py             # Data models
```

## ⚙️ Configuration

Edit `.env` to customize:

```bash
# LLM Provider
LLM_PROVIDER=claude

# API Keys
CLAUDE_API_KEY=your_key_here

# Dataset Limits
MAX_ROWS_ANALYSIS=10000
MAX_ROWS_PREVIEW=50

# Data Cleaning
AUTO_CLEAN=true
MISSING_THRESHOLD=0.5

# Code Execution
ENABLE_CODE_EXECUTION=true
MAX_CODE_EXECUTION_TIME=30
```

## Security

- **Safe Code Execution**: Sandboxed environment with timeout limits
- **Code Validation**: Blacklist of dangerous operations
- **No File System Access**: Generated code cannot access files
- **API Key Protection**: Environment variables for sensitive data

## Supported Chart Types

The AI can generate various visualization types:
- **Bar Charts**: Comparisons and rankings
- **Line Charts**: Trends over time
- **Scatter Plots**: Correlations and relationships
- **Box Plots**: Distributions and outliers
- **Histograms**: Frequency distributions
- **Heatmaps**: Multi-dimensional patterns
- **And more**: Violin plots, area charts, pie charts, etc.

## Best Practices

1. **Clear Questions**: Be specific about what you want to visualize
2. **Clean Data**: Use the auto-clean feature for better results
3. **Appropriate Size**: Limit datasets to <10,000 rows for optimal performance
4. **Iterative Exploration**: Ask follow-up questions to dive deeper
