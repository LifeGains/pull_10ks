import requests
import re

def fetch_cik(identifier):
    """
    Fetch the 10-digit CIK for a given company name or ticker symbol.
    :param identifier: Company name or ticker symbol.
    :return: 10-digit CIK as a string, including leading zeros.
    """
    USER_AGENT = "Kevin/1.0 (ilikeyou1437@gmail.com) For personal use, not a bot"
    headers = {"User-Agent": USER_AGENT}
    search_url = f"https://www.sec.gov/files/company_tickers.json"

    response = requests.get(search_url, headers=headers)
    response.raise_for_status()

    companies = response.json()
    identifier_lower = identifier.lower()

    for company in companies.values():
        if (company["ticker"].lower() == identifier_lower or
            identifier_lower in company["title"].lower()):  # Loosen match for company name
            return str(company["cik_str"]).zfill(10)

    raise ValueError(f"Unable to find CIK for identifier: {identifier}")

if __name__ == "__main__":
    identifier = input("Enter company ticker or name: ").strip()
    try:
        cik = fetch_cik(identifier)
        print(f"The CIK for '{identifier}' is: {cik}")
    except Exception as e:
        print(f"Error: {e}")