import random
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from .models import Pokemon, UserPokemon, UserProfile, Message, TradeMessage
from django.db.models import Count
from .forms import TeamSelectionForm, MessageForm, TradeForm, AcceptTradeForm
from django.views.decorators.http import require_POST
from django.http import JsonResponse


def index(request):
    """Homepage view"""
    # Get 5 random Pokémon to display
    random_pokemon = Pokemon.objects.order_by('?')[:5]

    user_pokemon_count = 0
    if request.user.is_authenticated:
        user_pokemon_count = UserPokemon.objects.filter(user=request.user).count()
    
    # Get profiles for leaderboard (only those with selected pokemon)
    profiles = UserProfile.objects.annotate(
        pokemon_count=Count('selected_pokemon')
    ).filter(pokemon_count__gt=0).order_by('-pokemon_count')[:5]

    return render(request, 'pokemon_app/index.html', {
        'random_pokemon': random_pokemon,
        'user_pokemon_count': user_pokemon_count,
        'profiles': profiles,  # Add profiles to context
    })

def custom_logout(request):
    """Custom logout view that accepts both GET and POST methods"""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect('index')

def pokemon_list(request):
    """View all available Pokémon"""
    pokemon = Pokemon.objects.all().order_by('pokedex_id')
    return render(request, 'pokemon_app/pokemon_list.html', {'pokemon': pokemon})


def pokemon_detail(request, pokemon_id):
    """View details of a specific Pokémon"""
    pokemon = get_object_or_404(Pokemon, pokedex_id=pokemon_id)

    # Check if user owns this Pokémon
    user_pokemon = None
    if request.user.is_authenticated:
        user_pokemon = UserPokemon.objects.filter(user=request.user, pokemon=pokemon)

    return render(request, 'pokemon_app/pokemon_detail.html', {
        'pokemon': pokemon,
        'user_pokemon': user_pokemon,
    })


@login_required
def generate_pokemon(request):
    """Generate a random Pokémon for the user"""
    if request.method == 'POST':
        # Select a random Pokémon
        random_id = random.randint(1, 151)
        pokemon = get_object_or_404(Pokemon, pokedex_id=random_id)

        # Generate random IVs (0-31, like in the actual games)
        iv_hp = random.randint(0, 31)
        iv_attack = random.randint(0, 31)
        iv_defense = random.randint(0, 31)
        iv_special_attack = random.randint(0, 31)
        iv_special_defense = random.randint(0, 31)
        iv_speed = random.randint(0, 31)

        # Create a new UserPokemon
        user_pokemon = UserPokemon(
            user=request.user,
            pokemon=pokemon,
            iv_hp=iv_hp,
            iv_attack=iv_attack,
            iv_defense=iv_defense,
            iv_special_attack=iv_special_attack,
            iv_special_defense=iv_special_defense,
            iv_speed=iv_speed,
        )
        user_pokemon.save()

        messages.success(request, f'You caught a {pokemon.name}!')
        return redirect('my_pokemon')

    return redirect('index')


@login_required
def my_pokemon(request):
    """View all Pokémon owned by the user"""
    user_pokemon = UserPokemon.objects.filter(user=request.user).order_by('-capture_date')
    return render(request, 'pokemon_app/my_pokemon.html', {'user_pokemon': user_pokemon})


@login_required
def nickname_pokemon(request, user_pokemon_id):
    """Give a nickname to a Pokémon"""
    if request.method == 'POST':
        user_pokemon = get_object_or_404(UserPokemon, id=user_pokemon_id, user=request.user)
        nickname = request.POST.get('nickname', '').strip()

        if nickname:
            user_pokemon.nickname = nickname
            user_pokemon.save()
            messages.success(request, f'Your {user_pokemon.pokemon.name} is now known as {nickname}!')
        else:
            messages.error(request, 'Please provide a valid nickname.')

    return redirect('my_pokemon')


@login_required
def release_pokemon(request, user_pokemon_id):
    """Release a Pokémon back into the wild"""
    if request.method == 'POST':
        user_pokemon = get_object_or_404(UserPokemon, id=user_pokemon_id, user=request.user)
        pokemon_name = user_pokemon.nickname or user_pokemon.pokemon.name
        user_pokemon.delete()
        messages.success(request, f'You released {pokemon_name} back into the wild.')

    return redirect('my_pokemon')

@login_required
def select_pokemon(request):
    """View for selecting pokemon for the leaderboard team"""
    # Get or create user profile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get all user's pokemon
    user_pokemon = UserPokemon.objects.filter(user=request.user)
    
    # Get currently selected pokemon IDs
    selected_ids = [p.id for p in profile.selected_pokemon.all()]
    
    if request.method == 'POST':
        # Get selected pokemon IDs from form
        selected_ids = request.POST.getlist('selected_pokemon')
        
        # Validate maximum of 6 selections
        if len(selected_ids) > 6:
            messages.error(request, "You can only select up to 6 Pokémon for your team.")
        else:
            # Clear current selections
            profile.selected_pokemon.clear()
            
            # Add new selections
            for pokemon_id in selected_ids:
                pokemon = get_object_or_404(UserPokemon, id=pokemon_id, user=request.user)
                profile.selected_pokemon.add(pokemon)
            
            messages.success(request, "Your team has been updated!")
            return redirect('index')
    
    return render(request, 'pokemon_app/select_pokemon.html', {
        'user_pokemon': user_pokemon,
        'selected_ids': [int(id) for id in selected_ids],
    })

def leaderboard(request):
    """Full leaderboard view"""
    profiles = UserProfile.objects.annotate(
        pokemon_count=Count('selected_pokemon')
    ).filter(pokemon_count__gt=0).order_by('-pokemon_count')
    
    # Check if user has team
    has_team = False
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            has_team = profile.selected_pokemon.exists()
        except UserProfile.DoesNotExist:
            pass
    
    return render(request, 'pokemon_app/leaderboard.html', {
        'profiles': profiles,
        'has_team': has_team,
    })

@login_required
def message_board(request):
    """Message board view with message submission form"""
    all_messages = Message.objects.all().order_by('-timestamp')
    trade_form = TradeForm(request.user) if request.user.is_authenticated else None
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            new_message = form.save(commit=False)
            new_message.user = request.user
            new_message.save()
            messages.success(request, "Your message has been posted!")
            return redirect('message_board')
    else:
        form = MessageForm()
    return render(request, 'pokemon_app/message_board.html', {
        'messages_list': all_messages,
        'form': form,
        'trade_form': trade_form,
    })

@login_required
def create_trade(request):
    if request.method == 'POST':
        form = TradeForm(request.user, request.POST)
        if form.is_valid():
            trade = TradeMessage.objects.create(
                user=request.user,
                offered_pokemon=form.cleaned_data['offered_pokemon'],
                wanted_pokemon_type=form.cleaned_data['wanted_pokemon_type'],
                content=form.cleaned_data['content'],
            )
            messages.success(request, "Trade offer posted!")
            return redirect('message_board')
    else:
        form = TradeForm(request.user)
    return render(request, 'pokemon_app/create_trade.html', {'form': form})

@login_required
@require_POST
def accept_trade(request, trade_id):
    trade = get_object_or_404(TradeMessage, id=trade_id, is_completed=False)
    if trade.user == request.user:
        messages.error(request, "You cannot accept your own trade.")
        return redirect('message_board')
    user_pokemon_id = request.POST.get('pokemon_id')
    user_pokemon = get_object_or_404(UserPokemon, id=user_pokemon_id, user=request.user, pokemon=trade.wanted_pokemon_type)
    initiator_pokemon = trade.offered_pokemon
    initiator = trade.user
    initiator_pokemon.user = request.user
    user_pokemon.user = initiator
    initiator_pokemon.save()
    user_pokemon.save()
    trade.is_completed = True
    trade.accepted_by = request.user
    trade.traded_pokemon = user_pokemon
    trade.save()
    messages.success(request, "Trade completed successfully!")
    return redirect('message_board')

@login_required
def get_trade_pokemon_options(request, trade_id):
    trade = get_object_or_404(TradeMessage, id=trade_id, is_completed=False)
    user_pokemon = UserPokemon.objects.filter(user=request.user, pokemon=trade.wanted_pokemon_type)
    data = {
        "pokemon": [
            {
                "id": up.id,
                "name": up.nickname or up.pokemon.name,
                "level": up.level,
                "image": up.pokemon.image_url,
            }
            for up in user_pokemon
        ]
    }
    return JsonResponse(data)

# Create your views here.
