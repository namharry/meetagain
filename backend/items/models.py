from django.db import models

class LostItem(models.Model):
    # 필드 정의
    name = models.CharField(max_length=100)
    # 기타 필드...

class FoundItem(models.Model):
    # 필드 정의
    name = models.CharField(max_length=100)
    # 기타 필드...
