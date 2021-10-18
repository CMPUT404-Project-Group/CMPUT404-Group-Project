from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from .models import User, Post


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    set_password = forms.CharField(
        label='Password', widget=forms.PasswordInput)
    confirm_password = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)
    github = forms.CharField(label="github", required=False)

    class Meta:
        model = User
        fields = ('email', 'github')

    def clean_confirm_password(self):
        # Check that the two password entries match
        set_password = self.cleaned_data.get("set_password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if set_password and confirm_password and set_password != confirm_password:
            raise ValidationError("Passwords don't match")
        return confirm_password

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["set_password"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('displayName', 'email', 'github', 'password')


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'displayName', 'github', 'is_admin', 'is_active')
    list_filter = ('is_admin', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'displayName',
         'github', 'password', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('displayName', 'email', 'github', 'password1', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()


admin.site.register(User, UserAdmin)
admin.site.register(Post)

admin.site.unregister(Group)
