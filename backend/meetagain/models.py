from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.conf import settings

class LostItem(models.Model):
    CATEGORY_CHOICES = [
        ('카드', '카드'),
        ('지갑', '지갑'),
        ('전자기기', '전자기기'),
        ('의류', '의류'),
        ('가방', '가방'),
        ('신발', '신발'),
        ('문서/서류', '문서/서류'),
        ('귀금속', '귀금속'),
        ('악기', '악기'),
        ('책/노트', '책/노트'),
        ('스포츠 용품', '스포츠 용품'),
        ('신분증', '신분증'),
        ('현금', '현금'),
        ('기타', '기타'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='기타')

    lost_contact = models.CharField(max_length=20, blank=True)
    lost_location = models.CharField(max_length=200)
    lost_date = models.DateField()

    is_claimed = models.BooleanField(default=False)
    image = models.ImageField(upload_to='lost_items/', blank=True, null=True)

    def __str__(self):
        return f"[분실물] {self.name}"


class FoundItem(models.Model):
    CATEGORY_CHOICES = [
        ('카드', '카드'),
        ('지갑', '지갑'),
        ('전자기기', '전자기기'),
        ('의류', '의류'),
        ('가방', '가방'),
        ('신발', '신발'),
        ('문서/서류', '문서/서류'),
        ('귀금속', '귀금속'),
        ('악기', '악기'),
        ('책/노트', '책/노트'),
        ('스포츠 용품', '스포츠 용품'),
        ('신분증', '신분증'),
        ('현금', '현금'),
        ('기타', '기타'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='기타')

    found_location = models.CharField(max_length=200)
    found_date = models.DateField()

    is_returned = models.BooleanField(default=False)
    image = models.ImageField(upload_to='found_items/', blank=True, null=True)

    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"[습득물] {self.name}"
    
    
class Keyword(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    word = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user.username} - {self.word}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    # Generic relation to LostItem or FoundItem
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"🔔 {self.user.username} - '{self.keyword}' 매칭 알림"

class Notification(models.Model):
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    # 알림과 관련된 키워드 연결 (옵션)
    keyword = models.ForeignKey('Keyword', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.message
    
    