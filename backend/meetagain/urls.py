# backend/meetagain/urls.py
from django.urls import path
from . import views

app_name = 'meetagain'

urlpatterns = [
    # 메인
    path('', views.index_view, name='index'),

    # 분실물 (Lost)
    path('lost/register/', views.lost_register_view, name='lost_register'),
    path('lost/<int:item_id>/edit/', views.lost_update_view, name='lost_edit'),
    path('lost/<int:item_id>/delete/', views.lost_delete_view, name='lost_delete'),
    path('lost/<int:item_id>/', views.lost_detail_view, name='lost_detail'),

    # 습득물 (Found)
    path('found/register/', views.found_register_view, name='found_register'),
    path('found/<int:item_id>/', views.found_detail_view, name='found_detail'),
    path('found/', views.found_index_view, name='found_index'),           # ✅ 목록(신규 표준)
    path('found/form/', views.found_index_view, name='found_form'),       # ✅ 호환 유지(예전 이름)

    # 키워드
    path('keywords/', views.keyword_list, name='keyword_list'),
    path('keywords/add/', views.keyword_add, name='add_keyword'),
    path('keywords/delete/<int:keyword_id>/', views.keyword_delete, name='delete_keyword'),

    # 알림(Notification)
    path('notifications/', views.get_notifications, name='get_notifications'),               # JSON
    path('notifications/read/<int:notification_id>/', views.mark_notification_read_and_redirect, name='read_notification'),
    path('notifications/page/', views.notification_list, name='notification_list'),

    # 공지사항(Notice)
    path('notice/', views.notice_list, name='notice_list'),               # ✅ 리스트
    path('notice/create/', views.notice_create, name='notice_create'),
    path('notice/<int:pk>/', views.notice_detail, name='notice_detail'),
    path('notice/<int:pk>/update/', views.notice_update, name='notice_update'),
    path('notice/<int:pk>/delete/', views.notice_delete, name='notice_delete'),

    # 지도 API
    path('api/items/', views.map_pins_api, name='map_pins_api'),

    # 회원 탈퇴
    path('quit/', views.quit_account_view, name='quit_account'),
    path('quit/done/', views.quit_done_view, name='quit_done'),

    # FAQ / 문의
    path('faq/', views.faq_view, name='faq'),

    # 공지사항 관련
    path('notice/', views.notice_view, name='notice'),

    # 문의사항 관련
    path("inquiry/", views.inquiry_view, name="inquiry"),                         # 작성
    path("myinquiries/", views.myinquiries_view, name="myinquiries"),            # 목록
    path("myinquiries/<int:pk>/", views.inquiry_detail_view, name="inquiry_detail"),  # 상세
    path("myinquiries/<int:pk>/edit/", views.inquiry_edit_view, name="inquiry_edit"),  # 수정

    # 관리자 페이지 문의사항 관련
    path('inquiry/', views.inquiry_create, name='inquiry_create'),
    path('inquiry/success/', views.inquiry_success, name='inquiry_success'),
]
