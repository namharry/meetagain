from django.urls import path
from . import views

app_name = 'meetagain'

urlpatterns = [
    # ✅ 메인 페이지
    path('', views.index_view, name='index'),

    # ✅ 분실물 등록/수정/삭제/상세
    path('register/', views.register_lost_item, name='register'),
    path('item/<int:item_id>/edit/', views.update_lost_item, name='edit'),
    path('item/<int:item_id>/delete/', views.delete_lost_item, name='delete'),
    path('item/<int:item_id>/', views.detail_view, name='detail'),

    # ✅ 지도용 좌표 API
    path('api/map-pins/', views.map_pins_api, name='map-pins'),

    # ✅ 키워드 관련 API
    path('keywords/add/', views.add_keyword, name='add_keyword'),
    path('keywords/delete/', views.delete_keyword, name='delete_keyword'),
    path('keywords/', views.keyword_list, name='keyword_list'),

    # ✅ 알림 관련 API
    path('notifications/create/', views.create_notification, name='create_notification'),
    path('notifications/', views.get_notifications, name='get_notifications'),

    # ✅ 알림 웹 페이지
    path('notifications/page/', views.notification_list, name='notification_list'),
]
