#meetagain/forms.py

from django import forms
from .models import LostItem, FoundItem, Keyword, Notice, Inquiry
from django.core.exceptions import ValidationError
from datetime import date


class KeywordForm(forms.ModelForm):
    class Meta:
        model = Keyword
        fields = ['word']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')  # 유저 정보를 따로 받아옴
        super().__init__(*args, **kwargs)

    def clean_word(self):
        word = self.cleaned_data['word']
        if Keyword.objects.filter(user=self.user, word=word).exists():
            raise forms.ValidationError("이미 등록한 키워드입니다.")
        return word
        
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
        widgets = {
            'found_date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'placeholder': 'YYYY-MM-DD',
                }
            )
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['found_date'].input_formats = ['%Y-%m-%d']
    
    def clean(self): #모든 필드가 입력되었는지 확인해주는 메서드
        cleaned_data = super().clean()
        required_fields = [
            'name',
            'description',
            'category',
            'found_location',
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

class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ['title', 'content']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 10}),
        }

class InquiryForm(forms.ModelForm):
    class Meta:
        model = Inquiry
        fields = ['subject', 'category', 'content']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'content': forms.Textarea(attrs={'class': 'form-control'}),
        }
