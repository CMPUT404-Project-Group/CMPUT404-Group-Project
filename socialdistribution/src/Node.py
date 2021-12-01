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

    def __get_response__(node, uri):
        headers = {'Authorization': f'Token {node.auth_token}'}
        response = requests.get(uri, headers=headers)
        content = []
        
        if response.ok:
            try:
                content = json.loads(response.content.decode('utf-8'))
            except KeyError:
                pass
            finally:
                return content

    @abstractmethod
    def get_authors(node):
        pass

    @abstractmethod
    def get_author_posts(node, author_id):
        pass

    @abstractmethod
    def get_post(node, uri):
        pass

    @abstractmethod
    def get_followers(node, author_id):
        pass

class Node_Interface(Abstract_Node_Interface):

    def get_authors(node):
        uri = URLDecorator.authors_url(str(node))
        return Node_Interface.__get_response__(node, uri)['data']
    
    def get_author_posts(node, author_id):
        uri = URLDecorator.author_posts_url(author_id)
        return Node_Interface.__get_response__(node, uri)['data']
    
    def get_post(node, uri):
        return Node_Interface.__get_response__(node, uri)['data'][0]
    
    def get_followers(node, author_id):
        uri = URLDecorator.author_followers_url(author_id)
        return Node_Interface.__get_response__(node, uri)['data']

class Team_2_Interface(Abstract_Node_Interface):

    def get_authors(node):
        uri = URLDecorator.authors_url(str(node))
        return Team_2_Interface.__format_authors__(
            node, Node_Interface.__get_response__(node, uri)['authors'])
    
    def get_author_posts(node, author_id):
        uri = f"{URLDecorator.author_posts_url(author_id)}/"
        return Node_Interface.__get_response__(node, uri)['posts']
    
    def get_post(node, uri):
        return Node_Interface.__get_response__(node, uri)['data'][0]
    
    def get_followers(node, author_id):
        uri = URLDecorator.author_followers_url(author_id)
        return Node_Interface.__get_response__(node, uri)['data']

    def __format_authors__(node, authors):
        for author in authors:
            author['id'] = f"{node.url}/author/{author.pop('author_id')}"
        return authors