# GitHub Repository Summarizer API

This project implements an API service that accepts a public GitHub repository URL and returns a human-readable summary of the project using an LLM (accessed through Nebius Token Factory).

The API analyzes repository contents, selects the most informative files, and generates:

* A description of what the project does
* The main technologies used
* A brief explanation of the repository structure

## API Endpoint

### POST `/summarize`

Request body:

```json
{
  "github_url": "GITHUB_URL"
}
```

Successful response:

```json
{
  "summary": "Human-readable description of the project",
  "technologies": ["Python", "ExampleLib"],
  "structure": "Brief description of repository layout"
}
```

Error response:

```json
{
  "status": "error",
  "message": "Description of what went wrong"
}
```

## Setup and Run Instructions

The following instructions assume a clean Linux/macOS machine with Python installed.

### 1. Obtain the project source

Unzip the provided archive or clone the repository:

```bash
unzip repo_summarizer.zip
cd repo_summarizer
```


### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
```

Activate it:


```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure LLM access API key

Set your LLM access API key (e.g., Nebius Token Factory) using an environment variable.

```bash
export API_KEY=YOUR_API_KEY
```

### 5. Start the server

Run:

```bash
uvicorn app.main:app --reload
```

The server starts at:

```
http://localhost:8000
```


### 6. Test the endpoint

Test the service using:

```bash
curl -X POST http://localhost:8000/summarize \
  -H "Content-Type: application/json" \
  -d '{"github_url": "https://github.com/psf/requests"}'
```

A successful request returns a summary JSON response.


## LLM Model Choice

The implementation uses `meta-llama/Llama-3.3-70B-Instruct` due to its strong reasoning capabilities and reliable instruction-following, which are essential for analyzing diverse repository files and generating consistent structured JSON output. Its refined instruct tuning helps reduce formatting errors, and its pricing model offers a practical balance between accuracy, speed, and operational cost for repository-scale analysis.


## Repository Processing Approach

Since repositories can be very large, sending all files to the the LLM may exceed context limits and cost lots of tokens. 
The service selects only the most informative content. Below is a description of the selection strategy.

### Included Content

The service prioritizes:

* README files
* Dependency files (`requirements.txt`, `pyproject.toml`, `package.json`, etc.)
* Configuration and setup files
* Representative source files
* Directory structure information

These files provide strong signals about project purpose, technologies, and organization.


### Skipped Content

The service ignores files and folders that add little semantic value or are unnecessarily large, including:

* Generated directories (`node_modules`, `dist`, `build`, etc.)
* Cache and compiled output folders
* Binary files (images, archives, executables)
* Lock files and temporary artifacts


### Context Size Management

To stay within LLM context limits:

* Only a subset of source files is sampled
* Large files are truncated
* Total context size is capped

This ensures large repositories can still be summarized efficiently without exceeding model limits.
