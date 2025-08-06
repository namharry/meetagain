from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType

from .models import LostItem, FoundItem, Keyword, Notification
from .forms import LostItemForm
from users.forms import SignupForm

import json

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

@login_required
def index_view(request):
    print("Index view called")  # 디버깅용 로그
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
    return render(request, 'pages/index.html', context)

def founditem_create_view(request):
    return render(request, 'found/found_register.html')

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

@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications
    })

def detail_view(request, item_id):
    item = get_object_or_404(LostItem, id=item_id)
    context = {
        'item': item,
    }
    return render(request, 'meetagain/detail.html', context)

@require_POST
def add_keyword(request):
    word = request.POST.get('word', '').strip()
    
    if not word:
        messages.error(request, "키워드를 입력해주세요.")
        return redirect('meetagain:keyword_list')

    # 중복 키워드 방지
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
def keyword_list(request):
    keywords = Keyword.objects.filter(user=request.user)
    return render(request, 'keywords/keyword_list.html', {
        'keywords': keywords
    })

def founditem_detail(request, item_id):
    item = get_object_or_404(FoundItem, id=item_id)
    return render(request, 'found/founditem_detail.html', {'item': item})

def mark_notification_read_and_redirect(request, notification_id):
    notification = Notification.objects.filter(id=notification_id, user=request.user).first()
    
    if notification:
        # 읽음 처리
        notification.is_read = True
        notification.save()

        # 연결된 아이템으로 리디렉트
        if notification.item:
            model_name = notification.content_type.model
            if model_name == "founditem":
                return redirect('meetagain:founditem_detail', item_id=notification.item.id)
            elif model_name == "lostitem":
                return redirect('meetagain:detail', item_id=notification.item.id)
    
    # 예외 처리 → 홈으로
    return redirect('meetagain:index')