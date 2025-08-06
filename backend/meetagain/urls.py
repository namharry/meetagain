from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'meetagain'

urlpatterns = [
    # ✅ 분실물 등록/수정/삭제/상세
    path('register/', views.register_lost_item, name='register'),
    path('item/<int:item_id>/edit/', views.update_lost_item, name='edit'),
    path('item/<int:item_id>/delete/', views.delete_lost_item, name='delete'),
    path('item/<int:item_id>/', views.detail_view, name='detail'),
    path('found/create/', views.founditem_create_view, name='founditem_create'),

    # ✅ 키워드 관련 API
    path('keywords/add/', views.add_keyword, name='add_keyword'),
    path('keywords/delete/<int:keyword_id>/', views.delete_keyword, name='delete_keyword'),  # ⬅️ 수정됨
    path('keywords/', views.keyword_list, name='keyword_list'),

    # ✅ 알림 관련 API
    path('notifications/create/', views.create_notification, name='create_notification'),
    path('notifications/', views.get_notifications, name='get_notifications'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_read_and_redirect, name='read_notification'),

    # ✅ 알림 웹 페이지
    path('notifications/page/', views.notification_list, name='notification_list'),

    # ✅ FoundItem 상세 보기
    path('found/<int:item_id>/', views.founditem_detail, name='founditem_detail'),

]
