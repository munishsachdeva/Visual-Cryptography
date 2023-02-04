from django import forms
from django.contrib.auth.models import User
from .models import *

# class CaptchaShare(forms.ModelForm):
 
#     class Meta:
#         model = ControlVote
#         fields = ['image']

class RegistrationForm(forms.ModelForm):
    confirm_password = forms.CharField(max_length=100, widget=forms.PasswordInput)
    # hidden_input = forms.ImageField()
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
        widgets = {
            'password': forms.PasswordInput,
        }



class ChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
