from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from datetime import datetime
import json

from .models import LostItem, FoundItem, Keyword, Notification
from .forms import LostItemForm, FoundItemForm
from users.forms import SignupForm

# --------------------
# 분실물 (LostItem) 및 메인 뷰 (meetagain 쪽 중복 선택)
# --------------------

@login_required
def register_lost_item(request):
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('meetagain:index')
        else:
            return render(request, 'register.html', {'form': form})
    else:
        form = LostItemForm()
    return render(request, 'register.html', {'form': form})

@login_required
def index_view(request):
    print("Index view called")
    items = LostItem.objects.all().order_by('-lost_date')

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
    return render(request, 'pages/index.html', context)

def search_view(request):
    qs = LostItem.objects.all()
    category = request.GET.get('category')
    keyword = request.GET.get('q')
    date = request.GET.get('date')

    if category:
        qs = qs.filter(category=category)
    if keyword:
        qs = qs.filter(name__icontains=keyword)
    if date:
        qs = qs.filter(lost_date=date)

    context = {'items': qs}
    return render(request, 'meetagain/search.html', context)

@login_required
def update_lost_item(request, item_id):
    item = get_object_or_404(LostItem, id=item_id)
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('meetagain:detail', item_id=item.id)
    else:
        form = LostItemForm(instance=item)
    return render(request, 'update_lost_item.html', {'form': form, 'item': item})

@login_required
def delete_lost_item(request, item_id):
    item = get_object_or_404(LostItem, id=item_id)
    if request.method == 'POST':
        item.delete()
        return redirect('meetagain:index')
    return render(request, 'confirm_delete.html', {'item': item})

@login_required
def keyword_list(request):
    keywords = Keyword.objects.filter(user=request.user)
    return render(request, 'keywords/keyword_list.html', {'keywords': keywords})

@require_POST
def add_keyword(request):
    word = request.POST.get('word', '').strip()

    if not word:
        messages.error(request, "키워드를 입력해주세요.")
        return redirect('meetagain:keyword_list')

    keyword, created = Keyword.objects.get_or_create(user=request.user, word=word)

    if created:
        messages.success(request, f"'{word}' 키워드가 등록되었습니다.")
    else:
        messages.info(request, f"이미 '{word}' 키워드를 등록하셨습니다.")

    return redirect('meetagain:keyword_list')

@require_POST
def delete_keyword(request, keyword_id):
    keyword = Keyword.objects.filter(id=keyword_id, user=request.user).first()
    if keyword:
        messages.success(request, f"'{keyword.word}' 키워드가 삭제되었습니다.")
        keyword.delete()
    else:
        messages.error(request, "해당 키워드를 찾을 수 없습니다.")
    return redirect('meetagain:keyword_list')

@login_required
def detail_view(request, item_id):
    item = get_object_or_404(LostItem, id=item_id)
    context = {'item': item}
    return render(request, 'meetagain/detail.html', context)

# --------------------
# 습득물 (FoundItem) 관련 뷰 (추가된 것들 모두 유지)
# --------------------

def founditem_list(request):
    items = FoundItem.objects.all().values()
    return JsonResponse(list(items), safe=False)

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

@staff_member_required
def map_pins_api(request):
    items = FoundItem.objects.filter(
        is_returned=False,
        lat__isnull=False,
        lng__isnull=False
    )
    data = [{
        'id': item.id,
        'title': item.name,
        'lat': item.lat,
        'lng': item.lng,
        'status': '미반환' if not item.is_returned else '반환됨',
    } for item in items]
    return JsonResponse(data, safe=False)

@login_required
def founditem_form_view(request):
    if request.method == 'POST':
        form = FoundItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.lat = request.POST.get('lat')
            item.lng = request.POST.get('lng')
            item.save()
            return render(request, 'found_item_success.html')
    else:
        form = FoundItemForm()
    return render(request, 'users/found_items_form.html', {'form': form})

# --------------------
# 알림(Notification) 관련 뷰
# --------------------

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
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications/notification_list.html', {'notifications': notifications})

@login_required
def mark_notification_read_and_redirect(request, notification_id):
    notification = Notification.objects.filter(id=notification_id, user=request.user).first()

    if notification:
        notification.is_read = True
        notification.save()

        if notification.item:
            model_name = notification.content_type.model
            if model_name == "founditem":
                return redirect('meetagain:founditem_detail', item_id=notification.item.id)
            elif model_name == "lostitem":
                return redirect('meetagain:detail', item_id=notification.item.id)
        else:
            return redirect('meetagain:notification_list')

    return redirect('meetagain:notification_list')

def lostitem_list(request):
    items = LostItem.objects.all()  # 모든 분실물 항목을 가져옴
    return render(request, 'meetagain/lostitem_list.html', {'items': items})

def lostitem_detail(request, item_id):
    # `item_id`에 해당하는 `LostItem` 객체를 가져옴
    item = get_object_or_404(LostItem, id=item_id)
    # 해당 항목을 템플릿으로 전달
    return render(request, 'meetagain/lostitem_detail.html', {'item': item})

@login_required
def lostitem_create(request):
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('meetagain:index')  # 분실물 등록 후 메인 페이지로 리디렉션
    else:
        form = LostItemForm()  # GET 요청이면 빈 폼을 렌더링

    return render(request, 'meetagain/lostitem_create.html', {'form': form})