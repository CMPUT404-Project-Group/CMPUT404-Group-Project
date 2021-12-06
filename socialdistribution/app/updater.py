from django.core.cache import cache
from django.db.utils import OperationalError
from src.Node import Node_Interface_Factory
from api.models import Node
from apscheduler.schedulers.background import BackgroundScheduler

def start():
    scheduler = BackgroundScheduler({'apscheduler.timezone': 'UTC'})
    scheduler.add_job(update_cached_authors, 'interval', minutes=1)
    scheduler.add_job(update_cached_posts, 'interval', minutes=1)
    scheduler.start()

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
    cache.set('posts', posts, 100)

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
    cache.set('authors', remote_authors, 100)