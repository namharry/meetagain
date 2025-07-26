from django.urls import path
from django.contrib.auth import views as auth_views
from .views import signup_view, login_view, password_change_view, dummy_view, admin_found_list, admin_lost_list
from .views import (
    my_account_view,
    app_settings_view,
    found_items_view,
    lost_items_view,
    logout_view,
    quit_view,
    customer_center_view,
    inquiry_view,
    notice_view,
    faq_view,
    guide_view,
)

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/users/login/'), name='logout'),
    path('password_change/', password_change_view, name='password_change'),

    # 비밀번호 재설정 관련 URL
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    #DUMMY URL
    path('my_account/', my_account_view, name='my_account'),
    path('app_settings/', app_settings_view, name='app_settings'),
    path('found_items/', found_items_view, name='found_items'),
    path('lost_items/', lost_items_view, name='lost_items'),
    path('logout/', logout_view, name='logout'),
    path('quit/', quit_view, name='quit'),
    path('customer_center/', customer_center_view, name='customer_center'),
    path('inquiry/', inquiry_view, name='inquiry'),
    path('notice/', notice_view, name='notice'),
    path('faq/', faq_view, name='faq'),
    path('guide/', guide_view, name='guide'),
    path('admin/lost/', admin_lost_list, name='admin_lost_list'),
    path('admin/found/', admin_found_list, name='admin_found_list'),

]


