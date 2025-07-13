from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    username = None #username은 항상 django에 기본적으로 포함. 학번으로 대체할 경우 username을 명시적으로 없애야함.
    student_id = models.CharField(max_length=20, unique=True)  # 학번
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'student_id'  # 로그인 시 ID로 사용할 필드
    REQUIRED_FIELDS = ['email']
