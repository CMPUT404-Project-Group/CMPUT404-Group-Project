from src.url_decorator import URLDecorator
import json
import requests
from abc import ABC, abstractmethod

class Node_Interface_Factory():

    def get_interface(Node):
        team = Node.team
        if team == 'TEAM 2':
            return Team_2_Interface
        else:
            return Node_Interface

class Abstract_Node_Interface(ABC):

    def __get_response__(uri):
        response = requests.get(uri)
        data = []
        
        if response.ok:
            try:
                content = json.loads(response.content.decode('utf-8'))
                data = content['data']
            except KeyError:
                data = []
        return data

    @abstractmethod
    def get_authors(node):
        pass

    @abstractmethod
    def get_author_posts(author_id):
        pass

    @abstractmethod
    def get_post(uri):
        pass

    @abstractmethod
    def get_followers(author_id):
        pass

class Node_Interface(Abstract_Node_Interface):

    def get_authors(node):
        uri = URLDecorator.authors_url(str(node))
        return Node_Interface.__get_response__(uri)
    
    def get_author_posts(author_id):
        uri = URLDecorator.author_posts_url(author_id)
        return Node_Interface.__get_response__(uri)
    
    def get_post(uri):
        return Node_Interface.__get_response__(uri)[0]
    
    def get_followers(author_id):
        uri = URLDecorator.author_followers_url(author_id)
        return Node_Interface.__get_response__(uri)

class Team_2_Interface(Abstract_Node_Interface):
    
    def __get_response__(uri):
        return super().__get_response__()
