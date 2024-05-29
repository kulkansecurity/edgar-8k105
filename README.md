# Edgar 8K105 Filings Analysis Tool

This Python script, `edgar-8k105.py`, is designed to fetch and analyze SEC filings specifically related to "Material Cybersecurity Incidents" and "Item 1.05". It employs the SEC's EDGAR database to retrieve these filings and analyze their potential impact on stock prices using Yahoo Finance data.

More on our blog at:

- https://blog.kulkan.com/XXXXXXXXXXXXXXXXXXXXXXXXXX

![Edgar8K105](screencapture.png?raw=true "Edgar-8k105")

## Features

- Fetch 8-K and 8-K/A SEC filings including Item 1.05 and Material Cybersecurity Incidents
- Analyze stock price changes around the date of the filing.
- Utilize Yahoo Finance to obtain historical stock data.
- Provides detailed output, including company names, CIKs, filing dates, and URLs.

## Prerequisites

To run this script, you will need:
- Python 3.x
- Requests: `pip install requests`
- Pandas: `pip install pandas`
- yfinance: `pip install yfinance`

## Usage

1. Modify the `USER_AGENT` variable in the script to include your company name and contact email as per SEC guidelines.
2. Run the script in a Python environment.

## Example

Run the script using:

```bash
python edgar-8k105.py
```

Output will be displayed in the console, showing details about each filing and the analysis of stock price changes, if applicable.

![Edgar8K105](screencapture.png?raw=true "Edgar-8k105")

## Disclaimer

This tool is for educational purposes only. Please ensure compliance with the SEC's EDGAR service terms of use and identify your requests properly.

Additionally, do NOT rely on the output of the script to try and predict price fluctuations in the Market.

## Acknowledgments

Thanks to the Securities and Exchange Commission (SEC) for providing access to the EDGAR data and Yahoo Finance for stock data.

