from extract.normal_3 import *
from extract.pdf_3_adv import *
# from extract.pdf_3 import *
# from urllib.parse import urlparse
# from explain import *
from explain_url import *
from extract.date_me_3 import *
from info import *
import pandas as pd
from datetime import datetime
import csv
import os
import time
import json

# --- Configuration & Setup -----------------
# csv_name = "Red_notice_700_results"
# request user to provide input file path and output file name

print("Make sure input file have columns:  company_name,domain,keyword,company_url")
load = "All_yes"
csv_name = "json_update"
# load = input("Enter input file path __.csv : ")
# csv_name = input("Enter output file name __.csv : ")
CHECKPOINT_FILE = f"checkpoint/{csv_name}_checkpoint.csv"
INPUT_CSV_PATH = f"input/{load}.csv"


# File Header -------------------------------------
HEADERS = ["Company Name", "Domain", "Page URL", "Keyword", "Date", "Usage Indicated", "Explanation", "Processing Time (s)"]
# -------------------------------------------------


# ----- checkpoint function -----
def save_checkpoint(result: dict):
    """Appends a single result row to the checkpoint CSV file."""
    file_exists = os.path.exists(CHECKPOINT_FILE)
    try:
        with open(CHECKPOINT_FILE, "a", newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=HEADERS)
            if not file_exists:
                writer.writeheader()
            writer.writerow(result)
    except IOError as e:
        print(f"Error: Could not write to checkpoint file {CHECKPOINT_FILE}. {e}")


def load_processed_items():
    """Loads already processed (URL, Keyword) pairs from the checkpoint file to avoid re-work."""
    if not os.path.exists(CHECKPOINT_FILE):
        return set()
    try:
        df_checkpoint = pd.read_csv(CHECKPOINT_FILE)
        if "Page URL" in df_checkpoint.columns and "Keyword" in df_checkpoint.columns:
            return set(zip(df_checkpoint["Page URL"], df_checkpoint["Keyword"]))
        else:
            return set()
    except (pd.errors.EmptyDataError, KeyError, FileNotFoundError):
        return set()

# -------------------------

# --- Main Execution ---

def main():
    """Main function to run the processing script."""
    already_processed = load_processed_items()
    if already_processed:
        print(f"Found {len(already_processed)} items in the checkpoint file to skip.")

    try:
        df_input = pd.read_csv(INPUT_CSV_PATH)
        # --- CHANGE 1: Added 'domain' to the required columns check ---
        # required_columns = ['company_name', 'company_url', 'keyword', 'domain_name']
        required_columns = ['domain', 'company_url', 'keyword']
        if not all(col in df_input.columns for col in required_columns):
            print(f"Error: Input CSV '{INPUT_CSV_PATH}' must contain columns: {required_columns}")
            return
    except FileNotFoundError:
        print(f"Error: Input CSV file not found at '{INPUT_CSV_PATH}'")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading the input CSV: {e}")
        return

    all_new_results = []

    # Place where we take csv as input (Change the column name if needed)

    for index, row in df_input.iterrows():
        # --- CHANGE 2: Read all required columns from the row, including the new domain ---
        # comp_name = row['company_name']
        current_url = row['company_url']
        keyword = row['keyword']
        domain_from_csv = row['domain'] # This is the new Domain Name
        # -------------------------------------------------------- http Problem
        if not current_url.startswith(("http://", "https://")):
            current_url = "https://" + current_url
        # ----------------------------------------------------------------------
        if (current_url, keyword) in already_processed:
            continue
        # ----------------------------------------------------------------------
        # Company Name - Updated part
        company_name_from_csv = row.get('company_name')
        comp_name = info(current_url, company_name_from_csv=company_name_from_csv)
        # comp_name = info(current_url)

        start_time = time.time()
        print(f"Processing URL: {current_url}, Keyword: {keyword}, Company: {comp_name}")

        try:
            if current_url.lower().endswith(".pdf"):
                contexts, date = pdf(current_url, keyword)
                print("-> Using PDF function")
            else:
                contexts = normal(current_url, keyword)
                date = date_me(current_url)
                print("-> Using HTML function")

            # --- CHANGE 3: Use the domain from the CSV directly. The info() function is no longer needed. ---
            # home_url = domain_from_csv

            if not contexts:
                usage_indicated = "No"
                explanation = "No relevant keywords found on the page."
            else:
                gemini_analysis = explain(
                    chunk_text=contexts,
                    keyword_tech=keyword,
                    company_name=comp_name,
                    page_url=current_url  # Page url to LLM
                )
                usage_indicated = "Yes" if gemini_analysis.get("uses_tech") else "No"
                explanation = gemini_analysis.get("explanation", "No explanation provided.")

            result = {
                "Company Name": comp_name,
                "Domain": domain_from_csv,
                "Page URL": current_url,
                "Keyword": keyword,
                "Date": date or "Not found",
                "Usage Indicated": usage_indicated,
                "Explanation": explanation
            }

        except Exception as e:
            print(f"  [ERROR] Failed to process {current_url}: {e}")
            print("  -> Logging error and continuing to next URL.")

            result = {
                "Company Name": comp_name,
                "Domain": domain_from_csv,
                "Page URL": current_url,
                "Keyword": keyword,
                "Date": "Not found",
                "Usage Indicated": "Error",
                "Explanation": f"Failed to process URL. Error: {str(e)}"
            }

        duration = time.time() - start_time
        result["Processing Time (s)"] = round(duration, 2)

        print(f"  -> Completed in {duration:.2f} seconds.")

        save_checkpoint(result)
        all_new_results.append(result)


    if all_new_results:
        print(f"\n\n--- Processing Complete ---")
        # Create a base filename to use for both file types
        base_filename = f"{csv_name}_{datetime.now().strftime('%d-%m')}"
        os.makedirs("results_csv", exist_ok=True)
        os.makedirs("results_json", exist_ok=True)

        # --- 1. Save to CSV ---
        try:
            csv_path = os.path.join("results_csv", f"{base_filename}.csv")
            df_output = pd.DataFrame(all_new_results)
            df_output.to_csv(csv_path, index=False)
            print(f"Saved {len(all_new_results)} new results to '{csv_path}'")
        except Exception as e:
            print(f"  [ERROR] Failed to save CSV file: {e}")

        # --- 2. Save to JSON ---
        try:
            json_path = os.path.join("results_json", f"{base_filename}.json")
            # The `all_new_results` list is already in the perfect format for JSON
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(all_new_results, f, ensure_ascii=False, indent=4)
            print(f"Also saved results to '{json_path}'")
        except Exception as e:
            print(f"  [ERROR] Failed to save JSON file: {e}")

    else:
        print("\n\n--- Processing Complete ---")
        print("No new URLs were processed. All items in the input file were already in the checkpoint.")

if __name__ == "__main__":
    main()