from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin
import requests
import time
import re
import csv


def get_all_categories(link):
    response = requests.get(link)
    html = response.content
    soup = bs(html, "lxml")
    categories = soup.find(class_='side_categories').find_all('a', href=True)
    for categorie in categories:
        categorie_link = urljoin(link, categorie['href'])
        get_product_of_categorie(categorie_link)


def get_product_of_categorie(category_url):
    response = requests.get(category_url)
    html = response.content
    soup = bs(html, "lxml")
    links = soup.find_all('h3')
    print(len(links))
    for link in links:
        link = urljoin(category_url, link.find('a', href=True)['href'])
        # print(link)
        # scrap_product(link)
    next_page = soup.find(class_="next")
    if next_page:
        link = urljoin(category_url, next_page.find('a', href=True)['href'])
        get_product_of_categorie(link)


def scrap_product(product_page_url):
    response = requests.get(product_page_url)
    html = response.content
    soup = bs(html, "lxml")
    content = get_table(soup)
    number_available = soup.find("p", class_="instock availability").get_text().strip()

    # print(int(re.findall(r"\d+", number_available)[0]))
    # print(int(''.join(filter(str.isdigit, number_available))))

    universal_product_code = content['UPC']
    title = soup.find('h1').get_text()
    price_including_tax = content['Price (incl. tax)']
    price_excluding_tax = content['Price (excl. tax)']
    number_available = int(''.join(filter(str.isdigit, number_available)))
    product_description = soup.find("article").find("p", recursive=False).get_text()
    category = soup.select_one("a[href*=category\/books\/]").get_text()
    review_rating = soup.find('p', class_="star-rating")['class'][1]
    image_url = soup.find("img")["src"]

    return (product_page_url, universal_product_code, title, price_including_tax, price_excluding_tax,
            number_available, product_description, category, review_rating, image_url)


def get_table(soup):
    content = {}
    table = soup.find('table')
    rows = table.find_all('tr')
    for row in rows:
        col1 = row.find_all('th')
        col2 = row.find_all('td')
        content[col1[0].text] = col2[0].text
    return content


get_all_categories("http://books.toscrape.com/index.html")

# if __name__ == '__main__':
#     print_hi('PyCharm')
