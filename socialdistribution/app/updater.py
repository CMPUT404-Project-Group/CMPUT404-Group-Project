from django.core.cache import cache
from django.db.utils import OperationalError
from src.Node import Node_Interface_Factory
from api.models import Node

def update_cached_posts():
    posts = []
    try:
        for node in Node.objects.get_queryset().filter(is_active=True):
                node_interface = Node_Interface_Factory.get_interface(node)
                authors = node_interface.get_authors(node)
                for author in authors:
                    author_posts = node_interface.get_author_posts(node, author['id'])
                    posts.extend(author_posts)
    except OperationalError:
        pass
    cache.set('posts', posts)

def update_cached_authors():
    nodes = Node.objects.get_queryset().filter(is_active=True)
    remote_authors = {}

    try:
        for node in nodes:
            node_interface = Node_Interface_Factory.get_interface(node)
            node_authors = node_interface.get_authors(node)
            remote_authors[node.team] = node_authors
    except OperationalError:
        pass 
    cache.set('authors', remote_authors)