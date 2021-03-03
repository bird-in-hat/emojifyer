import itertools
import re
from typing import Iterator

import requests                   # Convenient work with http requests
from bs4 import BeautifulSoup     # Widely used html parsing lib
from bs4.element import Comment, PageElement
from flask import Flask, request  # Lighweight framework, easy deploy for SPA

app = Flask(__name__)


def is_elem_visible(page_element: PageElement) -> bool:
    """Checks if bs4 element is visible text
    """
    visible_elems = ['style', 'script', 'head', 'title', 'meta', '[document]']
    if page_element.parent.name in visible_elems:
        return False
    if isinstance(page_element, Comment):
        return False
    return True


def emoji_generator() -> Iterator[str]:
    """Infinitely returns next emoji in emoji_list
    """
    emoji_list = ['\U0001F600', '\U0001F642', '\U0001F61D', '\U0001F92B']
    for emoji in itertools.cycle(emoji_list):
        yield emoji


@app.route('/emojify/')
def emojify():
    url = request.args.get('url', None)
    if not url:
        return ('Provide <url> param as request arg, '
                'like /?url=https://example.com'), 400

    try:
        with requests.get(url) as response:
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
    except Exception as err:
        print('Url exception', repr(err))
        return 'Url exception', 400

    emoji_iter = emoji_generator()
    try:
        visible_elems = filter(
            lambda elem: len(elem) > 5 and is_elem_visible(elem),
            soup.findAll(text=True))

        for elem in visible_elems:
            if not elem.string:
                continue

            replace_to = '___emoji___'
            emoji_str = re.sub(r'(\b\w{6}\b)', f'\\1{replace_to}', elem.string)
            while replace_to in emoji_str:
                emoji_str = emoji_str.replace(replace_to, next(emoji_iter), 1)

            elem.string.replace_with(emoji_str)
        return str(soup)
    except Exception as err:
        print('Replacement error', repr(err))
        return 'Error while replacing', 400


@app.route('/')
def home():
    return 'Using: /emojify/?url=<url>', 200
