from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import FoundItem, LostItem
from .forms import FoundItemForm
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime
import json

# --------------------
# ✅ 습득물 (FoundItem)
# --------------------

# 전체 조회
def founditem_list(request):
    items = FoundItem.objects.all().values()
    return JsonResponse(list(items), safe=False)

# 상세 조회
@login_required
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

# 등록 (POST, API 용)
@csrf_exempt
def founditem_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': '입력 데이터 형식이 올바르지 않습니다.'}, status=400)

        try:
            lat = float(data.get('lat')) if data.get('lat') is not None else None
            lng = float(data.get('lng')) if data.get('lng') is not None else None
        except ValueError:
            return JsonResponse({'error': '위치 좌표 값이 잘못되었습니다.'}, status=400)

        # ✅ 날짜 형식 검증 및 변환
        try:
            found_date_str = data.get('found_date')
            found_date = datetime.strptime(found_date_str, '%Y-%m-%d').date() if found_date_str else None
        except ValueError:
            return JsonResponse({'error': '날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식이어야 합니다.'}, status=400)

        item = FoundItem.objects.create(
            name=data.get('name'),
            description=data.get('description', ''),
            category=data.get('category', '기타'),
            found_location=data.get('found_location'),
            found_date=found_date,
            lat=lat,
            lng=lng,
            is_returned=False,
        )

        return JsonResponse({'id': item.id, 'message': '습득물 등록이 완료되었습니다.'}, status=201)

    return JsonResponse({'error': 'POST 요청만 허용됩니다.'}, status=400)

# 관리자용 지도 핀
@staff_member_required
def map_pins_api(request):
    items = FoundItem.objects.filter(
        is_returned=False,
        lat__isnull=False,
        lng__isnull=False
    )

    data = [
        {
            'id': item.id,
            'title': item.name,
            'lat': item.lat,
            'lng': item.lng,
            'status': '미반환' if not item.is_returned else '반환됨',
        }
        for item in items
    ]

    return JsonResponse(data, safe=False)

# --------------------
# ✅ 분실물 (LostItem)
# --------------------

# 전체 조회
def lostitem_list(request):
    items = LostItem.objects.all().values()
    return JsonResponse(list(items), safe=False)

# 상세 조회
@login_required
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

# 등록 (POST, API용)
@login_required
@csrf_exempt
def lostitem_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': '입력 데이터 형식이 올바르지 않습니다.'}, status=400)

        try:
            lost_date_str = data.get('lost_date')
            lost_date = datetime.strptime(lost_date_str, '%Y-%m-%d').date() if lost_date_str else None
        except ValueError:
            return JsonResponse({'error': '날짜 형식이 잘못되었습니다. YYYY-MM-DD 형식이어야 합니다.'}, status=400)

        item = LostItem.objects.create(
            name=data.get('name'),
            description=data.get('description', ''),
            category=data.get('category', '기타'),
            lost_location=data.get('lost_location'),
            lost_date=lost_date,
            lost_contact=data.get('lost_contact', ''),
            is_claimed=False,
        )

        return JsonResponse({'id': item.id, 'message': '분실물 등록이 완료되었습니다.'}, status=201)

    return JsonResponse({'error': 'POST 요청만 허용됩니다.'}, status=400)

# 습득물 등록 HTML 폼 뷰
@login_required
def founditem_form_view(request):
    if request.method == 'POST':
        form = FoundItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.lat = request.POST.get('lat')
            item.lng = request.POST.get('lng')
            item.save()
            return render(request, 'found_item_success.html')  # 성공 페이지
    else:
        form = FoundItemForm()

    return render(request, 'users/found_items_form.html', {'form': form})
