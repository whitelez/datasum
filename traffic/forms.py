# code from Tango with Django
# http://www.tangowithdjango.com/book17/chapters/login.html
# http://www.tangowithdjango.com/book17/chapters/forms.html
# for form related classes

from django import forms
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')