from django.urls import path
from . import views

app_name = 'meetagain'

urlpatterns = [
    path('', views.index_view, name='index'),  # ✅ 메인 페이지 (검색 리스트)
    path('register/', views.register_lost_item, name='register'),  # ✅ 등록 페이지
    path('api/map-pins/', views.map_pins_api, name='map-pins'),  # ✅ 지도용 좌표 API
]