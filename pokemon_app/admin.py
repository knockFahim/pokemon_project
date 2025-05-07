from django.contrib import admin
from .models import Pokemon, PokemonType, UserPokemon, Message, UserProfile


class PokemonTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


class PokemonAdmin(admin.ModelAdmin):
    list_display = ('pokedex_id', 'name', 'get_types', 'base_hp', 'base_attack', 'base_defense')
    list_filter = ('types',)
    search_fields = ('name', 'pokedex_id')
    ordering = ('pokedex_id',)

    def get_types(self, obj):
        return ", ".join([t.name for t in obj.types.all()])

    get_types.short_description = 'Types'


class UserPokemonAdmin(admin.ModelAdmin):
    list_display = ('pokemon', 'user', 'nickname', 'level', 'capture_date')
    list_filter = ('pokemon__types', 'user', 'level')
    search_fields = ('pokemon__name', 'user__username', 'nickname')
    date_hierarchy = 'capture_date'


class MessageAdmin(admin.ModelAdmin):
    list_display = ('user', 'content', 'timestamp')
    list_filter = ('user', 'timestamp')
    search_fields = ('content', 'user__username')
    date_hierarchy = 'timestamp'


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')
    search_fields = ('user__username', 'bio')


admin.site.register(PokemonType, PokemonTypeAdmin)
admin.site.register(Pokemon, PokemonAdmin)
admin.site.register(UserPokemon, UserPokemonAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(UserProfile, UserProfileAdmin)

# Register your models here.
