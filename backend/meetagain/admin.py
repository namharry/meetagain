from django.contrib import admin
from .models import LostItem, FoundItem, Notice, Inquiry, Keyword, Notification

# LostItem
@admin.register(LostItem)
class LostItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'lost_location', 'lost_date_start', 'lost_date_end')
    list_filter = ('lost_date_start', 'lost_date_end')
    search_fields = ('name', 'lost_location')

# FoundItem
@admin.register(FoundItem)
class FoundItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'found_location', 'found_date')
    list_editable = ('status',)
    list_filter = ('status', 'found_date')
    search_fields = ('name', 'found_location')

# Notice
@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at')
    search_fields = ('title', 'content', 'author__student_id')
    list_filter = ('created_at', 'updated_at')

# Inquiry
@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'subject', 'created_at', 'status', 'response')
    list_display_links = ('subject',)  # subject 필드 클릭 가능하도록 설정
    list_filter = ('status', 'created_at')
    search_fields = ('subject', 'content', 'user__student_id')
    fields = ('user', 'subject', 'category', 'content', 'created_at', 'status', 'response')
    readonly_fields = ('created_at',)

    def save_model(self, request, obj, form, change):
        if obj.response and obj.status != 'answered':
            obj.status = 'answered'  # 답변이 있으면 상태 자동 변경
        super().save_model(request, obj, form, change)

# Keyword
@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'word')
    search_fields = ('word', 'user__student_id')
    list_filter = ('user',)

# Notification
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'keyword', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('keyword', 'user__student_id')