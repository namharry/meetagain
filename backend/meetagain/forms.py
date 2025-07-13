from django import forms
from .models import LostItem
from .models import FoundItem

class LostItemForm(forms.ModelForm):
    class Meta:
        model = LostItem
        fields = [
            'name',
            'description',
            'category',
            'lost_contact',
            'lost_location',
            'lost_date',
            'is_claimed',
            'image'
        ]

class FoundItemForm(forms.ModelForm):
    class Meta:
        model = FoundItem
        fields = [
            'name',
            'description',
            'category',
            'found_location',
            'found_date',
            'is_returned',
            'image',
            'lat',
            'lng'
        ]