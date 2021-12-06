from requests.models import InvalidURL, MissingSchema
from src.url_decorator import URLDecorator
import json
import requests
from abc import ABC, abstractmethod

class Node_Interface_Factory():

    def get_interface(Node):
        team = Node.team
        if team == 'TEAM 2':
            return Team_2_Interface
        elif team == 'TEAM 18':
            return Team_18_Interface
        else:
            return Node_Interface

class Abstract_Node_Interface(ABC):

    def __get_response__(node, uri):
        headers = {'Authorization': f'Basic {node.auth_token}'}
        response = requests.get(uri, headers=headers)
        content = {}
        
        if response.ok:
            try:
                content = json.loads(response.content.decode('utf-8'))
            except KeyError:
                pass
        return content

    @abstractmethod
    def get_authors(node):
        pass

    @abstractmethod
    def get_author(node, author_id):
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
        response = Node_Interface.__get_response__(node, uri)
        if 'data' in response:
            return response['data']
        return response
    
    def get_author(node, author_id):
        uri = URLDecorator.author_id_url(node, author_id)
        response = Node_Interface.__get_response__(node, uri)
        if 'data' in response:
            return response['data'][0]
        else:
            return response
    
    def get_author_posts(node, author_id):
        uri = URLDecorator.author_posts_url(author_id)
        response = Node_Interface.__get_response__(node, uri)
        if 'data' in response:
            return response['data']
        else:
            return response

    def get_post(node, uri):
        response = Node_Interface.__get_response__(node, uri)
        if 'data' in response:
            return response['data']
        else:
            return response

    def get_followers(node, author_id):
        uri = URLDecorator.author_followers_url(author_id)
        response = Node_Interface.__get_response__(node, uri)
        if 'data' in response:
            return response['data']
        else:
            return response
        

class Team_2_Interface(Abstract_Node_Interface):

    def get_authors(node):
        uri = URLDecorator.authors_url(str(node))
        return Team_2_Interface.__format_authors__(
            node, Node_Interface.__get_response__(node, uri)['authors'])
    
    def get_author(node, author_id):
        uri = f"{URLDecorator.author_id_url(node, author_id)}/"
        return Team_2_Interface.__format_author__(
            node, Node_Interface.__get_response__(node, uri))
    
    def get_author_posts(node, author_id):
        uri = f"{URLDecorator.author_posts_url(author_id)}/"
        response = Node_Interface.__get_response__(node, uri)
        if 'post' in response:
            return response['post']
        else:
            return response
    
    def get_post(node, uri):
        response = Node_Interface.__get_response__(node, uri)
        if 'post' in response:
            return response['post']
        else:
            return response['data'][0]
    
    def get_followers(node, author_id):
        uri = URLDecorator.author_followers_url(author_id)
        response = Node_Interface.__get_response__(node, uri)
        if 'data' in response:
            return response['data']
        else:
            return response

    def __format_authors__(node, authors):
        for author in authors:
            author = Team_2_Interface.__format_author__(node, author)
        return authors
    
    def __format_author__(node, author):
        author['id'] = f"{node.url}/author/{author.pop('author_id')}"
        return author

class Team_18_Interface(Abstract_Node_Interface):

    def get_authors(node):
        return Node_Interface.get_authors(node)

    def get_author(node, author_id):
         uri = f"{URLDecorator.author_id_url(node, author_id)}"
         return Node_Interface.__get_response__(node, uri)

    def get_author_posts(node, author_id):
        uri = f"{node.url}/author/{URLDecorator.author_posts_url(author_id)}/"
        response = Node_Interface.__get_response__(node, uri)['data']
        if 'data' in response:
            return response['data']
        return response

    def get_post(node, uri):
        uri = f"{uri}/"
        response =  Node_Interface.__get_response__(node, uri)
        if 'data' in response:
            return response['data']
        else:
            return response

    def get_followers(node, author_id):
        return Node_Interface.get_followers(author_id)
