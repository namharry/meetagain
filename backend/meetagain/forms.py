from django import forms
from .models import LostItem

class LostItemForm(forms.ModelForm):
    class Meta:
        model = LostItem
        fields = ['name', 'description', 'category', 'lost_contact', 'lost_location', 'lost_date',
                  'found_location', 'found_date', 'is_claimed', 'image']
