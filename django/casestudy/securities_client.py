import json
import os
import requests

api_key = os.environ.get('SECURITIES_API_KEY')
base_url = 'https://app.albert.com/casestudy/stock/{}'
get_tickers_url = 'tickers/'
get_prices_url = 'prices/?tickers={}'

def get_tickers():
    url = base_url.format(get_tickers_url)
    response = requests.get(url, headers={'Albert-Case-Study-API-Key': api_key})
    json_response = json.loads(response.text)
    return json_response

def get_prices(tickers):
    url = base_url.format(get_prices_url.format(','.join(tickers)))
    response = requests.get(url, headers={'Albert-Case-Study-API-Key': api_key})
    json_response = json.loads(response.text)
    return json_response