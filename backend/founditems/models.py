from django.db import models

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
    CATEGORY_CHOICES = LostItem.CATEGORY_CHOICES  # 같은 선택지 사용

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
