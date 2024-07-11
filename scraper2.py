import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random

# Base URL for the website with placeholder for page number
base_url = "https://www.wg-gesucht.de/en/wg-zimmer-in-Duesseldorf.30.0.1.{page}.html"

# Initialize a list to store the data
data = []

# Function to clean and extract text
def get_text_or_default(element, default='N/A'):
    return element.get_text(strip=True) if element else default

# Function to extract description from the listing page
def extract_description(listing_url):
    response = requests.get(listing_url)
    response.raise_for_status()
    response.encoding = 'utf-8'  # Ensure proper encoding
    soup = BeautifulSoup(response.content, 'html.parser')

    description_parts = []

    for section in soup.find_all('div', class_='section_panel_tab'):
        section_id = section['data-text']
        description_div = soup.find('div', id=section_id[1:])
        if description_div:
            description_parts.append(get_text_or_default(description_div.find('p')))
    
    return ' '.join(description_parts)

# Page counter
page = 0

while True:
    # Construct the URL for the current page
    url = base_url.format(page=page)
    
    # Make a request to the website
    response = requests.get(url)
    response.raise_for_status()
    response.encoding = 'utf-8'  # Ensure proper encoding
    
    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all listing elements
    listings = soup.find_all('div', class_='wgg_card offer_list_item')
    if not listings:
        print(f"No listings found on page {page}, stopping.")
        break  # Stop if no more listings
    
    # Loop through each listing and extract all information
    for listing in listings:
        # Initialize a dictionary to store all available data for the listing
        listing_data = {}

        # Extract the full link
        link = listing.find('a', class_='detailansicht')
        full_link = link['href'] if link else 'N/A'
        full_link = "https://www.wg-gesucht.de" + full_link if full_link != 'N/A' else 'N/A'
        listing_data['full_link'] = full_link
        
        # Extract the title
        listing_data['title'] = get_text_or_default(listing.find('h3', class_='truncate_title noprint'))
        
        # Extract the details
        details = listing.find('div', class_='col-xs-11')
        listing_data['details'] = get_text_or_default(details)
        
        # Extract the price
        price_div = listing.find('div', class_='col-xs-3')
        price = price_div.find('b') if price_div else None
        listing_data['price'] = get_text_or_default(price)
        
        # Extract the availability
        availability = listing.find('div', class_='col-xs-5 text-center')
        listing_data['availability'] = get_text_or_default(availability)
        
        # Extract the size
        size_div = listing.find('div', class_='col-xs-3 text-right')
        size = size_div.find('b') if size_div else None
        listing_data['size'] = get_text_or_default(size)
        
        # Extract the landlord name
        landlord = listing.find('span', class_='ml5')
        listing_data['landlord'] = get_text_or_default(landlord)
        
        # Extract the online status
        online_status = 'N/A'
        for span in listing.find_all('span'):
            if 'color' in span.attrs.get('style', ''):
                online_status = span.get_text(strip=True)
                break
        listing_data['online_status'] = online_status
        
        # Extract the description from the full link page
        if full_link != 'N/A':
            description = extract_description(full_link)
            listing_data['description'] = description
        
        # Append the listing data to the list
        data.append(listing_data)
    
    print(f"Processed page {page}, found {len(listings)} listings.")
    
    # Pause to respect website's request rate
    delay = random.uniform(2, 7)
    time.sleep(delay)  # Adjust delay as necessary
    
    # Increment the page counter
    page += 1

# Convert the list to a DataFrame
df = pd.DataFrame(data)

# Save the DataFrame to a CSV file with correct encoding
df.to_csv('duesseldorf_listings_description.csv', index=False, encoding='utf-8')

# Print the DataFrame
print(df)