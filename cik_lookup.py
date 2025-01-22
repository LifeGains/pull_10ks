import requests
import difflib

def get_match_ratio(str1: str, str2: str) -> float:
    """Calculate the similarity ratio between two strings."""
    return difflib.SequenceMatcher(None, str1.lower(), str2.lower()).ratio()

def fetch_cik(identifier: str = None) -> str:
    """
    Fetch the 10-digit CIK using a tiered matching approach.
    First tries exact ticker match, then falls back to company name matching.
    Returns 10-digit CIK as string, including leading zeros.
    """
    USER_AGENT = "Kevin/1.0 (ilikeyou1437@gmail.com) For personal use, not a bot"
    headers = {"User-Agent": USER_AGENT}
    search_url = "https://www.sec.gov/files/company_tickers.json"

    response = requests.get(search_url, headers=headers)
    response.raise_for_status()
    companies = response.json()

    # Step 1: Try ticker match first
    print("Enter company ticker: ")
    ticker = input().strip().upper()
    
    for company in companies.values():
        if company["ticker"].upper() == ticker:
            return str(company["cik_str"]).zfill(10), ticker, company["title"]
    
    # Step 2: If no ticker match, try company name
    print("\nNo exact ticker match found.")
    print("Enter company name: ")
    company_name = input().strip()
    
    best_match = None
    best_ratio = 0
    
    for company in companies.values():
        ratio = get_match_ratio(company_name, company["title"])
        if ratio > 0.5 and ratio > best_ratio:  # Must be >50% match
            best_ratio = ratio
            best_match = company
    
    if best_match:
        print(f"\nFound match: {best_match['title']} (Match confidence: {best_ratio:.1%})")
        
        return str(best_match["cik_str"]).zfill(10), best_match["ticker"], best_match["title"]
    
    raise ValueError(f"Unable to find CIK for company. Please verify the ticker or name.")

if __name__ == "__main__":
    try:
        cik, ticker, coname = fetch_cik()
        print(f"CIK found: {cik}")
    except Exception as e:
        print(f"Error: {e}")