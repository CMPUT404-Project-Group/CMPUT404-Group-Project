from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from api.models import Comment, Post, User
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
import logging


class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        # https://stackoverflow.com/a/46283680 - CC BY-SA 3.0
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    github = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(max_length=255, required=True)
    displayName = forms.CharField(max_length=30, required=True)

    def save(self, commit=True):
        if commit:
            user = get_user_model().objects.create_user(email=self.cleaned_data["email"], displayName=self.cleaned_data[
                "displayName"], github=self.cleaned_data["github"], password=self.cleaned_data["password1"], type="author")
        return user

    class Meta:
        model = User
        fields = ('displayName', 'email', 'github', 'password1', 'password2')


class PostCreationForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text_content', 'image_content',
                  'categories', 'visibility')

    def __init__(self, *args, **kwargs):
        self.user = None
        self.id = None

        if "user" in kwargs:
            self.user = kwargs.pop("user")
        if "id" in kwargs:
            self.id = kwargs.pop("id")
        if "published" in kwargs:
            self.published = kwargs.pop("published")
        super(PostCreationForm, self).__init__(*args, **kwargs)

    # TODO: Unlisted always false
    def save(self, commit=True):
        assert self.user, "User is not defined"

        if not self.id:
            return Post.objects.create_post(
                author=self.user,
                categories=self.cleaned_data['categories'],
                image_content=self.cleaned_data["image_content"],
                text_content=self.cleaned_data["text_content"],
                title=self.cleaned_data["title"],
                visibility=self.cleaned_data["visibility"],
                unlisted=False
            )
        else:
            return Post.objects.edit_post(
                author=self.user,
                categories=self.cleaned_data['categories'],
                image_content=self.cleaned_data["image_content"],
                text_content=self.cleaned_data["text_content"],
                title=self.cleaned_data["title"],
                visibility=self.cleaned_data['visibility'],
                unlisted=False,
                id=self.id,
                published=self.published
            )

class SharePostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text_content', 'categories', 'visibility')
    
    def __init__(self, *args, **kwargs):
        self.user = None
        self.post = None

        if "user" in kwargs:
            self.user = kwargs.pop("user")
        if "post" in kwargs:
            self.post = kwargs.pop("post")
        super(SharePostForm, self).__init__(*args, **kwargs)
    
    def save(self, commit=True):
        assert self.user, "User is not defined"
        assert self.post, "Post to be shared is not defined"

        new_shared_post = Post.objects.share_post(
                author=self.user,
                text_content=self.cleaned_data["text_content"],
                title="{} shared a post".format(self.user),
                categories=self.cleaned_data['categories'],
                visibility=self.cleaned_data["visibility"],
                unlisted=False,
                shared_post=self.post
        )

        return new_shared_post

class ManageProfileForm(UserChangeForm):
    github = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(max_length=255, required=True)
    displayName = forms.CharField(max_length=30, required=True)
    password = None
    class Meta:
        model = User
        fields = ('displayName', 'email', 'github')


class CommentCreationForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('comment',)

    def __init__(self, *args, **kwargs):
        self.user = None
        self.post = None

        if "user" in kwargs:
            self.user = kwargs.pop("user")
        if "post" in kwargs:
            self.post = kwargs.pop("post")
        super(CommentCreationForm, self).__init__(*args, **kwargs)

    def save(self, commit=True):
        assert self.user, "User is not defined"
        assert self.post, "Post is not defined"

        comment = Comment.objects.create_comment(
            author=self.user,
            comment=self.cleaned_data['comment'],
            post=self.post
        )

        return comment

