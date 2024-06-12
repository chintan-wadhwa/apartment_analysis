import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

def scrape_wg_gesucht_selenium(pages=1):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)

    base_url = "https://www.wg-gesucht.de/en/wg-zimmer-in-Duesseldorf.30.0.1.{}.html"
    results = []

    for page in range(pages):
        url = base_url.format(page)
        driver.get(url)
        
        # Wait for the content to load
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[id^='liste-details-ad-']"))
            )
        except Exception as e:
            print(f"Timeout on page {page}: {e}")
            with open(f'page_{page}_source.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            continue

        soup = BeautifulSoup(driver.page_source, 'html.parser')
        listings = soup.select("div[id^='liste-details-ad-']")

        print(f"Found {len(listings)} listings on page {page}")

        for listing in listings:
            try:
                # Title and Link
                title_tag = listing.find('h3', class_='truncate_title')
                title = title_tag.get_text(strip=True) if title_tag else "N/A"
                link_tag = title_tag.find('a') if title_tag else None
                link = link_tag['href'] if link_tag else "N/A"
                link = "https://www.wg-gesucht.de" + link if link and not link.startswith('http') else link
                
                # Details
                details_tag = listing.find('span')
                details = details_tag.get_text(strip=True) if details_tag else "N/A"
                
                # Price
                price_tag = listing.find('b')
                price = price_tag.get_text(strip=True) if price_tag else "N/A"
                
                # Availability
                availability_tag = listing.select_one('div.row.noprint.middle > div.col-xs-5.text-center')
                availability = availability_tag.get_text(strip=True) if availability_tag else "N/A"
                
                # Size
                size_tag = listing.select_one('div.row.noprint.middle > div.col-xs-3.text-right')
                size = size_tag.get_text(strip=True) if size_tag else "N/A"
                
                # Landlord
                landlord_tag = listing.select_one('div.row.noprint.bottom span.ml5')
                landlord = landlord_tag.get_text(strip=True) if landlord_tag else "N/A"
                
                # Online Status
                online_status_tag = listing.select_one('span[style*="color: #218700;"]')
                online_status = online_status_tag.get_text(strip=True) if online_status_tag else "N/A"
                
                # Description
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

    driver.quit()
    return pd.DataFrame(results)

if __name__ == "__main__":
    pages = int(input("Enter the number of pages to scrape: "))
    df = scrape_wg_gesucht_selenium(pages)
    if not df.empty:
        df.to_csv('wg_gesucht_data.csv', index=False)
        print("Data saved to wg_gesucht_data.csv")
    else:
        print("No data found.")
