from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, student_id, email, password=None, **extra_fields):
        if not student_id:
            raise ValueError('The Student ID must be set')
        email = self.normalize_email(email)
        user = self.model(student_id=student_id, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, student_id, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(student_id, email, password, **extra_fields)


class User(AbstractUser):
    username = None
    student_id = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)

    allow_notification = models.BooleanField(default=True)  # 알림 수신 여부
    allow_location = models.BooleanField(default=True)  # 위치 정보 제공 여부

    USERNAME_FIELD = 'student_id'
    REQUIRED_FIELDS = ['email']

    objects = UserManager()

    def __str__(self):
        return self.student_id
