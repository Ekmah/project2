from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import requests
import time
import re
import csv
import os



def get_all_categories(link):
    t = time.time()
    response = requests.get(link)
    html = response.content
    soup = bs(html, "lxml")
    categories = soup.find(class_='side_categories').find('ul', recursive=False).find('ul').find_all('a', href=True)
    for categorie in categories:
        categorie_link = urljoin(link, categorie['href'])
        get_product_of_categorie(categorie_link, [])
    print(time.time() - t)


def get_product_of_categorie(category_url, products=[]):
    response = requests.get(category_url)
    html = response.content
    soup = bs(html, "lxml")
    links = soup.find_all('h3')
    for link in links:
        link = urljoin(category_url, link.find('a', href=True)['href'])
        products.append(scrap_product(link))

    next_page = soup.find(class_="next")
    if next_page:
        link = urljoin(category_url, next_page.find('a', href=True)['href'])
        print(link)
        get_product_of_categorie(link, products)
    else:
        category = soup.find('h1').get_text().replace(" ", "_")
        fieldnames = ["product_page_url", "universal_product_code", "title", "price_including_tax",
                      "price_excluding_tax", "number_available", "product_description", "category", "review_rating",
                      "image_url"]
        filename = f'CSVs/{category}.csv'
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'a', encoding='UTF8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(products)


def scrap_product(product_page_url):
    response = requests.get(product_page_url)
    html = response.content
    soup = bs(html, "lxml")
    content = get_table(soup)
    number_available = soup.find("p", class_="instock availability").get_text().strip()

    universal_product_code = content['UPC']
    title = soup.find('h1').get_text()
    price_including_tax = content['Price (incl. tax)']
    price_excluding_tax = content['Price (excl. tax)']
    number_available = int(''.join(filter(str.isdigit, number_available)))
    product_description = soup.find("article").find("p", recursive=False)
    if product_description:
        product_description = product_description.get_text()
    else:
        product_description = 'No description'
    category = soup.select_one("a[href*=category\/books\/]").get_text()
    review_rating = soup.find('p', class_="star-rating")['class'][1]

    image_url = urljoin(product_page_url, soup.find("img")["src"])
    # print(image_url)
    img_data = requests.get(image_url).content
    image_name = f'Images/{os.path.basename(image_url)}'
    os.makedirs(os.path.dirname(image_name), exist_ok=True)
    with open(image_name, 'wb') as handler:
        handler.write(img_data)

    return {"product_page_url": product_page_url, "universal_product_code": universal_product_code,
            "title": title, "price_including_tax": price_including_tax, "price_excluding_tax": price_excluding_tax,
            "number_available": number_available, "product_description": product_description, "category": category,
            "review_rating": review_rating, "image_url": image_url}


def get_table(soup):
    content = {}
    table = soup.find('table')
    rows = table.find_all('tr')
    for row in rows:
        col1 = row.find_all('th')
        col2 = row.find_all('td')
        content[col1[0].text] = col2[0].text
    return content


if __name__ == '__main__':
    get_all_categories("http://books.toscrape.com/index.html")
