from django.shortcuts import render, redirect
from .models import *
from .forms import *
from .utils import *
from django.contrib import messages
from django.contrib.auth.decorators import login_required


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            new_prof = Profile.objects.create(user=user, username=user.username)
            new_prof.save()
            messages.success(request, f'Welcome!, {username}.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


@login_required(login_url='login')
def new_auction(request):
    if request.method == 'POST':
        form = AuctionForm(request.POST)
        if form.is_valid():
            form.instance.open_data = datetime.now()
            form.save()
            messages.success(request, 'Auction create')
            return redirect('new_auction')
    else:
        form = AuctionForm()
    return render(request, 'new_auction.html', {'form': form})


@login_required(login_url='login')
def betting(request):
    id_ = request.session.get('selected_id')
    auction = Auction.objects.filter(id=id_)
    last_bets = last_bet(id_)
    last_users = last_user(id_)
    last_dates = last_date(id_)
    check = check_data(auction[0].close_data)
    all_bets = len_bets(id_)
    if check is True:
        if request.method == 'POST':
            user = request.user
            form = request.POST
            prof_user = Profile.objects.get(user=user)
            bet_price = form['bet']
            if all_bets < 1:
                if float(bet_price) >= auction[0].open_price:
                    now = datetime.now()
                    add_data_redis(auction[0].id, bet_price, datetime.strftime(now, "%m/%d/%Y, %H:%M:%S"), user)
                    prof_user.total_bet += 1
                    prof_user.save()
                    messages.success(request, 'Confermed!')
                    return redirect('betting')
                else:
                    messages.error(request, 'Bet lower than open price')
                    return redirect('betting')
            else:
                last_price = float(last_bets)
                if float(bet_price) > last_price:
                    now = datetime.now()
                    add_data_redis(auction[0].id, bet_price, datetime.strftime(now, "%m/%d/%Y, %H:%M:%S"), user)
                    prof_user.total_bet += 1
                    prof_user.save()
                    messages.success(request, 'Confermed!')
                else:
                    messages.error(request, 'Import is lower than last bet')
                return redirect('betting')
        return render(request, 'betting.html',
                      {'auction': auction, 'bets': last_bets,
                       'users': last_users, 'date': last_dates, 'tot_bets': all_bets})
    messages.error(request, 'Aucttion is closed!')
    return redirect('home')


@login_required(login_url='login')
def home(request):
    auction = Auction.objects.filter(active=True)
    for data in auction:
        check = check_data(data.close_data)
        if check is False:
            data.active = False
            data.save()
            check_winner(request, data.id)
    check_prof = check_profile(request)
    if check_prof is True:
        return redirect('profile')
    auctions_open = Auction.objects.filter(active=True)
    if request.method == 'POST':
        form = request.POST
        auct_ids = form['auct_id']
        auct_id = int(auct_ids)
        request.session['selected_id'] = auct_id
        return redirect('betting')
    else:
        return render(request, 'home.html', {'auction': auctions_open})


@login_required(login_url='login')
def info_profile(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    if profile.wallet < 0:
        messages.error(request, f'Attention! you must pay {profile.wallet}')
    return render(request, 'profile.html', {'profile': profile})



