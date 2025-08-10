# backend/users/urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'users'

urlpatterns = [
    # Auth
    path("signup/", views.signup_view, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("password_change/", views.password_change_view, name="password_change"),
    path("password_reset/", views.custom_password_reset_view, name="password_reset"),

    # AJAX 인증 관련
    path("send-signup-code/", views.send_signup_code_ajax, name="send_signup_code"),
    path("verify-signup-code/", views.verify_signup_code_ajax, name="verify_signup_code"),
    path("verify-reset-code/", views.verify_reset_code_ajax, name="verify_reset_code"),

    # 마이페이지
    path("mypage/", views.mypage_view, name="mypage"),

    # ✅ 설정 업데이트 API (mypage 토글이 호출)
    path("settings/update/", views.update_setting, name="update_setting"),

    # DUMMY/기타 페이지
    path("app_settings/", views.app_settings_view, name="app_settings"),
    path("found_items/", views.found_items_view, name="found_items"),
    path("lost_items/", views.lost_items_view, name="lost_items"),
    path("admin/lost/", views.admin_lost_list, name="admin_lost_list"),
    path("admin/found/", views.admin_found_list, name="admin_found_list"),
]
