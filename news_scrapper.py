"""
This function is for scrapping news using bs4. It will be automatically triggered by LLM .

"""

import os
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup as BS
import requests as req

# Define today's date
today_date = datetime.today().strftime('%Y-%m-%d')

# Define the folder where you want to save the CSV file
news_data_folder = 'NewsData'
if not os.path.exists(news_data_folder):
    os.makedirs(news_data_folder)  # Create the folder if it doesn't exist

# Define the CSV file name
file_name = f'{today_date}_latest_news.csv'
file_path = os.path.join(news_data_folder, file_name)

def process_news():
    # List of companies for which we want to fetch the news
    companies = [
        "Amazon", "American Express", "Boeing", "Johnson and Johnson", "Lilly",
        "Procter&Gamble", "Meta", "Netflix", "Tesla", "Pfizer"
    ]

    # Prepare the list to hold the scraped news data
    news_data = []

    # Loop over each company to fetch their news
    for company in companies:
        url = f"https://www.businesstoday.in/topic/{company}"

        # Fetch the webpage content
        webpage = req.get(url)

        # Parse the webpage content with BeautifulSoup
        trav = BS(webpage.content, "html.parser")

        cnt = 0  # Counter to limit news articles per company
        for link in trav.find_all('a'):
            if (str(type(link.string)) == "<class 'bs4.element.NavigableString'>" and len(link.string) > 35):
                link_text = link.string
                link_href = link.get('href')

                # Append the news data
                news_data.append({
                    'Company Name': company,
                    'Data': link_text,
                    'Title': link_text,
                    'Link': link_href
                })
                cnt += 1
                if cnt == 10:  # Limit to 10 articles per company
                    break

    # Create a DataFrame from the news data
    df = pd.DataFrame(news_data)

    # Save the DataFrame to a CSV file in the NewsData folder
    df.to_csv(file_path, index=False)

    print(f'Latest news saved to {file_path}.')

def check_and_process_news():
    # Check if the CSV file already exists in the NewsData folder
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist. Fetching the news...")
        process_news()
    else:
        print(f"File {file_path} already exists.")

# Example usage: Fetch news for a specific company
def get_news(company_name):
    # If the file doesn't exist, fetch news
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist. Fetching the news...")
        process_news()


        # Load the news data from the CSV file
    df = pd.read_csv(file_path)

        # Filter the DataFrame to get news for the specific company
    filtered_df = df[df['Company Name'] == company_name]

        # If no news found for the company, return a message
    if filtered_df.empty:
        return f"No news found for {company_name}."

        # Pick two random rows from the filtered DataFrame
    random_news = filtered_df.sample(n=2)

        # Get the 'Title' and 'Link' columns
    news_titles_and_links = random_news[['Title', 'Link']].values.tolist()

    return news_titles_and_links

def news_helper(company_name):
    # Single case
    if company_name == "Eli Lily":
        company_name = "Lilly"
    return get_news(company_name)
