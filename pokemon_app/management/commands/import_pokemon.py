import requests
import random
from django.core.management.base import BaseCommand
from pokemon_app.models import Pokemon, PokemonType


class Command(BaseCommand):
    help = 'Import Gen 1 Pokemon data from the PokeAPI'

    def handle(self, *args, **kwargs):
        # Create Pokemon types
        types = [
            "Normal", "Fire", "Water", "Electric", "Grass", "Ice", "Fighting",
            "Poison", "Ground", "Flying", "Psychic", "Bug", "Rock", "Ghost", "Dragon"
        ]

        # Create type objects
        type_objects = {}
        for type_name in types:
            pokemon_type, created = PokemonType.objects.get_or_create(name=type_name)
            type_objects[type_name.lower()] = pokemon_type
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created type: {type_name}'))

        # Generation 1 Pokémon are numbers 1-151
        for pokedex_id in range(1, 152):
            # Check if this Pokémon already exists
            if Pokemon.objects.filter(pokedex_id=pokedex_id).exists():
                self.stdout.write(f'Pokemon #{pokedex_id} already exists, skipping')
                continue

            # Fetch Pokémon data from PokeAPI
            self.stdout.write(f'Fetching Pokemon #{pokedex_id}...')
            response = requests.get(f'https://pokeapi.co/api/v2/pokemon/{pokedex_id}')

            if response.status_code != 200:
                self.stdout.write(self.style.ERROR(f'Failed to fetch Pokemon #{pokedex_id}'))
                continue

            pokemon_data = response.json()

            # Get species data for description
            species_response = requests.get(f'https://pokeapi.co/api/v2/pokemon-species/{pokedex_id}')
            species_data = species_response.json()

            # Find an English description
            description = "No description available"
            for entry in species_data.get('flavor_text_entries', []):
                if entry.get('language', {}).get('name') == 'en':
                    description = entry.get('flavor_text', '').replace('\\n', ' ').replace('\f', ' ')
                    break

            # Create the Pokemon object
            pokemon = Pokemon(
                pokedex_id=pokedex_id,
                name=pokemon_data['name'].capitalize(),
                height=pokemon_data['height'] / 10,  # Convert to meters
                weight=pokemon_data['weight'] / 10,  # Convert to kg
                description=description,
                image_url=pokemon_data['sprites']['other']['official-artwork']['front_default'],
                base_hp=next((stat['base_stat'] for stat in pokemon_data['stats'] if stat['stat']['name'] == 'hp'), 50),
                base_attack=next(
                    (stat['base_stat'] for stat in pokemon_data['stats'] if stat['stat']['name'] == 'attack'), 50),
                base_defense=next(
                    (stat['base_stat'] for stat in pokemon_data['stats'] if stat['stat']['name'] == 'defense'), 50),
                base_special_attack=next(
                    (stat['base_stat'] for stat in pokemon_data['stats'] if stat['stat']['name'] == 'special-attack'),
                    50),
                base_special_defense=next(
                    (stat['base_stat'] for stat in pokemon_data['stats'] if stat['stat']['name'] == 'special-defense'),
                    50),
                base_speed=next(
                    (stat['base_stat'] for stat in pokemon_data['stats'] if stat['stat']['name'] == 'speed'), 50),
            )
            pokemon.save()

            # Add types
            for type_data in pokemon_data['types']:
                type_name = type_data['type']['name']
                if type_name in type_objects:
                    pokemon.types.add(type_objects[type_name])

            self.stdout.write(self.style.SUCCESS(f'Created Pokemon: {pokemon.name}'))

        self.stdout.write(self.style.SUCCESS('Pokemon import completed!'))