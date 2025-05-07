from django.db import models
from django.contrib.auth.models import User
import random


class PokemonType(models.Model):
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class Pokemon(models.Model):
    # Gen 1 Pokémon have IDs from 1-151
    pokedex_id = models.IntegerField(unique=True)
    name = models.CharField(max_length=100)
    types = models.ManyToManyField(PokemonType)
    height = models.FloatField()  # in meters
    weight = models.FloatField()  # in kg
    description = models.TextField()
    image_url = models.URLField()
    base_hp = models.IntegerField()
    base_attack = models.IntegerField()
    base_defense = models.IntegerField()
    base_special_attack = models.IntegerField()
    base_special_defense = models.IntegerField()
    base_speed = models.IntegerField()

    def __str__(self):
        return f"#{self.pokedex_id} - {self.name}"

def random_level():
    return random.randint(5, 100)

def random_iv():
    return random.randint(0, 31)


class UserPokemon(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="pokemon")
    pokemon = models.ForeignKey(Pokemon, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=100, blank=True, null=True)
    capture_date = models.DateTimeField(auto_now_add=True)
    level = models.IntegerField(default=random_level)  # Start at level 5
    iv_hp = models.IntegerField(default=random_iv)
    iv_attack = models.IntegerField(default=random_iv)
    iv_defense = models.IntegerField(default=random_iv)
    iv_special_attack = models.IntegerField(default=random_iv)
    iv_special_defense = models.IntegerField(default=random_iv)
    iv_speed = models.IntegerField(default=random_iv)

    def __str__(self):
        if self.nickname:
            return f"{self.nickname} ({self.pokemon.name}) - owned by {self.user.username}"
        return f"{self.pokemon.name} - owned by {self.user.username}"

    # Calculate actual stats based on base stats, level, and IVs
    @property
    def hp(self):
        return int(((2 * self.pokemon.base_hp + self.iv_hp) * self.level / 100) + self.level + 10)

    @property
    def attack(self):
        return int(((2 * self.pokemon.base_attack + self.iv_attack) * self.level / 100) + 5)

    @property
    def defense(self):
        return int(((2 * self.pokemon.base_defense + self.iv_defense) * self.level / 100) + 5)

    @property
    def special_attack(self):
        return int(((2 * self.pokemon.base_special_attack + self.iv_special_attack) * self.level / 100) + 5)

    @property
    def special_defense(self):
        return int(((2 * self.pokemon.base_special_defense + self.iv_special_defense) * self.level / 100) + 5)

    @property
    def speed(self):
        return int(((2 * self.pokemon.base_speed + self.iv_speed) * self.level / 100) + 5)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    # Change the related model from Pokemon to UserPokemon
    selected_pokemon = models.ManyToManyField('UserPokemon', blank=True, related_name='selected_by_profiles')

    def __str__(self):
        return self.user.username

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"

class TradeMessage(Message):
    is_completed = models.BooleanField(default=False)
    accepted_by = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='accepted_trades')
    offered_pokemon = models.ForeignKey('UserPokemon', on_delete=models.CASCADE, related_name='trade_offers')
    traded_pokemon = models.ForeignKey('UserPokemon', blank=True, null=True, on_delete=models.SET_NULL, related_name='traded_for')
    wanted_pokemon_type = models.ForeignKey('Pokemon', on_delete=models.CASCADE, related_name='trade_requests')

# Create your models here.
