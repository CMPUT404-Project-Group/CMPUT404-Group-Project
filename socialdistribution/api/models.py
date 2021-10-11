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
            username=username,  # displayName
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
    type = models.CharField(max_length=255, unique=False,
                            null=False, blank=False, default="author")
    id = models.CharField(auto_created=True, max_length=255,
                          unique=True, null=False, blank=False, primary_key=True)
    host = models.URLField(max_length=255, unique=False,
                           null=False, blank=False, default=HOST_API_URL)
    # this should be returned from the API as displayName; keep it as username in db for default django stuff
    username = models.CharField(max_length=255, unique=True)
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

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username

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
