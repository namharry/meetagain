# founditems/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # 습득물
    path('found/', views.founditem_list),
    path('found/<int:item_id>/', views.founditem_detail),
    path('found/create/', views.founditem_create),  # ✅ 등록

    # 분실물
    path('lost/', views.lostitem_list),
    path('lost/<int:item_id>/', views.lostitem_detail),
    path('lost/create/', views.lostitem_create),
]
