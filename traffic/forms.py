# code from Tango with Django
# http://www.tangowithdjango.com/book17/chapters/login.html
# http://www.tangowithdjango.com/book17/chapters/forms.html
# for form related classes

from django import forms
from django.contrib.auth.models import User

class UserForm(forms.ModelForm):
    #password = forms.CharField(widget=forms.PasswordInput()) # for users to input password
    organization = forms.CharField()
    # for user to input their intended use
    intended_use = forms.CharField(label="Intended use", max_length=500, widget=forms.Textarea)

    class Meta:
        model = User
        fields = (
                    'username',
                    'email',
                    #'password' #manually verify user and grant permission currently
                  )