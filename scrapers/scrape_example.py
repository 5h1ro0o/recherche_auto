import httpx
from bs4 import BeautifulSoup

def fetch_listings():
    url = "https://example.com/search?q=vw+golf"
    resp = httpx.get(url, timeout=20)
    soup = BeautifulSoup(resp.text, "html.parser")
    # parser simple : à adapter selon site
    items = []
    for el in soup.select(".listing"):
        items.append({
            "id": el.get("data-id"),
            "title": el.select_one(".title").text.strip(),
            "price": int(el.select_one(".price").text.replace('€','').replace(' ',''))
        })
    return items

if __name__ == "__main__":
    print(fetch_listings())
