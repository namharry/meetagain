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

# 고정 선택지
LOCATION_CHOICES = [
    ('난향관','난향관'), ('성신관','성신관'), ('수정관','수정관'),
    ('중앙도서관','중앙도서관'), ('조형1관','조형1관'), ('조형2관','조형2관'),
    ('체육관','체육관'), ('프라임관','프라임관'), ('행정관','행정관'),
    ('학생회관','학생회관'), ('음악관','음악관'), ('기타','기타'),
]

class LostItemForm(forms.ModelForm):

    lost_locations = forms.MultipleChoiceField(
        choices=LOCATION_CHOICES,
        required=True,
        widget=forms.SelectMultiple(attrs={
            "class": "form-select",
            "id": "lost_locations",
        }),
        label="분실 장소(복수 선택 가능)"
    )

    class Meta:
        model = LostItem
        fields = [
            'name',
            'description',
            'category',
            'lost_locations',
            'lost_date_start',
            'lost_date_end',
            'is_claimed',
            'image'
        ]
        widgets = {
            'lost_date_start': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'placeholder': 'YYYY-MM-DD',
                }
            ),
            'lost_date_end': forms.DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control',
                    'placeholder': 'YYYY-MM-DD',
                }
            ),
        }
    
    def clean(self): #모든 필드가 입력되었는지 확인해주는 메서드
        cleaned_data = super().clean()

        required_fields = [
            'name',
            'category',
            'lost_locations',
            'lost_date_start',
            'lost_date_end',
        ] 

        for field in required_fields:
            value = cleaned_data.get(field)
            if value in (None, ''):
                self.add_error(field, f"{self.fields[field].label or field} 항목은 필수입니다.")

        locations = cleaned_data.get('lost_locations', [])
        if not locations or (isinstance(locations, (list, tuple)) and len(locations) == 0):
            self.add_error('lost_locations', "분실 장소는 최소 1개 이상 선택하세요.")
        else:
            # 공백 제거 등 정리
            cleaned_data['lost_locations'] = [s.strip() for s in locations if s and s.strip()]

         # 날짜 교차 검증
        start = cleaned_data.get('lost_date_start')
        end = cleaned_data.get('lost_date_end')
        today = date.today()

        if start and start > today:
            self.add_error('lost_date_start', "미래 날짜는 입력할 수 없습니다.")
        if end and end > today:
            self.add_error('lost_date_end', "미래 날짜는 입력할 수 없습니다.")
        if start and end and start > end:
            self.add_error('lost_date_end', "분실 종료일은 시작일보다 빠를 수 없습니다.")

        return cleaned_data

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            return image

    # content_type 속성 안전하게 접근
        content_type = getattr(image, 'content_type', None)
        if content_type and not content_type.startswith('image/'):
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
            'category',
            'found_location',
            'found_date',
            'lat',
            'lng'
        ]

        for field in required_fields:
            value = cleaned_data.get(field)
            if value in (None, ''):
                self.add_error(field, f"{self.fields[field].label or field} 항목은 필수입니다.")
        
        found_date = cleaned_data.get('found_date')
        if found_date and found_date > date.today():
            self.add_error('found_date', "미래 날짜는 입력할 수 없습니다.")
        
        # 위경도 범위 검사
        lat = cleaned_data.get('lat')
        lng = cleaned_data.get('lng')
        try:
            if not (-90.0 <= float(lat) <= 90.0):
                self.add_error('lat', "위도(lat)는 -90 ~ 90 범위여야 합니다.")
        except (TypeError, ValueError):
            self.add_error('lat', "위도(lat)는 숫자여야 합니다.")
        
        try:
            if not (-180.0 <= float(lng) <= 180.0):
                self.add_error('lng', "경도(lng)는 -180 ~ 180 범위여야 합니다.")
        except (TypeError, ValueError):
            self.add_error('lng', "경도(lng)는 숫자여야 합니다.")

        return cleaned_data

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            return image

        content_type = getattr(image, 'content_type', None)
        if content_type and not content_type.startswith('image/'):
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
