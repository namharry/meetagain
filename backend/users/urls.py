from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
     path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path('logout/', views.logout_view, name='logout'),
    path('password_change/', views.password_change_view, name='password_change'),
    path('password_reset/', views.custom_password_reset_view, name='password_reset'),

    # ✅ AJAX 인증 관련 추가
    path('send-signup-code/', views.send_signup_code_ajax, name='send_signup_code'),
    path('verify-signup-code/', views.verify_signup_code_ajax, name='verify_signup_code'),
    path('verify-reset-code/', views.verify_reset_code_ajax, name='verify_reset_code'),

    # DUMMY
    path('my_account/', views.my_account_view, name='my_account'),
    path('app_settings/', views.app_settings_view, name='app_settings'),
    path('found_items/', views.found_items_view, name='found_items'),
    path('lost_items/', views.lost_items_view, name='lost_items'),
    path('quit/', views.quit_view, name='quit'),
    path('customer_center/', views.customer_center_view, name='customer_center'),
    path('inquiry/', views.inquiry_view, name='inquiry'),
    path('notice/', views.notice_view, name='notice'),
    path('faq/', views.faq_view, name='faq'),
    path('guide/', views.guide_view, name='guide'),
    path('admin/lost/', views.admin_lost_list, name='admin_lost_list'),
    path('admin/found/', views.admin_found_list, name='admin_found_list'),
]
