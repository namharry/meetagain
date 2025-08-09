from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'meetagain'

urlpatterns = [
    # ✅ 메인 페이지로 진입하는 URL
    path('', views.index_view, name='index'),
    
    # ✅ 분실물 등록/수정/삭제/상세
    path('register/', views.register_lost_item, name='register'),
    path('item/<int:item_id>/edit/', views.update_lost_item, name='edit'),
    path('item/<int:item_id>/delete/', views.delete_lost_item, name='delete'),
    path('item/<int:item_id>/', views.detail_view, name='detail'),
   

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

    # 습득물
    path('found/', views.founditem_list),
    path('found/<int:item_id>/', views.founditem_detail, name='found_detail'),
    path('found/form/', views.founditem_form_view, name='founditem_form'),

    # 분실물
    path('lost/', views.lostitem_list),
    path('lost/<int:item_id>/', views.lostitem_detail),
    path('lost/create/', views.lostitem_create),

    path('api/items/', views.map_pins_api, name='map_pins_api'),
]

#분실물 item인지 lost인지 통일 필요
