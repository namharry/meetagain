from django import forms
from .models import FoundItem

class FoundItemForm(forms.ModelForm):
    class Meta:
        model = FoundItem
        # lat, lng는 지도에서 받기 때문에 제외!
        fields = [
            'name',
            'description',
            'category',
            'found_location',
            'found_date',
            'image',
        ]