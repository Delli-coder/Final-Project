from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=256, default='')
    wallet = models.FloatField(default=1000)
    total_bet = models.IntegerField(default=0)
    wins = models.IntegerField(default=0)
    active = models.BooleanField(default=True)


class Auction(models.Model):
    object = models.CharField(max_length=50)
    description = models.CharField(max_length=256, default='')
    image = models.ImageField(upload_to='media/', null=True, blank=True)
    open_date = models.DateTimeField(auto_now_add=True)
    close_date = models.DateTimeField()
    total_bet = models.IntegerField(default=0)
    open_price = models.FloatField(default=0, )
    close_price = models.FloatField(default=0)
    winner = models.CharField(max_length=256, default='')
    active = models.BooleanField(default=True)
    json_details_file = models.TextField(default='')
    tx = models.CharField(max_length=256, default='')
