from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.db import models, IntegrityError
from django.db.models.constraints import UniqueConstraint
from django.db.models.deletion import CASCADE
from django.db.models.manager import BaseManager
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

from dotenv import load_dotenv
import markdown
import os
from uuid import uuid4
import logging 

from django.conf import settings
HOST_API_URL = settings.HOST_API_URL


class SettingManager(models.Manager):
    def create_setting(self, setting, on):
        setting = self.create(setting=setting, on=on)
        return setting


class SiteSetting(models.Model):
    setting = models.CharField(max_length=255, unique=True)
    on = models.BooleanField()

    objects = SettingManager()

    def value(self):
        return self.on


class UserManager(BaseUserManager):
    def create_user(self, email, displayName, github=None, password=None, type="author"):
        """
        Creates and saves a User.
        """
        if not email:
            raise ValueError('Users must have an email address')

        uuid = uuid4()
        host = HOST_API_URL

        user = self.model(
            type=type,
            id=uuid,
            host=host,
            displayName=displayName,
            url=host+str(uuid),
            github=github,
            email=self.normalize_email(email),
        )

        user.is_active = SiteSetting.objects.get(setting="allow_join").value()
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, displayName, github=None, password=None, type="server-admin"):
        """
        Creates and saves a superuser.
        """
        user = self.create_user(
            email,
            displayName=displayName,
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
    type = models.CharField(max_length=255, unique=False,
                            null=False, blank=False, default="author")
    id = models.UUIDField(auto_created=True, max_length=255,
                          unique=True, null=False, blank=False, primary_key=True, default=uuid4)
    host = models.URLField(max_length=255, unique=False,
                           null=False, blank=False, default=HOST_API_URL)
    displayName = models.CharField(max_length=255, unique=True)
    url = models.CharField(max_length=255, unique=False,
                           blank=False, null=False, default=HOST_API_URL)
    github = models.CharField(
        max_length=50, unique=True, blank=True, null=True)

    # user metadata
    email = models.EmailField(
        max_length=255, unique=True, verbose_name="email address")
    is_active = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'displayName'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.displayName

    def has_perm(self, perm, obj=None):
        return True  # temp

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

    class Meta:
        ordering = ['displayName']


class PostBuilder():

    def __init__(self, id=None, published=None):
        self.id = id
        self.published = published
        if not id:
            self.id = uuid4()

        self.type = 'post'
        self.source = None
        self.origin = None
        self.count = 0
        self.comment_page = None

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
        self.shared_post = None

    def set_post_content(self, title, categories, text_content=None, image_content=None, shared_post=None, image_link=None):
        self.title = title
        self.categories = categories
        self.text_content = text_content
        self.image_content = image_content
        self.shared_post = shared_post
        self.image_link = image_link

    # TODO: Description is not very descriptive
    def set_post_metadata(self, author, visibility, unlisted):
        assert self.title, "set_post_content must be called before set_post_metadata"

        self.author = author
        self.visibility = visibility
        self.unlisted = unlisted

        self.__set_description__()
        self.__set_content_type__()
        self.__set_urls__()
        self.__set_size__()

    def get_post(self):
        post = Post(
            type=self.type,
            title=self.title,
            id=self.id,
            source=self.source,
            origin=self.origin,
            description=self.description,
            content_type=self.content_type,
            text_content=self.text_content,
            image_content=self.image_content,
            image_link=self.image_link,
            author=self.author,
            categories=self.categories,
            count=self.count,
            size=self.size,
            comment_page=self.comment_page,
            visibility=self.visibility,
            unlisted=self.unlisted,
            shared_post = self.shared_post

        )

        if not self.published:
            return post

        post.published = self.published
        return post

    def __set_description__(self):
        self.description = f"{self.title}"
        if self.text_content:
            self.description += f": {self.text_content[0:50]}..."

    # TODO: Content type just defaults to plain text at the moment
    def __set_content_type__(self):
        self.content_type = Post.ContentType.PLAIN
        marked_down_text = markdown.Markdown().convert(self.text_content)
        tag_stipped_text = marked_down_text.strip('<p>').strip('</p>')
        if tag_stipped_text != self.text_content:
            self.content_type = Post.ContentType.MARKDOWN
    
    def __set_urls__(self):
        post_url = f"{HOST_API_URL}author/{self.author.id}/posts/{self.id}"
        
        self.origin = post_url
        self.source = post_url
        self.comment_page = f"{post_url}/comments"


    # TODO: Figure out size of post dynamically (possibly iterate through attributes adding size)
    def __set_size__(self):
        self.size = 0


class PostManager(models.Manager):

    def create_post(self, author, categories, image_content, text_content, title, visibility, unlisted, image_link=None):
        post_builder = PostBuilder()
        post_builder.set_post_content(
            title, categories, text_content, image_content, None, image_link)
        post_builder.set_post_metadata(author, visibility, unlisted)

        post = post_builder.get_post()
        post.save(using=self._db)
        return post

    def share_post(self, author, text_content, title, categories, visibility, unlisted, shared_post):
        post_builder = PostBuilder()
        post_builder.set_post_content(title, categories, text_content, None, shared_post)
        post_builder.set_post_metadata(author, visibility, unlisted)

        post = post_builder.get_post()
        post.save(using=self._db)
        return post

# TODO: Specify uploadto field for image_content to post_imgs within project root
# TODO: Upon adding comment model add comment as foreign key
# TODO: Increment count upon commenting
class Post(models.Model):

    class Visibility(models.TextChoices):
        PUBLIC = "public"
        PRIVATE_TO_AUTHOR = "private_to_author"
        PRIVATE_TO_FRIEND = "private_to_friend"

    class ContentType(models.TextChoices):
        MARKDOWN = "text/markdown"
        PLAIN = "text/plain"
        APPLICATION = "application/base64"
        PNG = "image/png;base64"
        JPG = "image/jpg;base64"

    type = models.CharField(max_length=255, unique=False,
                            null=False, blank=False, default="post")
    title = models.CharField(
        max_length=255, unique=False, null=False, blank=False)
    id = models.CharField(max_length=255, unique=True,
                          null=False, primary_key=True)
    source = models.URLField(
        max_length=255, unique=False, null=False, blank=False)
    origin = models.URLField(
        max_length=255, unique=False, null=False, blank=False)
    description = models.CharField(
        max_length=255, unique=False, null=False, blank=False)
    content_type = models.CharField(
        max_length=255, choices=ContentType.choices)
    text_content = models.TextField(unique=False, blank=True)
    image_content = models.ImageField(unique=False, blank=True, upload_to="images/")
    image_link = models.TextField(unique=False, blank=True, null=True)
    author = models.ForeignKey(
        "User",
        on_delete=models.CASCADE
    )
    categories = models.TextField(unique=False, blank=True, null=False)
    count = models.IntegerField(
        unique=False, null=False, blank=False, default=0)
    size = models.IntegerField(unique=False, null=False, blank=False)
    comment_page = models.CharField(
        max_length=255, unique=False, null=False, blank=False)
    # comments could potentially be done at serialization to avoid data duplication
    # (get all comments which have this post_id within their comment_id)
    # If we do this size may also have to be done at serialization although I think this may be easier anyways
    published = models.DateTimeField(
        unique=False, blank=False, null=False, auto_now_add=True)
    visibility = models.CharField(
        max_length=255, choices=Visibility.choices, unique=False, blank=False, null=False, default=Visibility.PUBLIC)
    unlisted = models.BooleanField(
        unique=False, blank=False, null=False, default=False)
    shared_post = models.ForeignKey("api.Post", null=True, on_delete=CASCADE)

    objects = PostManager()

    def __str__(self):
        return f"{self.author}, {self.title}, {self.text_content}, {self.image_content}, {self.categories}"

    class Meta:
        ordering = ['published']

# TODO: Add other content types (currently just plain and markdown)
# TODO: Add posts or post_id to comment model
class CommentManager(models.Manager):

    def create_comment(self, author, comment, post):

        content_type = self.__get_content_type__(comment)
        
        comment = Comment(
            type="comment",
            author=author,
            comment=comment,
            content_type=content_type,
            post=post,
            id=uuid4()
        )
        comment.save()

        return comment
    
    def __get_content_type__(self, comment):
        content_type = Post.ContentType.PLAIN
        marked_down_comment = markdown.Markdown().convert(comment)
        tag_stipped_comment = marked_down_comment.strip('<p>').strip('</p>')
        if tag_stipped_comment != comment:
            content_type = Post.ContentType.MARKDOWN
        return content_type


class Comment(models.Model):
    id = models.CharField(max_length=255, unique=True,
                          null=False, blank=False, primary_key=True)
    type = models.CharField(max_length=255, unique=False,
                            null=False, blank=False)
    author = models.ForeignKey("User", on_delete=models.CASCADE)
    comment = models.TextField(unique=False, blank=False, null=False)
    content_type = models.CharField(
        max_length=255, unique=False, null=False, blank=False)
    published = models.DateTimeField(
        unique=False, blank=False, null=False, auto_now_add=True)
    post = models.ForeignKey("Post", on_delete=CASCADE)
    objects = CommentManager()

    class Meta:
        ordering = ['published']


#TODO: context is currently a placeholder
class LikeManager(models.Manager):

    def create_like(self, author, content_object):
        summary = f"{author} liked {content_object}"

        like = Like(
            id=uuid4(),
            context=HOST_API_URL,
            summary=summary,
            type='like',
            author=author,
            content_object=content_object
        )

        try:
            like.save()
        except IntegrityError:
            return None

        return like

class Like(models.Model):
    id = models.CharField(max_length=255, unique=True, null=False, blank=False, primary_key=True)
    context = models.URLField(max_length=255, unique=False, null=False, blank=False)
    summary = models.CharField(max_length=255, unique=False, null=False, blank=False)
    type = models.CharField(max_length=255, unique=False, null=False, blank=False)
    author = models.ForeignKey("User", on_delete=CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=CASCADE)
    object_id = models.CharField(max_length=255, unique=False, null=False, blank=False)
    content_object = GenericForeignKey('content_type', 'object_id')

    objects = LikeManager()

    class Meta:
        unique_together = (('content_type', 'object_id', 'author'))



class InboxManager(models.Manager):
    def create(self, author_id, item):
        inbox = self.model(
            author_id=author_id,
            item=item,
        )
        inbox.save(using=self._db)
        return inbox


class Inbox(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    item = models.JSONField(default=dict)
    created_at = models.DateTimeField(unique=False, blank=False, null=False, auto_now_add=True)
    objects = InboxManager()

    class Meta:
        ordering = ['-created_at']
        
