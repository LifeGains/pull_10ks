import requests
import os
import cik_lookup
from datetime import datetime

# Set up constants
BASE_URL = "https://data.sec.gov/submissions/"
USER_AGENT = "Kevin/1.0 (ilikeyou1437@gmail.com) For personal use, not a bot"
SAVE_DIR = r"C:\Users\kevin\google_drive_life_gains\My Drive\Github\Repos\sec_10k_puller\all_10k_filings"
GPT_ENDPOINT = "https://chatgpt.com/g/g-6761212046648191a582b7f3616c29b6-business-interpreter"

# Function to fetch the company filings
def fetch_company_filings(cik):
    headers = {"User-Agent": USER_AGENT}
    url = f"{BASE_URL}CIK{cik}.json"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

# Function to download a specific filing
def download_filing(filing_url, save_path):
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(filing_url, headers=headers, stream=True)
    response.raise_for_status()
    with open(save_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=1024):
            f.write(chunk)

# Function to filter filings by form type and year range
def filter_filings(filings, form_type, years_to_fetch):
    current_year = datetime.now().year
    filtered_filings = []

    for index, form in enumerate(filings.get("form", [])):
        if form == form_type:
            filing_date = filings["filingDate"][index]  # Filing date
            filing_year = datetime.strptime(filing_date, "%Y-%m-%d").year

            # Check if the filing falls within the desired year range
            if current_year - filing_year < years_to_fetch:
                accession_number = filings["accessionNumber"][index].replace("-", "")
                primary_doc = filings["primaryDocument"][index]
                reporting_year = filings["reportDate"][index].split("-")[0]
                filing_url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}/{primary_doc}"
                
                filtered_filings.append((filing_url, reporting_year))
    return filtered_filings

# Function to process HTML content with GPT
def process_with_gpt(html_content):
    headers = {"User-Agent": USER_AGENT, "Content-Type": "application/json"}
    payload = {"html": html_content}
    response = requests.post(GPT_ENDPOINT, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()

# Main function
if __name__ == "__main__":
    os.makedirs(SAVE_DIR, exist_ok=True)

    identifier = input("Enter Ticker: ").strip().upper()
    print("Fetching CIK...")
    cik = cik_lookup.fetch_cik(identifier)
    print("CIK:", cik)

    years_to_fetch = int(input("Enter the number of years of filings to pull: ").strip())
    
    print("Fetching filings...")
    
    # Get json associated with cik
    data = fetch_company_filings(cik)
    # print(data)
    # Get exact accessionNumbers of all filings
    filings_recent = data.get("filings", {}).get("recent", [])
    print(filings_recent)
    filings = filings_recent
    
    # filings_files = data.get("filings", {}).get("files", [])
    # # Convert list of filings into a dictionary-like structure
    # if filings_files:
    #     filings_dict = {
    #         key: [item[key] for item in filings_files if key in item]
    #         for key in filings_files[0]
    #     }
    #     print(filings_dict)
        # filings = filings_dict
    # else:
    #     filings_dict = {}
        # filings = filings_dict
    
    # raise Exception("break")

    # print(filings)
    # print("Available keys in filings['recent']:", sorted(filings.keys()))

    # Fetch and download filings for each form type
    for form_type in ["10-K", "DEF 14A"]:
        print(f"Processing {form_type} filings...")
        form_filings = filter_filings(filings, form_type, years_to_fetch)

        for filing_url, reporting_year in form_filings:
            print(f"Downloading {form_type} filing: {filing_url}")

            save_path = os.path.join(SAVE_DIR, identifier, f"{identifier}_{reporting_year}_{form_type}.html")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)  # Ensure directory exists
            print(f"Save path: {save_path}")
            download_filing(filing_url, save_path)

    print(f"All 10-K filings downloaded to '{SAVE_DIR}' folder.")

    # Run entire html from filing_url_list[0] through this custom GPT located here (https://chatgpt.com/g/g-6761212046648191a582b7f3616c29b6-business-interpreter) 
    # and return the GPT's response here. 

    # if filing_url_list:
    #     print("Processing with GPT:", filing_url_list[0])
    #     first_filing_url = filing_url_list[0]
    #     response = requests.get(first_filing_url, headers={"User-Agent": USER_AGENT})
    #     response.raise_for_status()
    #     html_content = response.text
    #     gpt_response = process_with_gpt(html_content)
    #     print("GPT Response:", gpt_response)