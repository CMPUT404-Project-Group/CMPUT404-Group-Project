from src.url_decorator import URLDecorator
import json
import requests


class Node_Interface():

    def __get_response__(uri):
        response = requests.get(uri)
        return json.loads(response.content.decode('utf-8'))['data']


    def get_authors(node):
        uri = URLDecorator.authors_url(str(node))
        return Node_Interface.__get_response__(uri)
    
    def get_author_posts(author_id):
        uri = URLDecorator.author_posts_url(author_id)
        return Node_Interface.__get_response__(uri)
    
    def get_post(uri):
        return Node_Interface.__get_response__(uri)[0]
    
