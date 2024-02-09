
import requests
from bs4 import BeautifulSoup

# Use a single request to get the data
url = 'https://www.binance.com/en/price/bitcoin'
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Assuming these selectors are correct and pointing to static parts of the page
    # (which might not be the case for dynamic content)
    price_selector = '.css-1267ixm > div.css-1bwgsh3'
    rate_selector = '.css-1267ixm > div.css-12i542z'
    
    price_element = soup.select_one(price_selector)
    rate_element = soup.select_one(rate_selector)
    
    if price_element and rate_element:
        print(f'Bitcoin Price: {price_element.text}')
        print(rate_element.text)
    else:
        print('Could not find the Bitcoin price or rate on the page.')
else:
    print('Failed to retrieve the webpage')