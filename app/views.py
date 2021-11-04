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
            new_prof = Profile.objects.create(user=user, username=user.username)  # profilo creato con 1000 $
            new_prof.save()
            messages.success(request, f'Welcome!, {username}.')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


@login_required(login_url='login')
def new_auction(request):
    if request.method == 'POST':
        form = AuctionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Auction create')  # nuova asta creata con i parametri scelti
            return redirect('new_auction')
    else:
        form = AuctionForm()
    return render(request, 'new_auction.html', {'form': form})


@login_required(login_url='login')
def betting(request):
    if request.user.is_superuser:
        messages.error(request, 'super user can access to admin/ and new_auction page only')
        return redirect('new_auction')
    id_ = request.session.get('selected_id')
    auction = Auction.objects.filter(id=id_)
    last_bets = last_bet(id_)
    last_users = last_user(id_)
    last_dates = last_date(id_)
    check = check_data(auction[0].close_date)  # secondo check per la data di chiusura dell'asta
    all_bets = len_bets(id_)
    if check is True:
        if request.method == 'POST':
            user = request.user
            form = request.POST
            prof_user = Profile.objects.get(user=user)
            bet_price = form['bet']
            if all_bets < 1:  # se non ci sono ancora scommesse effettuate,
                # l'importo dovra essere maggiore dell'open price scelto alla creazione dell'asta
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
    if request.user.is_superuser:
        messages.error(request, 'super user can access to admin/ and new_auction page only')
        return redirect('new_auction')
    auction = Auction.objects.filter(active=True)
    for data in auction:
        check = check_data(data.close_date)  # primo check data fine asta
        if check is False:
            data.active = False
            data.save()
            check_winner(request, data.id)  # funzione per aggiudicare il vincitore, creare il fileJson con i dettagli
            # dell'asta conclusa ed invia l'hash del file Jsone in una transazione sulla blockchain
    check_prof = check_profile(request)  # se il profilo utente ha il saldo negativo viene reindirizzato alla pagina
    # personale invitando di effettuare il pagamento
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
    if request.user.is_superuser:
        messages.error(request, 'super user can access to admin/ and new_auction page only')
        return redirect('new_auction')
    user = request.user
    profile = Profile.objects.get(user=user)
    if profile.wallet < 0:
        messages.error(request, f'Attention! you must pay {profile.wallet}')
    return render(request, 'profile.html', {'profile': profile})



