from django import forms
from django.forms import DateTimeInput
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Auction


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class AuctionForm(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['object', 'description', 'image',  'close_date', 'open_price']
        widgets = {'close_date': DateTimeInput(attrs={'placeholder': 'YYYY-MM-DD HH:MM'})}


class AuctionBet(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['open_price']
