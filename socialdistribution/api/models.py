from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager
import os
from uuid import uuid4
from dotenv import load_dotenv

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

#TODO: Change ID to be in line with spec
#TODO: Specify uploadto field for image_content to post_imgs within project root
#TODO: Add default to comment_page once ID's are UUID such that comment_page = HOST/author/author_UUID/post/post_UUID/comments
#TODO: Upon adding comment functionality finish comment model
#TODO: Add category to model
#TODO: Figure out page size
class Post(models.Model):
    # class Meta:
    #     constraints = [
    #         models.CheckConstraint(
    #             check=models.Q(text_content__isnull=True) | models.Q(image_content__isnull=True),
    #             name="Posts can have text or an image but not both"
    #         ),
    #         models.CheckConstraint(
    #             check=models.Q(text_content__isnull=False) | models.Q(image_content__isnull=False),
    #             name="Posts must have text or image content"
    #         )
    #     ]

    class Visibility(models.IntegerChoices):
        PUBLIC = 0
    
    class ContentType(models.TextChoices):
        MARKDOWN = "text/markdown"
        PLAIN = "text/plain"
        APPLICATION = "application/base64"
        PNG = "image/png;base64"
        JPG = "image/jpg;base64"

    type = models.CharField(max_length=255, unique=False, null=False, blank=False, default="post")
    title = models.CharField(max_length=255, unique=False, null=False, blank=False)
    id = models.CharField(auto_created=True, max_length=255, unique=True, null=False, blank=False, primary_key=True)
    source = models.URLField(
        max_length=255, unique=False, null=False, blank=False, default=f"{HOST_API_URL}/posts/{id}")
    origin = models.URLField(
        max_length=255, unique=False, null=False, blank=False, default=f"{HOST_API_URL}/posts/{id}")
    description = models.URLField(max_length=255, unique=False, null=False, blank=False)
    content_type = models.CharField(max_length=255, choices=ContentType.choices)
    text_content = models.TextField(blank=True)
    image_content = models.ImageField(blank=True)
    author = models.ForeignKey(
        "User",
        on_delete=models.CASCADE
        )
    #categories
    count = models.IntegerField(unique=False, null=False, blank=False, default=0)
    size = models.IntegerField(unique=False, null=False, blank=False)
    #comment_page = models.URLField(max_length=255, unique=False, null=False, blank=False)
    #comments
    published = models.DateTimeField(editable=False, auto_now_add=True)
    visibility = models.IntegerField(choices=Visibility.choices, default=Visibility.PUBLIC)
    unlisted = models.BooleanField(default=False)

    def clean(self):
        self.clean_content_type()
        self.clean_description()
        self.clean_size()
    
    def clean_content_type(self):
        if self.text_content:
            self.content_type = self.ContentType.PLAIN
        elif self.image_content:
            self.clean_content_type_image()

    def clean_content_type_image(self):
        file_name = self.image_content.filename
        file_extension = file_name[:file_name.rfind('.')]

        if file_extension == 'png':
            self.content_type = self.ContentType.PNG
        else:
            self.content_type = self.ContentType.JPG
    
    def clean_description(self):
        if self.description == "" or not self.description:
            self.description = str(self)

    def clean_size(self):
        if self.size == 0 or not self.size:
            self.size = self.get_size()
    
    #TODO: Figure out page size
    def get_size(self):
        return 30

        

    def __str__(self):
        return f"{self.title}"
    

    
