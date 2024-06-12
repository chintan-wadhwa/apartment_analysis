import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

# Base URL for the website with a placeholder for page number
base_url = "https://www.wg-gesucht.de/en/wg-zimmer-in-Duesseldorf.30.0.1.{page}.html"

# Number of pages to scrape
num_pages = 3  # Set the number of pages you want to scrape

# Initialize a list to store the data
data = []

# Function to clean and extract text
def get_text_or_default(element, default='N/A'):
    return element.get_text(strip=True) if element else default

# Function to fetch additional details from the individual listing page
def fetch_listing_details(listing_url):
    try:
        response = requests.get(listing_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract price
        price_div = soup.find('div', class_='col-xs-6 text-center')
        price = get_text_or_default(price_div.find('b', class_='key_fact_value'))
        
        # Extract description
        description_paragraph = soup.find('p')
        description = get_text_or_default(description_paragraph)
        
        return price, description
    except Exception as e:
        print(f"Error fetching details from {listing_url}: {e}")
        return 'N/A', 'N/A'

# Loop through the specified number of pages
for page in range(0, num_pages):
    # Construct the URL for the current page
    url = base_url.format(page=page)
    
    # Make a request to the website
    response = requests.get(url)
    response.raise_for_status()
    
    # Parse the content with BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all listing elements
    listings = soup.find_all('div', class_='wgg_card offer_list_item')
    if not listings:
        print(f"No listings found on page {page}, stopping.")
        break  # Stop if no more listings
    
    # Loop through each listing and extract information
    for listing in listings:
        # Initialize a dictionary to store all available data for the listing
        listing_data = {}

        # Extract the full link
        link = listing.find('a', class_='detailansicht')
        full_link = link['href'] if link else 'N/A'
        full_url = "https://www.wg-gesucht.de" + full_link if full_link != 'N/A' else 'N/A'
        listing_data['full_link'] = full_url

        # Extract the title
        listing_data['title'] = get_text_or_default(listing.find('h3', class_='truncate_title noprint'))
        
        # Extract the details
        details = listing.find('div', class_='col-xs-11')
        listing_data['details'] = get_text_or_default(details)

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
        
        # Fetch additional details from the listing page
        price, description = fetch_listing_details(full_url)
        listing_data['price'] = price
        listing_data['description'] = description
        
        # Append the listing data to the list
        data.append(listing_data)
    
    print(f"Processed page {page}, found {len(listings)} listings.")
    
    # Pause to respect website's request rate
    time.sleep(1)  # Adjust delay as necessary

# Convert the list to a DataFrame
df = pd.DataFrame(data)

# Save the DataFrame to a CSV file
df.to_csv('wg_gesucht_listings.csv', index=False, encoding='utf-8')

# Print the DataFrame
print(df)
