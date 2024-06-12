import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def scrape_wg_gesucht(pages=1):
    base_url = "https://www.wg-gesucht.de/en/wg-zimmer-in-Duesseldorf.30.0.1.{}.html"
    results = []

    for page in range(pages):
        url = base_url.format(page)
        response = requests.get(url)
        
        if response.status_code != 200:
            print(f"Failed to retrieve page {page}: Status Code {response.status_code}")
            continue
        
        soup = BeautifulSoup(response.content, 'html.parser')
        listings = soup.find_all('div', class_='wgg_card offer_list_item')
        
        print(f"Found {len(listings)} listings on page {page}")
        
        for listing in listings:
            try:
                title_tag = listing.find('h3', class_='truncate_title')
                title = title_tag.get_text(strip=True) if title_tag else "N/A"
                
                link_tag = title_tag.find('a') if title_tag else None
                link = link_tag['href'] if link_tag else "N/A"
                link = "https://www.wg-gesucht.de" + link if link and not link.startswith('http') else link
                
                details_tag = listing.find('span')
                details = details_tag.get_text(strip=True) if details_tag else "N/A"
                
                price_tag = listing.find('b', string=re.compile("€"))
                price = price_tag.get_text(strip=True) if price_tag else "N/A"
                
                availability_tag = listing.find_all('div', class_='col-xs-5 text-center')
                availability = availability_tag[0].get_text(strip=True) if availability_tag else "N/A"
                
                size_tag = listing.find('div', class_='col-xs-3 text-right')
                size = size_tag.get_text(strip=True) if size_tag else "N/A"
                
                landlord_tag = listing.find('span', class_='ml5')
                landlord = landlord_tag.get_text(strip=True) if landlord_tag else "N/A"
                
                online_status_tag = listing.find('span', style="color: #218700;")
                online_status = online_status_tag.get_text(strip=True) if online_status_tag else "N/A"
                
                description_tag = listing.find('div', class_='wordWrap')
                description = description_tag.get_text(strip=True) if description_tag else "N/A"

                results.append({
                    'Title': title,
                    'Link': link,
                    'Details': details,
                    'Price': price,
                    'Availability': availability,
                    'Size': size,
                    'Landlord': landlord,
                    'Online Status': online_status,
                    'Description': description
                })
                
            except Exception as e:
                print(f"Error processing listing: {e}")

    return pd.DataFrame(results)

if __name__ == "__main__":
    pages = int(input("Enter the number of pages to scrape: "))
    df = scrape_wg_gesucht(pages)
    if not df.empty:
        df.to_csv('wg_gesucht_data.csv', index=False)
        print("Data saved to wg_gesucht_data.csv")
    else:
        print("No data found.")