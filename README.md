# AI-Powered Data Analyst

This lightweight, full-stack application allows users to upload CSV files and interactively analyze them using natural language. 
## Features

- Chat UI for CSV data  
  Ask questions like "What are the top 5 products by sales?" or "Plot average revenue by month".

- Python Tooling  
  Natural language queries are translated into Python code and executed on the CSV.

- Plot Support  
  Graphs, charts, and other visualizations are returned as images and displayed in the chat.

- Agent Memory  
  Maintains chat history across a session for more context-aware analysis.

## Getting Started

### 1. Clone and install dependencies

```bash
git clone https://github.com/adityacasturi/DataAnalyzer.git
cd DataAnalyzer
```

### 2. Set your environment

Create a `.env` file in the backend directory (or export directly) with your Google Gemini API key:

```env
GOOGLE_API_KEY=your_gemini_api_key
```

Or export it directly:

```bash
export GOOGLE_API_KEY=your_gemini_api_key
```

### 3. Start the backend

```bash
uvicorn backend.main:app --reload
```

This starts the FastAPI server at `http://localhost:8000`.

### 4. Start the frontend

```bash
cd frontend
streamlit run app.py
```

The application will open in your browser.