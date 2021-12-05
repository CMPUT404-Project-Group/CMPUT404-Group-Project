from src.url_decorator import URLDecorator
import json
import requests


class Node_Interface():

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

    def get_authors(node):
        uri = URLDecorator.authors_url(str(node))
<<<<<<< Updated upstream
        return Node_Interface.__get_response__(uri)
    
    def get_author_posts(author_id):
        uri = URLDecorator.author_posts_url(author_id)
        return Node_Interface.__get_response__(uri)
    
    def get_post(uri):
        return Node_Interface.__get_response__(uri)[0]
=======
        response = Node_Interface.__get_response__(node, uri)
        if 'data' in response:
            return response['data']
        else:
            return response
    
    def get_author(node, author_id):
        uri = URLDecorator.author_id_url(node, author_id)
        response = Node_Interface.__get_response__(node, uri)
        if 'data' in response and len(response['data']) > 0:
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
            return response['data'][0]
        else:
            return response
>>>>>>> Stashed changes
    
    def get_followers(author_id):
        uri = URLDecorator.author_followers_url(author_id)
<<<<<<< Updated upstream
        return Node_Interface.__get_response__(author_id)
    
=======
        response = Node_Interface.__get_response__(node, uri)
        if 'data' in response:
            return response['data']
        else:
            return response
    
    def send_follow_request(node, author_id):
        return

class Team_2_Interface(Abstract_Node_Interface):

    def get_authors(node):
        uri = URLDecorator.authors_url(str(node))
        response = Node_Interface.__get_response__(node, uri)
        if 'authors' in response:
            return Team_2_Interface.__format_authors__(
                node, response['authors'])
        else:
            return response
    
    def get_author(node, author_id):
        uri = f"{URLDecorator.author_id_url(node, author_id)}/"
        response = Node_Interface.__get_response__(node, uri)
        if response == []:
            return response
        return Team_2_Interface.__format_author__(
            node, response)
    
    def get_author_posts(node, author_id):
        uri = f"{URLDecorator.author_posts_url(author_id)}/"
        response = Node_Interface.__get_response__(node, uri)
        if 'posts' in response:
            return Node_Interface.__get_response__(node, uri)['posts']
        else:
            return response
    
    def get_post(node, uri):
        response = Node_Interface.__get_response__(node, uri)
        if 'data' in response and len(response['data']) > 0:
            return response['data'][0]
        else:
            return response

    
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
        response = Node_Interface.__get_response__(node, uri)
        if 'data' in response:
            return response['data']
        else:
            return response

    def get_post(node, uri):
        uri = f"{uri}/"
        response = Node_Interface.__get_response__(node, uri)
        if 'data' in response:
            return response['data']
        else:
            return response

    def get_followers(node, author_id):
        return Node_Interface.get_followers(author_id)
>>>>>>> Stashed changes
