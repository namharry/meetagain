from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'meetagain'

urlpatterns = [
    # ✅ 메인 페이지로 진입하는 URL
    path('', views.index_view, name='index'),
    
    # ✅ 분실물 등록/수정/삭제/상세
    path('lost/register/', views.lost_register_view, name='lost_register'),
    path('lost/<int:item_id>/edit/', views.lost_update_view, name='lost_edit'),
    path('lost/<int:item_id>/delete/', views.lost_delete_view, name='lost_delete'),
    path('lost/<int:item_id>/', views.lost_detail_view, name='lost_detail'),  # 상세 조회 URL 통일

    # ✅ 키워드 관련 API
    path('keywords/add/', views.keyword_add, name='add_keyword'),
    path('keywords/delete/<int:keyword_id>/', views.keyword_delete, name='delete_keyword'),
    path('keywords/', views.keyword_list, name='keyword_list'),

    # ✅ 알림 관련 API
    path('notifications/create/', views.create_notification, name='create_notification'),
    path('notifications/', views.get_notifications, name='get_notifications'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_read_and_redirect, name='read_notification'),

    # ✅ 알림 웹 페이지
    path('notifications/page/', views.notification_list, name='notification_list'),

    # 습득물 관련 URL
    path('found/register/', views.found_register_view, name='found_register'),
    path('found/<int:item_id>/', views.found_detail_view, name='found_detail'),
    path('found/form/', views.found_index_view, name='found_form'),

    # 지도 API
    path('api/items/', views.map_pins_api, name='map_pins_api'),

    # 회원 탈퇴 관련 URL 추가
    path('quit/', views.quit_account_view, name='quit_account'),
    path('quit/done/', views.quit_done_view, name='quit_done'),
]
