from django.shortcuts import render, redirect, get_object_or_404
from .forms import LostItemForm
from .models import LostItem, FoundItem, Keyword, Notification
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Keyword
import json
from django.contrib.auth.decorators import login_required

@login_required
def register_lost_item(request):
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES)  # 이미지도 받으니까 request.FILES도 필요
        if form.is_valid():
            form.save()  # DB에 저장
            return redirect('meetagain:index')  # 등록 후 메인으로 이동
        else: #폼이 유효하지 않으면 오류 포함된 상태로 다시 렌더링
            return render(request, 'register.html', {'form': form})
    else: 
        form = LostItemForm()
    return render(request, 'register.html', {'form': form})

def index_view(request):
    items = LostItem.objects.all().order_by('-lost_date')

    # 검색어, 위치 필터는 기존과 동일
    q = request.GET.get('q', '')
    location = request.GET.get('location', '')
    category = request.GET.get('category', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if q:
        items = items.filter(name__icontains=q)
    if location:
        items = items.filter(lost_location__icontains=location)
    if category and category != 'all':
        items = items.filter(category=category)
    if date_from:
        items = items.filter(lost_date__gte=date_from)
    if date_to:
        items = items.filter(lost_date__lte=date_to)

    # 최근 분실물 6개만 가져오기
    items = items.order_by('-lost_date')[:6]

    context = {
        'items': items,
        'q': q,
        'location': location,
        'category': category,
        'date_from': date_from,
        'date_to': date_to,
        'category_choices': LostItem.CATEGORY_CHOICES,
    }
    return render(request, 'index.html', context)

def search_view(request):
    qs = LostItem.objects.all()
    category = request.GET.get('category')
    keyword = request.GET.get('q')
    date = request.GET.get('date')  # YYYY-MM-DD

    if category:
        qs = qs.filter(category=category)
    if keyword:
        qs = qs.filter(name__icontains=keyword)
    if date:
        qs = qs.filter(lost_date=date)

    context = {'items': qs}
    return render(request, 'meetagain/search.html', context)

#  지도용 핀 데이터 API
def map_pins_api(request):
    items = LostItem.objects.all()
    data = []

    for item in items:
        data.append({
            'name': item.name,
            'lat': ... ,  # 위도값 추가 필요 (좌표 변환이 안 돼 있으면 대략적인 값)
            'lng': ... ,  # 경도값 추가 필요
            'location': item.lost_location,
            'date': item.lost_date.strftime('%Y-%m-%d'),
        })

    return JsonResponse({'pins': data})

@csrf_exempt

@csrf_exempt
def create_notification(request):
    if request.method == "POST":
        data = json.loads(request.body)
        message = data.get('message')
        keyword_id = data.get('keyword_id')

        if not message:
            return JsonResponse({"error": "No message provided"}, status=400)

        notif = Notification.objects.create(
            message=message,
            keyword_id=keyword_id
        )
        return JsonResponse({"message": "Notification created", "id": notif.id})

@csrf_exempt
def get_notifications(request):
    notifications = Notification.objects.filter(is_read=False).order_by('-created_at')
    data = [{
        "id": n.id,
        "message": n.message,
        "created_at": n.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    } for n in notifications]

    return JsonResponse({"notifications": data})

@login_required
def update_lost_item(request, item_id):
    item = get_object_or_404(LostItem, id=item_id)
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('meetagain:detail', item_id=item.id)  # 수정 후 상세 페이지로 이동
    else:
        form = LostItemForm(instance=item)
    return render(request, 'update_lost_item.html', {'form': form, 'item': item})

@login_required
def delete_lost_item(request, item_id):
    item = get_object_or_404(LostItem, id=item_id)
    if request.method == 'POST':
        item.delete()
        return redirect('meetagain:index')  # 삭제 후 메인으로 이동
    return render(request, 'confirm_delete.html', {'item': item})
