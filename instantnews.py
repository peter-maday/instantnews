#!/usr/bin/env python

import os
import sys
import argparse
import requests
import textwrap

# Global constants
API_URL = "https://newsapi.org/register"
BASE_URL = "https://newsapi.org/v1/articles"
SOURCE_URL = "https://newsapi.org/v1/sources"
VALID = ['y', 'n']
NEWS_CATEGORIES = [
    'business', 'entertainment', 'gaming', 'general', 'music', 'politics',
    'science-and-nature', 'sport', 'technology'
]
WRAP_LINE_WIDTH = 100

# Global variables
news_codes = []
api_key = ""


def test_network_connection():
    """Test network connection"""
    try:
        response = requests.get("https://newsapi.org/")
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        print(
            "There was issue connecting to the server. Please check your network connection."
        )
        sys.exit(1)
    except requests.exceptions.RequestException as exception:
        print(exception)
        sys.exit(1)


def fetch_all_news_codes():
    """Fetch news codes from all sources"""
    response = requests.get(SOURCE_URL)
    json = response.json()
    global news_codes
    for source in json['sources']:
        news_codes.append(source['id'])


def load_config_key():
    """Load api key on a global api key and validate it"""
    try:
        global api_key
        api_key = os.environ['IN_API_KEY']
        if len(api_key) == 32:
            try:
                int(api_key, 16)
            except ValueError:
                print("Invalid API key")
    except KeyError:
        print('No API Token detected. '
              'Please visit {0} and get an API Token, '
              'which will be used by instantnews '
              'to get access to the data.'.format(API_URL))
        sys.exit(1)


def check_choice(choice):
    """Validate choice for yes or no"""
    return choice == 'y' or choice == 'n'


def show_sources_category(category):
    """Display news codes by category"""
    if category not in NEWS_CATEGORIES:
        print("Invalid category")
        sys.exit(1)

    url = "?category={category_type}"
    response = requests.get((SOURCE_URL + url).format(category_type=category))
    json = response.json()
    for source in json['sources']:
        print(u"{0}: <{1}> {2}".format("News Code", source['id'],
                                       source['name']))


def show_sources_all():
    """Display all news codes"""
    response = requests.get(SOURCE_URL)
    json = response.json()
    for source in json['sources']:
        print(u"{0}: <{1}> {2}".format("News Code", source['id'],
                                       source['name']))


def show_categories():
    """Display all news categories"""
    for category in NEWS_CATEGORIES:
        print(category)


def show_news(code, BASE_URL):
    """Display news with respect to news id"""
    url = "?source={news_id}&apiKey="
    response = requests.get((BASE_URL + url + api_key).format(news_id=code))
    json = response.json()

    for idx, article in enumerate(json['articles']):

        title = article['title']
        url = article['url']

        if article['description']:
            description = "\n".join(
                textwrap.wrap(description, width=WRAP_LINE_WIDTH))
        else:
            description = "N/A"

        print('')
        print('--------------------------------------------')
        print('')
        print(title)
        print('')
        print('{0}: {1}'.format("Summary", description))
        print('')
        print(f'URL: {url}')


def parser():
    """Parse arguments and call appropriate functions"""
    fetch_all_news_codes()
    load_config_key()

    if not sys.argv[1:]:
        print("Arguments needed. Use argument --help/-h for more information.")
    else:
        parser = argparse.ArgumentParser()
        parser.add_argument("--show_all",
                            "-sa",
                            action="store_true",
                            help="Shows all available news channel codes.")
        parser.add_argument("--categories",
                            "-c",
                            action="store_true",
                            help="Shows all available news categories.")
        parser.add_argument(
            "--show",
            "-s",
            action="store",
            help="Shows all news channel codes for a specified category.")
        parser.add_argument("--news",
                            "-n",
                            type=str,
                            help="Shows news articles "
                            "for a specified news channel code.")
        args = parser.parse_args()

        if args.show_all:
            show_sources_all()
        elif args.categories:
            show_categories()
        elif args.show:
            show_sources_category(args.show)
        elif args.news:
            if args.news in news_codes:
                show_news(args.news, BASE_URL)
            else:
                print("Invalid news code.")
                sys.exit(1)


def main():
    """Test network connection, then parse arguments"""
    test_network_connection()
    parser()


if __name__ == "__main__":
    main()
