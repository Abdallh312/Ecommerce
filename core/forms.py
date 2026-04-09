from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm as BasePasswordResetForm

class PasswordResetForm(BasePasswordResetForm):
    """Custom password reset form."""
    pass