from django.db import models

class LostItem(models.Model):
    name = models.CharField(max_length=100)        # 물건 이름
    description = models.TextField(blank=True)     # 물건 특징 설명 (공백 가능)
    
    lost_contact = models.CharField(max_length=20, blank=True) # 분실자 연락처
    lost_location = models.CharField(max_length=200)      # 분실 위치
    lost_date = models.DateField()                         # 분실 날짜
    
    found_location = models.CharField(max_length=200)     # 발견 위치
    found_date = models.DateField()                       # 발견 날짜
    
    is_claimed = models.BooleanField(default=False)    # meetagain(소유자 반환) 여부
    image = models.ImageField(upload_to='lost_items/', blank=True, null=True)  # 이미지 파일 저장, 관리하려면 Pillow 라이브러리 필요!!
    
    def __str__(self):
        return self.name

