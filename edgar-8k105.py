# 05-29-2024: Initial release of edgar-8k105.py
# Kulkan Security - www.kulkan.com
import requests, json, re
from datetime import datetime
import pandas as pd
import yfinance as yf


# The SEC requests callers to identify themselves, as described at https://www.sec.gov/os/accessing-edgar-data
USER_AGENT = 'Your Company Name (contact@example.com)'

def get_filings(filing_type, start_date, end_date, max_results=999999):
    base_url = "https://efts.sec.gov/LATEST/search-index"
    results = []
    fetched_results = 0
    page_size = 100  
    total_available_results = None  # To track the total results available as reported by the server

    while fetched_results < max_results:
        query = {
            # We don't only search for Item 1.05 because in some cases it's not properly indexed
            'q':'\"Material Cybersecurity Incidents\" OR \"Item 1.05\"',
            'forms': filing_type,
            'startdt': start_date,
            'enddt': end_date,
            'from': str(fetched_results),
            'size': page_size,
            'sort': 'desc'
        }


        headers = {
            'User-Agent': USER_AGENT,
            'Accept': 'application/json'
        }

        response = requests.get(base_url, headers=headers, params=query)
        if response.status_code != 200:
            raise Exception(f"Failed to retrieve data from SEC: {response.status_code}")

        data = response.json()
       
        filings = data['hits']['hits']

        if total_available_results is None:
            total_available_results = data['hits']['total']['value']

        if not filings:
            break

        for filing in filings:
            source = filing['_source']
            display_names = source.get('display_names', [])
            ticker_regex = re.findall(r'\((.*?)\)', display_names[0]) if display_names else None
            ticker = str(ticker_regex[0]).split(",")[0] if ticker_regex and ticker_regex[0][:4] != "CIK " else 'N/A'
            company_name = display_names[0] if display_names else 'N/A'
            ciks = source.get('ciks', [])
            cik = ciks[0] if ciks else 'N/A'
            filing_date = source.get('file_date', 'N/A')
            form_type = source.get('form', 'N/A')
            adsh = source.get('adsh', 'N/A')
            filing_href = f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh.replace('-', '')}/{adsh}-index.htm"
            doc_id = filing.get('_id', None)
            doc_id = doc_id.split(':')[1] if doc_id else 'N/A'
            document_href = f"https://www.sec.gov/Archives/edgar/data/{cik}/{adsh.replace('-', '')}/{doc_id}"
            published_timestamp = get_timestamp_from_index(filing_href)

            results.append({
                'company_name': company_name,
                'cik': cik,
                'filing_date': filing_date,
                'form_type': form_type,
                'filing_href': filing_href,
                'document_href': document_href,
                'ticker': ticker,
                'published_timestamp': published_timestamp,
            })

        fetched_results += len(filings)

        print(f"Fetched {fetched_results}/{total_available_results} filings...", end='\r', flush=True)

        # If the fetched results equal the available total or if the length of filings is less than requested page size, break
        if fetched_results >= total_available_results or len(filings) < page_size:
            break

    print("\nCompleted fetching filings.")  # Ensure a new line is started after the loop

    return results

def get_timestamp_from_index(index_href):
    headers = { 'User-Agent': USER_AGENT }
    response = requests.get(index_href, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to retrieve data from SEC: {response.status_code}")

    match = re.findall('<div class="info">(.*?)</div>', response.text)
    if len(match) >= 2:
        timestamp = match[1]
        return timestamp
    else:
        return None

def get_stock_data(ticker, start_date, end_date):
    return yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), progress=False)

def analyze_impact(ticker, filing_date):
    filing_date = pd.to_datetime(filing_date).normalize()  # Normalize to remove time

    if filing_date.date() == datetime.now().date(): # We won't have Candle data yet.
        print(f"Filing is very recent, skipping Stock analysis for now.")
        return None, None, None

    start_delta = 1
    end_delta = 1

    while (start_delta+end_delta) < 10:
        # Extend the range around the filing date, normalized dates
        date_range = pd.bdate_range(start=filing_date - pd.Timedelta(days=start_delta), end=filing_date + pd.Timedelta(days=end_delta)).normalize()

        stock_data = get_stock_data(ticker, date_range.min(), date_range.max() + pd.Timedelta(days=1))

        if stock_data.empty:
            print(f"No data available for {ticker} between {date_range.min()} and {date_range.max()}")
            start_delta += 1
            end_delta += 1
            continue  # Continue to expand the date range


        # Check if the filing date equals the max date, in which case we want to expand the search
        if filing_date == pd.Timestamp(date_range.max().date()):
            end_delta += 1
            continue

        if filing_date == pd.Timestamp(date_range.min().date()):
            start_delta += 1
            continue

        # Check if the max date is present in the stock_data index
        if pd.Timestamp(date_range.max().date()) not in stock_data.index:
            #print("Max date not in stock data, expanding search...")
            start_delta += 1
            end_delta += 1
            continue

        try:
            # Accessing the stock data by using normalized dates
            before_price = stock_data.loc[date_range.min(), 'Close']
            after_price = stock_data.loc[date_range.max(), 'Close']
            pct_change = (after_price - before_price) / before_price * 100
            print(stock_data) # We print the data here prior to returning
            return before_price, after_price, pct_change
        except KeyError as ex:
            #print("Key error:", ex)
            start_delta += 1
            end_delta += 1
        except Exception as ex:
            #print("Unexpected error:", ex)
            start_delta += 1
            end_delta += 1
            continue

    return None, None, None 



if __name__ == "__main__":
    print("Fetching filings from the SEC with Item 1.05 or Material Cybersecurity Incidents...")
    try:
        # Define the date range for the query
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        # The first filing making use of Item 1.05 for Cybersecurity is from (VFC) on 2023-12-18.
        start_date = "2023-12-01"
        
        filings = get_filings('8-K',start_date, end_date)

        if filings:
            print(f"\r\nPrinting {len(filings)} filings:")
            for filing in filings:
                print(f"Company: {filing['company_name']}, CIK: {filing['cik']}, Date: {filing['filing_date']}, Form Type: {filing['form_type']}")
                print(f"Filing URL: {filing['filing_href']}")
                print(f"Document URL: {filing['document_href']}")
                print(f"Published at: {filing['published_timestamp']} Eastern Time")
                print("")

                if (filing['ticker'] != "N/A"): 
                    # let's only provide dates, no timestamp here to analyze full day candles.
                    before, after, p_change = analyze_impact(filing['ticker'], filing['published_timestamp'].split(" ")[0])
                    if before != None:
                        print("")
                        print(f"Symbol/Ticker: {filing['ticker']}") 
                        print(f"Approximate Price Change (%): {p_change}") 

                print("-" * 80)
        else:
            print("No filings found.")
    except Exception as e:
        print(f"Error: {e}")

