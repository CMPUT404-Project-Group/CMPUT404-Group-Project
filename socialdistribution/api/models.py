from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.manager import BaseManager
from dotenv import load_dotenv
import os
from uuid import uuid4



load_dotenv()
HOST_API_URL = os.getenv("HOST_API_URL")

class UserManager(BaseUserManager):
    def create_user(self, email, username, github=None, password=None, type="author"):
        """
        Creates and saves a User.
        """
        if not email:
            raise ValueError('Users must have an email address')

        uuid = uuid4()
        host = HOST_API_URL

        if github:
            github_url = 'http://github.com/%s' % github
        else:
            github_url = None
            
        user = self.model(
            type=type,
            id=host+str(uuid),
            host=host,
            username=username, #displayName
            url=host+str(uuid),
            github=github_url,            
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, github=None, password=None, type="server-admin"):
        """
        Creates and saves a superuser.
        """
        user = self.create_user(
            email,
            username=username,
            github=github,
            password=password,
            type=type,
        )
        user.is_active = True
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    # required fields to be exposed by API
    type = models.CharField(max_length=255, unique=False, null=False, blank=False, default="author")
    id = models.CharField(auto_created=True, max_length=255, unique=True, null=False, blank=False, primary_key=True)
    host = models.URLField(max_length=255, unique=False, null=False, blank=False, default=HOST_API_URL)
    # this should be returned from the API as displayName; keep it as username in db for default django stuff
    username = models.CharField(max_length=255, unique=True)
    url = models.CharField(max_length=255, unique=False, blank=False, null=False, default=HOST_API_URL)
    github = models.CharField(max_length=50, unique=True, blank=True, null=True)

    # user metadata
    email = models.EmailField(max_length=255, unique=True, verbose_name="email address")
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True #temp
    
    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

class PostBuilder():

    def __init__(self):
        self.id = uuid4()
        post_url = f"{HOST_API_URL}posts/{self.id}"

        self.type = 'post'
        self.source = post_url
        self.origin = post_url
        self.count = 0
        self.comment_page = f"{post_url}/comments"

        self.title = None
        self.description = None
        self.content_type = None
        self.text_content = None
        self.image_content = None
        self.author = None
        self.categories = None
        self.size = None
        self.visibility = None
        self.unlisted = None
    
    def set_post_content(self, title, categories, text_content=None, image_content=None):
        self.title = title
        self.categories = categories
        self.text_content = text_content
        self.image_content = image_content
    
    #TODO: Description is not very descriptive
    def set_post_metadata(self, author, visibility, unlisted):
        assert self.title, "set_post_content must be called before set_post_metadata"

        self.author = author
        self.visibility = visibility
        self.unlisted = unlisted

        self.__set_description__()
        self.__set_content_type__()
        self.__set_size__()
    
    def get_post(self):
        return Post(
            type=self.type,
            title=self.title,
            id=self.id,
            source=self.source,
            origin=self.origin,
            description=self.description,
            content_type=self.content_type,
            text_content=self.text_content,
            image_content=self.image_content,
            author=self.author,
            categories=self.categories,
            count=self.count,
            size=self.size,
            comment_page=self.comment_page,
            visibility=self.visibility,
            unlisted=self.unlisted
        )
    
    def __set_description__(self):
        self.description = f"{self.title}"
        if self.text_content:
            self.description += f": {self.text_content[0:50]}..."
    
    #TODO: Content type just defaults to plain text at the moment
    def __set_content_type__(self):
        self.content_type = Post.ContentType.PLAIN
    
    #TODO: Figure out size of post dynamically (possibly iterate through attributes adding size)
    def __set_size__(self):
        self.size = 0


     

class PostManager(models.Manager):

    def create_post(self, author, categories, image_content, text_content, title, visibility, unlisted):
        post_builder = PostBuilder()
        post_builder.set_post_content(title, categories, text_content, image_content)
        post_builder.set_post_metadata(author, visibility, unlisted)
        
        post = post_builder.get_post()
        post.save(using=self._db)
        return post

#TODO: Specify uploadto field for image_content to post_imgs within project root
#TODO: Upon adding comment model add comment as foreign key
class Post(models.Model):

    class Visibility(models.TextChoices):
        PUBLIC = "public"
    
    class ContentType(models.TextChoices):
        MARKDOWN = "text/markdown"
        PLAIN = "text/plain"
        APPLICATION = "application/base64"
        PNG = "image/png;base64"
        JPG = "image/jpg;base64"

    type = models.CharField(max_length=255, unique=False, null=False, blank=False, default="post")
    title = models.CharField(max_length=255, unique=False, null=False, blank=False)
    id = models.CharField(max_length=255, unique=True, null=False, primary_key=True)
    source = models.URLField(
        max_length=255, unique=False, null=False, blank=False)
    origin = models.URLField(
        max_length=255, unique=False, null=False, blank=False)
    description = models.CharField(max_length=255, unique=False, null=False, blank=False)
    content_type = models.CharField(max_length=255, choices=ContentType.choices)
    text_content = models.TextField(unique=False, blank=True)
    image_content = models.ImageField(unique=False, blank=True)
    author = models.ForeignKey(
        "User",
        on_delete=models.CASCADE
        )
    categories = models.TextField(unique=False, blank=True, null=False)
    count = models.IntegerField(unique=False, null=False, blank=False, default=0)
    size = models.IntegerField(unique=False, null=False, blank=False)
    comment_page = models.CharField(max_length=255, unique=False, null=False, blank=False)
    #comments could potentially be done at serialization to avoid data duplication 
    #(get all comments which have this post_id within their comment_id)
    #If we do this size may also have to be done at serialization although I think this may be easier anyways
    published = models.DateTimeField(unique=False, blank=False, null=False, auto_now_add=True)
    visibility = models.CharField(
        max_length=255, choices=Visibility.choices, unique=False, blank=False, null=False, default=Visibility.PUBLIC)
    unlisted = models.BooleanField(unique=False, blank=False, null=False, default=False)

    objects = PostManager()

    def __str__(self):
        return f"{self.author}, {self.title}, {self.text_content}, {self.image_content}, {self.categories}"

class Comment(models.Model):
    type = models.CharField(max_length=255, unique=False, null=False, blank=False)
    author = models.ForeignKey("User", on_delete=models.CASCADE)
    comment = models.TextField(unique=False, blank=False, null=False)
    content_type = models.CharField(max_length=255, unique=False, null=False, blank=False)
    published = models.DateTimeField(unique=False, blank=False, null=False, auto_now_add=True)
    id = models.CharField(max_length=255, unique=False, null=False, blank=False, primary_key=True)

    


