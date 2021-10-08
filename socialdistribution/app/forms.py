from django import forms
from django.contrib.auth.forms import UserCreationForm
from api.models import Post, User
from django.utils.translation import gettext_lazy as _


class RegisterForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        # https://stackoverflow.com/a/46283680 - CC BY-SA 3.0
        for field in self.fields.values():
            field.widget.attrs['class'] = 'input'

    github_username = forms.CharField(max_length=30, required=False)
    email = forms.EmailField(max_length=255, required=True)
    username = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'github_username', 'password1', 'password2')

class Post_Creation_Form(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text_content', 'image_content', 'public')
