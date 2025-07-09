from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    student_id = models.CharField(max_length=20, unique=True)  # 학번
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'student_id'  # 로그인 시 ID로 사용할 필드
    REQUIRED_FIELDS = ['email', 'username']
