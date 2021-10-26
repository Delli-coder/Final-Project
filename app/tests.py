from django.test import TestCase
from .models import Auction
from datetime import *


auct = Auction.objects.get(id=1)
now = datetime.now()
if auct.close_data - now > timedelta(0, 0):
    print('active')
else:
    print('no-active')

# Create your tests here.
