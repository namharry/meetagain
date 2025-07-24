from django.urls import path
from . import views

app_name = 'meetagain'

urlpatterns = [
    path('', views.index_view, name='index'),  # ✅ 메인 페이지 (검색 리스트)
    path('register/', views.register_lost_item, name='register'),  # ✅ 등록 페이지

    # 🔧 수정/삭제 관련 경로
    path('item/<int:item_id>/edit/', views.update_lost_item, name='edit'),  # ✏️ 수정
    path('item/<int:item_id>/delete/', views.delete_lost_item, name='delete'),  # 🗑 삭제
    path('item/<int:item_id>/', views.detail_view, name='detail'),  # 🔍 상세보기 (선택사항)

    # ✅ 지도용 좌표 API
    path('api/map-pins/', views.map_pins_api, name='map-pins'),

    # ✅ 키워드 관련 API
    path('keywords/add/', views.add_keyword, name='add_keyword'),
    path('keywords/delete/', views.delete_keyword, name='delete_keyword'),
    path('keywords/', views.keyword_list, name='keyword_list'),

    # ✅ 알림 관련 API
    path('notifications/create/', views.create_notification, name='create_notification'),
    path('notifications/', views.get_notifications, name='get_notifications'),
]
