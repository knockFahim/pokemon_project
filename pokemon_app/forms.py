from django import forms
from .models import UserProfile, UserPokemon, Message, Pokemon
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class TeamSelectionForm(forms.Form):
    selected_pokemon = forms.ModelMultipleChoiceField(
        queryset=UserPokemon.objects.none(),  # Will be set in __init__
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, user, *args, **kwargs):
        super(TeamSelectionForm, self).__init__(*args, **kwargs)
        # Only show pokemon owned by this user
        self.fields['selected_pokemon'].queryset = UserPokemon.objects.filter(user=user)

    def clean_selected_pokemon(self):
        selected = self.cleaned_data['selected_pokemon']
        if len(selected) > 6:
            raise forms.ValidationError("You can only select up to 6 Pokémon for your team.")
        return selected

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Type your message here...',
                'class': 'form-control'
            }),
        }

class TradeForm(forms.Form):
    offered_pokemon = forms.ModelChoiceField(queryset=None, label="Pokémon to Offer")
    wanted_pokemon_type = forms.ModelChoiceField(queryset=Pokemon.objects.all(), label="Pokémon Type Wanted")
    content = forms.CharField(widget=forms.Textarea, required=False, label="Message (optional)")

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['offered_pokemon'].queryset = UserPokemon.objects.filter(user=user)

class AcceptTradeForm(forms.Form):
    pokemon_id = forms.ModelChoiceField(queryset=None, label="Pokémon to Trade")

    def __init__(self, user, wanted_type, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pokemon_id'].queryset = UserPokemon.objects.filter(user=user, pokemon=wanted_type)

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")