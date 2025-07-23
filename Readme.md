# Web Content Analyzer

This Script is a Python-based tool designed to analyze web pages and PDF documents for the presence of specific keywords. It extracts relevant text, determines if the keyword is used in a meaningful context, and provides an explanation for its findings.

## Features

*   **Web Page and PDF Analysis:**  Analyzes both standard web pages (HTML) and PDF documents.
*   **Keyword Detection:**  Identifies the presence of specified keywords within the content.
*   **Contextual Analysis:**  Uses a powerful language model (Gemini) to understand the context in which a keyword is used and determine if it's relevant.
*   **Date Extraction:**  Attempts to find the publication date of the content from various sources.
*   **CSV Input/Output:**  Takes a CSV file as input and generates a new CSV file with the analysis results.
*   **Checkpointing:**  Saves progress to a checkpoint file, allowing you to resume processing if interrupted.

## Project Structure

The project is organized into the following files and directories:

*   **`main.py`**: The main script that orchestrates the entire process. It reads the input CSV, calls the necessary functions for each URL, and writes the results to an output file.
*   **`extract/`**: This directory contains modules for extracting text from different sources.
    *   `normal.py`:  Handles the extraction of text from standard HTML web pages.
    *   `pdf.py`:  Handles the extraction of text from PDF documents.
    *   `date_me.py`:  A utility for extracting the publication date from a web page.
*   **`explain.py`**:  This module contains the logic for interacting with the Gemini language model to analyze the extracted text and determine if the keyword usage is relevant.
*   **`info.py`**: This module contains the logic of gathering company name and correct link.
## Getting Started

### Prerequisites

*   Python 3.x
*   Required Python libraries (install using `pip`):
    *   `pandas`
    *   `requests`
    *   `beautifulsoup4`
    *   `PyMuPDF`
    *   `google-generativeai`

You can install these dependencies with the following command:
