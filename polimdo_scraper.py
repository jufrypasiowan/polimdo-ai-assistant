import requests
from bs4 import BeautifulSoup
import re

def search_polimdo_data(query: str, max_results: int = 3) -> list:
    search_url = f"https://www.polimdo.ac.id/?s={requests.utils.quote(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    results = []
    try:
        response = requests.get(search_url, headers=headers, timeout=8)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            articles = soup.find_all("article")
            
            for article in articles[:max_results]:
                title_elem = article.find(["h2", "h3", "h1"])
                link_elem = article.find("a")
                excerpt_elem = article.find(["div", "p"], class_=re.compile("excerpt|entry-summary|entry-content", re.I))
                
                title = title_elem.get_text(strip=True) if title_elem else "Informasi Polimdo"
                link = link_elem["href"] if link_elem and "href" in link_elem.attrs else "https://www.polimdo.ac.id"
                snippet = excerpt_elem.get_text(strip=True) if excerpt_elem else "Detail informasi dapat dilihat pada tautan terlampir."
                
                results.append({
                    "title": title,
                    "link": link,
                    "snippet": snippet
                })
    except Exception as e:
        print(f"Error fetching Polimdo data: {e}")
        
    return results
