from django import forms
from .models import LostItem, FoundItem
from django.core.exceptions import ValidationError
from datetime import date 

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
    
    def clean(self): #모든 필드가 입력되었는지 확인해주는 메서드
        cleaned_data = super().clean()
        required_fields = [
            'name',
            'description',
            'category',
            'lost_contact',
            'lost_location',
            'lost_date',
            'image',
        ] 

        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, f"{field} 항목은 필수입니다.") 

        if 'is_claimed' not in cleaned_data: #BooleanField 별도 처리
            self.add_error('is_claimed', "처리 여부를 선택해주세요.")

        lost_date = cleaned_data.get('lost_date') #미래 날짜 입력 제한
        if lost_date and lost_date > date.today():
            self.add_error('lost_date', "미래 날짜는 입력할 수 없습니다.")

    def clean_image(self): #다른 형식자의 파일 업로드 불가
        image = self.cleaned_data.get('image')
        if image and not image.content_type.startswith('image/'):
            raise ValidationError("이미지 파일만 업로드할 수 있습니다.")
        return image
    
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
    
    def clean(self): #모든 필드가 입력되었는지 확인해주는 메서드
        cleaned_data = super().clean()
        required_fields = [
            'name',
            'description',
            'category',
            'found_location',
            'image',
            'lat',
            'lng'
        ]

        for field in required_fields:
            if not cleaned_data.get(field):
                self.add_error(field, f"{field} 항목은 필수입니다.")

        if 'is_returned' not in cleaned_data:
            self.add_error('is_returned', "처리 여부를 선택해주세요.")
        
        found_date = cleaned_data.get('found_date')
        if found_date and found_date > date.today():
            self.add_error('found_date', "미래 날짜는 입력할 수 없습니다.")

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image and not image.content_type.startswith('image/'):
            raise ValidationError("이미지 파일만 업로드할 수 있습니다.")
        return image
