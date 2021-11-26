
class URLDecorator():

    def author_id_url(url, author_id):
        return f"{url}/author/{author_id}"
    
    def post_id_url(url, author_id, post_id):
        url_pointing_to_author = URLDecorator.author_id_url(url, author_id)
        return f"{url_pointing_to_author}/post/{post_id}"

    def comment_id_url(url, author_id, post_id, comment_id):
        url_pointing_to_post = URLDecorator.post_id_url(url, author_id, post_id)
        return f"{url_pointing_to_post}/comment/{comment_id}"
    
    def authors_url(url):
        return f"{url}/authors"
    
    def author_inbox_url(url, author_id):
        url_pointing_to_author = URLDecorator.author_id_url(url, author_id)
        return f"{url_pointing_to_author}/inbox"
    
    def posts_id_url(url, author_id):
        url_pointing_to_author = URLDecorator.author_id_url(url, author_id)
        return f"{url_pointing_to_author}/posts"
    
    def author_liked_url(url, author_id):
        url_pointing_to_author = URLDecorator.author_id_url(url, author_id)
        return f"{url_pointing_to_author}/liked"
    
    def author_followers_url(url, author_id):
        url_pointing_to_author = URLDecorator.author_id_url(url, author_id)
        return f"{url_pointing_to_author}/followers"
    
    def author_follower_url(url, author_id, follower_id):
        url_pointing_to_author = URLDecorator.author_id_url(url, author_id)
        return f"{url_pointing_to_author}/follower/{follower_id}"
    
    def post_comments_url(url, author_id, post_id):
        url_pointing_to_post = URLDecorator.post_id_url(url, author_id, post_id)
        return f"{url_pointing_to_post}/comments"

    def post_likes_url(url, author_id, post_id):
        url_pointing_to_post = URLDecorator.post_id_url(url, author_id, post_id)
        return f"{url_pointing_to_post}/likes"
    
    def comment_likes_url(url, author_id, post_id, comment_id):
        url_pointing_to_comment = URLDecorator.comment_id_url(url, author_id, post_id, comment_id)
        return f"{url_pointing_to_comment}/likes"
    
    
    
    
