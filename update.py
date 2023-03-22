import io
import os
import re

from bs4 import BeautifulSoup
import requests

MYANIMELIST_USERNAME = os.getenv('MYANIMELIST_USERNAME')
MYANIMELIST_BASE_URL = 'https://myanimelist.net'


class MyAnimeListError(Exception):
    def __init__(self, status: int) -> None:
        super().__init__(status)


class NotFoundError(Exception):
    def __init__(self) -> None:
        super().__init__()


def request_mal() -> str:
    r = requests.get(f'{MYANIMELIST_BASE_URL}/history/{MYANIMELIST_USERNAME}')
    if r.status_code != 200:
        raise MyAnimeListError(r.status_code)
    return r.text


def scrape_mal(data: str, length: int) -> list:
    soup, media = BeautifulSoup(data, 'html.parser'), []

    entries = soup.find_all('td', attrs={'class': 'borderClass'})

    if entries:
        for entry in entries:
            if len(media) >= length:
                break
            if 'align="right"' not in str(entry):
                title = entry.a.text.replace('\n', '').strip()
                link = f'https://myanimelist.net' + entry.a.get('href').replace('\n', '')
                action = 'chap.' if 'manga.php?' in link else 'ep.'
                activity = entry.strong.text.replace('\n', '')
                media.append(f'[{title}]({link}) {action} {activity}')
    else:
        raise NotFoundError

    return [f'- {x}' for x in media]


def main() -> None:
    history = '\n\n'.join(scrape_mal(data=request_mal(), length=15))
    print(history)

    with io.open('README.md', 'r', encoding='utf8') as f:
        content = f.read()

    c = re.compile(r'<!\-\- MyAnimeList Activity Start \-\->.*<!\-\- MyAnimeList Activity End \-\->', re.DOTALL)
    chunk = f'<!-- MyAnimeList Activity Start -->\n\n{history}\n\n<!-- MyAnimeList Activity End -->'
    content = c.sub(chunk, content)

    with io.open('README.md', 'w', encoding='utf8') as f:
        f.write(content)


if __name__ == '__main__':
    main()
