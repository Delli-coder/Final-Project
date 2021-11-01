from django import forms
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
        fields = ['object', 'description', 'close_date', 'open_price']


class AuctionBet(forms.ModelForm):
    class Meta:
        model = Auction
        fields = ['open_price']
