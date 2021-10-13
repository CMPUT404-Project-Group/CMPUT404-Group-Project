from django import forms
from django.contrib.auth.forms import UserCreationForm
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
    username = forms.CharField(max_length=30, required=True)

    def save(self, commit=True):
            # user = super().save(commit=False)
            # user.set_password(self.cleaned_data["password1"])
            if commit:
                user = get_user_model().objects.create_user(email=self.cleaned_data["email"], username=self.cleaned_data["username"], github=self.cleaned_data["github"], password=self.cleaned_data["password1"], type="author")
            return user
    class Meta:
        model = User
        fields = ('username', 'email', 'github', 'password1', 'password2')

class PostCreationForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'text_content', 'image_content', 'categories', 'visibility')
