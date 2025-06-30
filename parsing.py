import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

def logger(path):
        def __logger(old_function):
                def new_function(*args, **kwargs):
                        call_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        function_name = old_function.__name__

                        result = old_function(*args, **kwargs)

                        log_entry = (
                                f"{call_time} - Функция: {function_name}\n"
                                f"Аргументы: args={args}, kwargs={kwargs}\n"
                                f"Результат: {result}\n"
                                f"{'-' * 50}\n"
                        )

                        with open(path, 'a', encoding='utf-8') as log_file:
                                log_file.write(log_entry)

                        return result

                return new_function
        return __logger

KEYWORDS = ['дизайн', 'фото', 'web', 'python']

BASE_URL = 'https://habr.com'
url = urljoin(BASE_URL, '/ru/articles/')

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

@logger('habr_parser.log')
def get_page(url, headers):
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text

@logger('habr_parser.log')
def parse_articles(html, keywords):
        soup = BeautifulSoup(html, 'html.parser')
        articles = soup.find_all('article', class_='tm-articles-list__item')
        results = []

        for article in articles:
                title_elem = article.find('h2', class_='tm-title')
                if not title_elem:
                        continue

                title = title_elem.text.strip()
                link_elem = title_elem.find('a', class_='tm-title__link')
                if not link_elem:
                        continue

                link = urljoin(BASE_URL, link_elem['href'])
                time_elem = article.find('time')
                date = time_elem['datetime'] if time_elem else 'No date'

                preview_text = []
                preview_elem = article.find('div', class_='article-formatted-body')
                if preview_elem:
                        preview_text.append(preview_elem.text.strip().lower())

                hubs = article.find_all('a', class_='tm-article-snippet__hubs-item-link')
                preview_text.extend([hub.text.strip().lower() for hub in hubs])
                full_text = ' '.join(preview_text)

                if any(keyword.lower() in full_text for keyword in keywords):
                        results.append(f"{date} – {title} – {link}")

        return results

def main():
        try:

                if os.path.exists('habr_parser.log'):
                        os.remove('habr_parser.log')


                html = get_page(url, headers)


                articles = parse_articles(html, KEYWORDS)


                for article in articles:
                        print(article)

        except requests.exceptions.RequestException as e:
                print(f"Ошибка при загрузке страницы: {e}")
        except Exception as e:
                print(f"Произошла ошибка: {e}")

if __name__ == '__main__':
        main()