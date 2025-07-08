from django.contrib import admin

from django.contrib import admin
from .models import LostItem

admin.site.register(LostItem)

#관리자 계정 아이디: noname 비번: 123456 이메일: test@example.com
# http://127.0.0.1:8000/admin/ 에서 로그인 후 LostItem 모델을 생성, 수정 가능.