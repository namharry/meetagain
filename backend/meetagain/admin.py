from django.contrib import admin
from .models import LostItem, FoundItem, Notice

admin.site.register(LostItem)

#관리자 계정 아이디: 12345678 비번: 123456 이메일: test@example.com
# http://127.0.0.1:8000/admin/ 에서 로그인 후 LostItem, FoundItem 모델을 생성, 수정 가능.

@admin.register(FoundItem)
class FoundItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name','status', 'found_location', 'found_date')
    list_editable = ('status',)
    list_filter = ('status', 'found_date')
    search_fields = ('name', 'found_location')

@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'author__username')
    list_filter = ('created_at', 'updated_at')
