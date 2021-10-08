from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, email, username, github=None, password=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
            github=github,
            username=username
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, github=None, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            github=github,
            username=username
        )
        user.is_active = True
        user.is_admin = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    email = models.EmailField(max_length=255, unique=True, verbose_name="email address")
    username = models.CharField(max_length=20, unique=True)
    github = models.CharField(max_length=50, unique=True, null=True, blank=True)
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

class Post(models.Model):
    
    class Visibility(models.IntegerChoices):
        PUBLIC = 0

    title = models.TextField()
    author_id = models.IntegerField(editable=False)
    text_content = models.TextField(blank=True)
    image_content = models.ImageField(blank=True)
    date_published = models.DateTimeField(editable=False, auto_now_add=True)
    public = models.IntegerField(choices=Visibility.choices, default='public')

    def __str__(self):
        return f"{self.author_id}, {self.title}, {self.text_content[:10]}..."
    

    
