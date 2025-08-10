# Verification Engine: AI-Powered Technology Stack Analysis

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen.svg" alt="Status">
</p>

This Script is a Python-based tool designed to analyze web pages and PDF documents for the presence of specific keywords. It extracts relevant text, determines if the keyword is used in a meaningful context, and provides an explanation for its findings.

## Key Technologies & Libraries

<p align="center">
  <img src="https://img.shields.io/badge/Pandas-2.2.3-blue" alt="Pandas">
  <img src="https://img.shields.io/badge/Selenium-4.33.0-green" alt="Selenium">
  <img src="https://img.shields.io/badge/Crawl4AI-0.6.3-purple" alt="Crawl4AI">
  <img src="https://img.shields.io/badge/Playwright-1.53.0-blue" alt="Playwright">
  <img src="https://img.shields.io/badge/Google_Gemini-AI-orange" alt="Gemini AI">
  <img src="https://img.shields.io/badge/BeautifulSoup-4.13.4-lightgrey" alt="BeautifulSoup">
</p>

## The Problem It Solves

Manually verifying a company's technology stack is a time-consuming and often inaccurate process. This engine was built to automate and enhance this process, providing reliable, data-driven insights with minimal human effort.

| Challenge (The Manual Way) | Solution (Verification Engine) |
| :--- | :--- |
| **High Time & Effort** | Automates the analysis of hundreds of URLs, saving countless hours of manual work. |
| **Low Accuracy** | Uses generative AI to understand context, distinguishing real usage from casual mentions or irrelevant matches. |
| **Difficult to Scale** | Processes large CSV files in batches, making it possible to analyze entire market segments. |
| **Unstructured Data** | Outputs clean, structured data in CSV and JSON formats, ready for immediate analysis and reporting. |

## Key Features

* **Multi-Format Content Analysis:** Seamlessly processes both live websites (HTML) and PDF documents, extracting text from complex layouts.
* **AI-Powered Contextual Verification:** Leverages Google's Gemini large language model to move beyond simple keyword matches. It analyzes the surrounding text to determine if a technology is being used operationally, mentioned in passing, or used in a different context.
* **Intelligent Date Extraction:** Employs a multi-layered heuristic approach to identify the publication or modification date of content by searching URL patterns, metadata, and document text.
* **Scalable & Resilient Processing:** Built to handle large datasets from a CSV input. A robust checkpointing system saves progress to both CSV and JSON formats, allowing you to resume lengthy analysis tasks without data loss.
* **Structured Data Output:** Generates clean, analysis-ready output in both CSV and JSON formats, detailing the company, domain, keyword, verification status, and a clear explanation from the AI model.

## Getting Started

Follow these instructions to get a local copy up and running.

### Prerequisites

* Python 3.9 or higher
* An active Google Gemini API key.

### Installation & Configuration

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Krishna9588/Verification_Engine.git
    cd Verification_Engine
    ```

2.  **Install dependencies using a Virtual Environment:**
    ```bash
    # Create and activate a virtual environment
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

    # Install required libraries from the requirements file
    pip install -r requirements.txt
    ```

3.  **Configure API Keys:**
    Open the `explain_url.py` file and add your Google Gemini API keys to the `API_KEYS` list. The script includes a key rotation feature to cycle through multiple keys if needed.

    ```python
    # In explain_url.py
    API_KEYS = ["YOUR_API_KEY_1",
                "YOUR_API_KEY_2",
                # Add more keys if you have them
               ]
    ```

## Usage

The Verification Engine is designed to be run from the command line and uses a CSV file for batch processing.

### 1. Prepare the Input CSV

Create a CSV file (e.g., `input/my_companies.csv`) with the following columns:
* `company_name`: The name of the company (optional, can be derived from the URL).
* `domain`: The company's primary domain (e.g., `example.com`).
* `keyword`: The technology or software keyword to search for (e.g., `AWS`, `VMware`).
* `company_url`: The specific URL of the page or PDF to analyze.

**Example `input.csv`:**
   ```csv
   company_name,domain,keyword,company_url
   Birlasoft,birlasoft.com,AWS,https://www.birlasoft.com/services/enterprise-products/aws
   Example,"example.com",Glue,https://www.example.com/sustainability-report.pdf
   ```

### 2. Run the Engine

Execute the main script from the project's root directory. The script will guide you through the process.

   ```bash
   python main_working_json.py
   ```

### 3. Review the Output
Upon completion, the script will generate:
* A CSV file in the results_csv/ directory.
* A JSON file in the results_json/ directory.
* Checkpoint files in the checkpoint/ and checkpoint_json/ directories, which log each result as it's processed.

### Contributing
Contributions are welcome! If you have suggestions for improving the engine, please feel free to fork the repository, make your changes, and submit a pull request. You can also open an issue to report bugs or suggest new features.
