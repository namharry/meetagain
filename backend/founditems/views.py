from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import FoundItem, LostItem
import json

# --------------------
# ✅ 습득물 (FoundItem)
# --------------------

# 전체 조회
def founditem_list(request):
    items = FoundItem.objects.all().values()
    return JsonResponse(list(items), safe=False)

# 상세 조회
def founditem_detail(request, item_id):
    item = get_object_or_404(FoundItem, id=item_id)
    return JsonResponse({
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'category': item.category,
        'found_location': item.found_location,
        'found_date': item.found_date,
        'image': item.image.url if item.image else None,
        'lat': item.lat,
        'lng': item.lng,
        'is_returned': item.is_returned,
    })

# 등록 (POST)
@csrf_exempt
def founditem_create(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        item = FoundItem.objects.create(
            name=data.get('name'),
            description=data.get('description', ''),
            category=data.get('category', '기타'),
            found_location=data.get('found_location'),
            found_date=data.get('found_date'),
            lat=data.get('lat'),
            lng=data.get('lng'),
            is_returned=False,
        )

        return JsonResponse({'id': item.id, 'message': '습득물 등록 완료!'}, status=201)

    return JsonResponse({'error': 'POST 요청만 허용됩니다'}, status=400)

# --------------------
# ✅ 분실물 (LostItem)
# --------------------

# 전체 조회
def lostitem_list(request):
    items = LostItem.objects.all().values()
    return JsonResponse(list(items), safe=False)

# 상세 조회
def lostitem_detail(request, item_id):
    item = get_object_or_404(LostItem, id=item_id)
    return JsonResponse({
        'id': item.id,
        'name': item.name,
        'description': item.description,
        'category': item.category,
        'lost_location': item.lost_location,
        'lost_date': item.lost_date,
        'lost_contact': item.lost_contact,
        'image': item.image.url if item.image else None,
        'is_claimed': item.is_claimed,
    })

@csrf_exempt
def lostitem_create(request):
    if request.method == 'POST':
        data = json.loads(request.body)

        item = LostItem.objects.create(
            name=data.get('name'),
            description=data.get('description', ''),
            category=data.get('category', '기타'),
            lost_location=data.get('lost_location'),
            lost_date=data.get('lost_date'),
            lost_contact=data.get('lost_contact', ''),
            is_claimed=False,
        )

        return JsonResponse({'id': item.id, 'message': '분실물 등록 완료!'}, status=201)

    return JsonResponse({'error': 'POST 요청만 허용됩니다'}, status=400)
