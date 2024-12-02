import os
import time
import re
import requests
import json
import pandas as pd
from dotenv import load_dotenv
import os
import requests
load_dotenv()


def standardize_filing_url(url):

    return url.replace('ix?doc=', '')


def get_master_tickers(edgar_headers):
    """
        This function retrieves and processes a list of company tickers (symbols) from the SEC's EDGAR
        API based on specified headers. It filters the list down to a predefined set of companies.


    """
    try:
        tickers_end_point = config['edgar']['tickers_url']
        companyTickers = requests.get(tickers_end_point, headers=edgar_headers)

        # Tickers are in order of market cap; filtering the top 10
        master_tickers_dict = json.loads(companyTickers.content)
        #master_tickers_dict = {key: master_tickers_dict[key] for key in list(master_tickers_dict.keys())[:10]}

        filtered_vals = {}
        master_tickers = []
        tmp_list = ['JNJ','BA','PFE','NFLX','AXP']

        # tmp_list = ['LLY','TSLA','AMZN','META','PG']
        # for key_str in master_tickers_dict.values():
        #     company_name = key_str['title']
        #     ticker = key_str['ticker']
        #     master_tickers.append(ticker)
        #     cik_str = f"{key_str['cik_str']:010d}"  # Format CIK with leading zeros
        #     filtered_vals[company_name] = {'ticker': ticker, 'cik': cik_str}
        filtered_vals = {}
        for key_str in master_tickers_dict.values():
            if len(filtered_vals ) == 10:
                break
            ticker = key_str['ticker']
            if ticker in tmp_list:
                company_name = key_str['title']
                cik_str = f"{key_str['cik_str']:010d}"  # Format CIK with leading zeros
                filtered_vals[company_name] = {'ticker': ticker, 'cik': cik_str}

        return filtered_vals, tuple(tmp_list)
    except Exception as e:
        print(f'Error occurred in get_master_tickers: {e}')



#TODO TO MOVE THESE VARIALBES TO CONFIG.JSON
def get_forms_details(master_tickers):
    """

    This function retrieves recent SEC filings for a list of company tickers,
    specifically focusing on annual (10-K) and quarterly (10-Q) filings between 2022 and 2024.

    """
    try:


        end_point = "https://api.sec-api.io"
        api_key = "1c24b7b0c5a22cb339ea118bd4febb54477c5dcd566481e1053a9da0036b17d2"
        sec_headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }

        payload = {
            "query": f"ticker:({','.join(master_tickers)}) AND (formType:10-K OR formType:10-Q) AND filedAt:[2022-01-01 TO 2024-12-31]",
            "from": "0",
            "size": "50",
            "sort": [{"filedAt": {"order": "desc"}}]
        }

        response = requests.post(end_point, headers=sec_headers, json=payload)
        return response.json()
    except Exception as e:
        print(f"Error occurred in get_forms_details: {e}")




def get_forms_details_new(master_tickers):
    """
    This function retrieves SEC filing details for a list of company tickers, querying for form types 10-K (annual) and 10-Q (quarterly) between 2022 and 2024.
    It processes the tickers in smaller batches to avoid potential API rate limits or request failures.
    :param master_tickers:
    :return:
    """
    try:
        end_point = "https://api.sec-api.io"
        api_key = "1c24b7b0c5a22cb339ea118bd4febb54477c5dcd566481e1053a9da0036b17d2"
        sec_headers = {
            "Authorization": api_key,
            "Content-Type": "application/json"
        }

        all_results = []  # This will hold all results from each batch

        # Process tickers in batches of 3
        for i in range(0, len(master_tickers), 3):
            batch_tickers = master_tickers[i:i+3]  # Get a batch of 3 tickers
            payload = {
                "query": f"ticker:({','.join(batch_tickers)}) AND (formType:10-K AND formType:10-Q) AND filedAt:[2022-01-01 TO 2024-12-31]",
                "from": "0",
                "size": "50",
                "sort": [{"filedAt": {"order": "desc"}}]
            }

            # Send the request for the current batch
            response = requests.post(end_point, headers=sec_headers, json=payload)
            time.sleep(1.5)
            if response.status_code == 200:
                batch_results = response.json().get("filings", [])
                all_results.extend(batch_results)  # Add batch results to the main list
            else:
                print(f"Failed to retrieve data for batch {batch_tickers}. Status code: {response.status_code}")

        # Return all results as a consolidated JSON
        return {"filings": all_results}

    except Exception as e:
        print(f"Error occurred in get_forms_details: {e}")



def download_pdf(df):
    """
    This function downloads all the required pdf files

    """
    api_key = "1c24b7b0c5a22cb339ea118bd4febb54477c5dcd566481e1053a9da0036b17d2"
    PDF_GENERATOR_API = 'https://api.sec-api.io/filing-reader'

    for _, metadata in df.iterrows():
        try:
            ticker = metadata['ticker']
            filing_url = metadata['linkToFilingDetails']
            date = metadata['filedAt'][:10]
            form_type = metadata['formType']

            # Create directory structure
            new_folder = f'./filings/{ticker}'
            os.makedirs(new_folder, exist_ok=True)

            # Generate filename and path
            file_name = f"{date}_{form_type}_{filing_url.split('/')[-1]}.pdf"
            file_path = os.path.join(new_folder, file_name)

            # Construct the API URL and download PDF
            api_url = f"{PDF_GENERATOR_API}?token={api_key}&type=pdf&url={filing_url}"
            response = requests.get(api_url, stream=True)
            response.raise_for_status()  # Raise an error for bad status codes
            time.sleep(1.5)
            # Check content type to ensure it's a PDF
            if response.headers.get('Content-Type') != 'application/pdf':
                print(f"Error: {ticker} - Expected PDF but got {response.headers.get('Content-Type')}")
                continue

            # Write PDF content to file
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)

            print(f"PDF for {ticker} saved at: {file_path}")

        except Exception as e:
            print(f"Exception occured in Downloading the PDF and the exception is {e}")

def rename_files_in_directory(directory_path):

    for root, dirs, files in os.walk(directory_path):
        for file in files:
            # Extract company, form type, and filing date from the filename using regex
            match = re.match(r'(\d{4}-\d{2}-\d{2})_(10-K|10-Q)_(\w+)-(\d{8})\.htm\.pdf', file)

            if match:
                date_str, form_type, company, filing_date = match.groups()

                year = filing_date[:4]

                if form_type == '10-K':

                    new_filename = f"{company.upper()}_{'10K'}_{year}.pdf"
                elif form_type == '10-Q':

                    quarter = (int(filing_date[4:6]) - 1) // 3 + 1  # Q1, Q2, Q3, Q4
                    new_filename = f"{company.upper()}_{'10Q'}_{year}_Q{quarter}.pdf"


                old_file_path = os.path.join(root, file)
                new_file_path = os.path.join(root, new_filename)

                os.rename(old_file_path, new_file_path)
                print(f"Renamed: {file} -> {new_filename}")
            else:
                print(f"Filename format not recognized: {file}")
if __name__ == "__main__":

    with open("config.json", "r") as config_file:
        config = json.load(config_file)

    edgar_headers = config['edgar']['headers']
    # rename_files_in_directory("./filings")

    master_tickers_data,master_tickers_tuple = get_master_tickers(edgar_headers)
    master_data_upload = get_forms_details_new(master_tickers=master_tickers_tuple)
    master_data_upload = master_data_upload['filings']
    df = pd.DataFrame(master_data_upload)
    df = df[['ticker','linkToFilingDetails','filedAt' ,'formType', 'cik', 'companyName', 'linkToHtml']]
    df['linkToFilingDetails'] = df['linkToFilingDetails'].apply(standardize_filing_url)

    download_pdf(df)
