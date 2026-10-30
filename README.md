# mini-rag (FROM NOTEBOOK TO PRODUCTION)

This project is mainly for learning about software engineering for AI-based systems. The first version includes a minimal implementation of a RAG model for question answering; later versions might include agentic workflows.

## Requirements

- [Git](https://git-scm.com/)
- [Miniconda](https://docs.anaconda.com/miniconda/)
- Python 3.8 or later
- **Windows users:** use [WSL2](https://learn.microsoft.com/windows/wsl/install) (Ubuntu) and run all commands below inside the WSL terminal.

## Installation

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd mini-rag-prod-version
```

### 2. Create and activate a conda environment

```bash
conda create -n mini-rag python=3.8
conda activate mini-rag
```

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Then open `.env` and fill in your own values.

## Run the server

```bash
uvicorn main:app --reload --port 8000
```

Then open http://localhost:8000/docs to check that the API is running. 

## python -m uvicorn main:app --reload --app-dir src
 

   
 
