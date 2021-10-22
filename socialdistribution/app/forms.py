from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from api.models import Post, User
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model


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
        if "user" in kwargs:
            self.user = kwargs.pop("user")
        if "data" in kwargs:
            self.image = kwargs['data']['image_content']
        super(PostCreationForm, self).__init__(*args, **kwargs)

    # TODO: Unlisted always false
    def save(self, commit=True):
        assert self.user, "User is not defined"
        post = Post.objects.create_post(
            author=self.user,
            categories=self.cleaned_data['categories'],
            image_content=self.image,
            text_content=self.cleaned_data["text_content"],
            title=self.cleaned_data["title"],
            visibility=self.cleaned_data["visibility"],
            unlisted=False
        )

class ManageProfileForm(UserChangeForm):

    password = None

    class Meta:
        model = User
        fields = ('displayName', 'email', 'github')
