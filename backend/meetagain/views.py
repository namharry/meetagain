from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import logout, authenticate
from datetime import datetime
import json
from .models import LostItem, FoundItem, Keyword, Notification, Notice
from .forms import LostItemForm, FoundItemForm
from users.forms import SignupForm

# staff_member_required를 직접 정의
def staff_member_required(view_func):
    """
    사용자 객체가 staff인지를 확인하는 데코레이터
    """
    return user_passes_test(lambda u: u.is_staff)(view_func)


# 메인 홈 화면용 뷰
def index_view(request):
    return render(request, 'pages/index.html')


# --------------------
# 분실물 (LostItem) 뷰
# --------------------

@login_required
def lost_register_view(request):
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('meetagain:lost_index')
        else:
            return render(request, 'lost/lost_register.html', {'form': form})
    else:
        form = LostItemForm()
    return render(request, 'lost/lost_register.html', {'form': form})

@login_required
def lost_index_view(request):
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
    return render(request, 'lost/lost_list.html', context)

@login_required
def lost_update_view(request, item_id):
    item = get_object_or_404(LostItem, id=item_id)
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('meetagain:lost_detail', item_id=item.id)
    else:
        form = LostItemForm(instance=item)
    return render(request, 'lost/lost_update.html', {'form': form, 'item': item})

@login_required
def lost_delete_view(request, item_id):
    item = get_object_or_404(LostItem, id=item_id)
    if request.method == 'POST':
        item.delete()
        return redirect('meetagain:lost_index')
    return render(request, 'lost/confirm_delete.html', {'item': item})

@login_required
def lost_detail_view(request, item_id):
    item = get_object_or_404(LostItem, id=item_id)
    context = {'item': item}
    return render(request, 'lost/lost_detail.html', context)


# --------------------
# 습득물 (FoundItem) 뷰
# --------------------

@login_required
def found_register_view(request):
    if request.method == 'POST':
        form = FoundItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('meetagain:found_index')
        else:
            return render(request, 'found/found_register.html', {'form': form})
    else:
        form = FoundItemForm()
    return render(request, 'found/found_register.html', {'form': form})

@login_required
def found_index_view(request):
    items = FoundItem.objects.all().order_by('-found_date')

    q = request.GET.get('q', '')
    location = request.GET.get('location', '')
    category = request.GET.get('category', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if q:
        items = items.filter(name__icontains=q)
    if location:
        items = items.filter(found_location__icontains=location)
    if category and category != 'all':
        items = items.filter(category=category)
    if date_from:
        items = items.filter(found_date__gte=date_from)
    if date_to:
        items = items.filter(found_date__lte=date_to)

    items = items.order_by('-found_date')[:6]

    context = {
        'items': items,
        'q': q,
        'location': location,
        'category': category,
        'date_from': date_from,
        'date_to': date_to,
        'category_choices': FoundItem.CATEGORY_CHOICES,
    }
    return render(request, 'found/found_index.html', context)

@login_required
def found_update_view(request, item_id):
    item = get_object_or_404(FoundItem, id=item_id)
    if request.method == 'POST':
        form = FoundItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('meetagain:found_detail', item_id=item.id)
    else:
        form = FoundItemForm(instance=item)
    return render(request, 'found/found_update.html', {'form': form, 'item': item})

@login_required
def found_delete_view(request, item_id):
    item = get_object_or_404(FoundItem, id=item_id)
    if request.method == 'POST':
        item.delete()
        return redirect('meetagain:found_index')
    return render(request, 'found/confirm_delete.html', {'item': item})

@login_required
def found_detail_view(request, item_id):
    item = get_object_or_404(FoundItem, id=item_id)
    context = {'item': item}
    return render(request, 'found/found_detail.html', context)


# --------------------
# 키워드 관련 뷰
# --------------------

# views.py (키워드 관련)
@login_required
def keyword_list(request):
    keywords = Keyword.objects.filter(user=request.user)
    return render(request, 'keywords/keyword_list.html', {'keywords': keywords})

@require_POST
@login_required
def keyword_add(request):
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
@login_required
def keyword_delete(request, keyword_id):
    keyword = Keyword.objects.filter(id=keyword_id, user=request.user).first()
    if keyword:
        messages.success(request, f"'{keyword.word}' 키워드가 삭제되었습니다.")
        keyword.delete()
    else:
        messages.error(request, "해당 키워드를 찾을 수 없습니다.")
    return redirect('meetagain:keyword_list')



# --------------------
# 사용자 키워드 알림(Notification) 관련 뷰
# --------------------

@login_required
def create_notification(request):
    # 실제 구현은 필요에 따라 작성하세요. 예시로 빈 응답 반환
    return JsonResponse({'message': 'Notification created (dummy response)'})


@login_required
def get_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    data = []
    for n in notifications:
        data.append({
            'id': n.id,
            'keyword': n.keyword,
            'content_type': n.content_type.model,
            'object_id': n.object_id,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),
        })
    return JsonResponse({'notifications': data})


@login_required
def mark_notification_read_and_redirect(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    #notification.read_at = datetime.now()
    notification.save()

    # 알림 클릭 후 이동할 URL 예: 상세 페이지로 이동하도록 수정 가능
    # 여기서는 임시로 메인 페이지로 리다이렉트
    return redirect('meetagain:index')


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'pages/notification_list.html', {'notifications': notifications})

# --------------------
# 공지사항 관련 뷰(관리자만 접근 가능)
# --------------------

def notice_list(request):
    # 모든 사용자 공지사항 목록 조회, 최신순
    notices = Notice.objects.order_by('-created_at')
    return render(request, 'notice/notice_list.html', {'notices': notices})

def notice_detail(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    return render(request, 'notice/notice_detail.html', {'notice': notice})

# 관리자 권한 체크용 데코레이터
def staff_required(view_func):
    decorated_view_func = login_required(user_passes_test(lambda u: u.is_staff)(view_func))
    return decorated_view_func

@staff_required
def notice_create(request):
    if request.method == 'POST':
        form = NoticeForm(request.POST)
        if form.is_valid():
            notice = form.save(commit=False)
            notice.author = request.user
            notice.save()
            messages.success(request, '공지사항이 성공적으로 등록되었습니다.')
            return redirect('notice_detail', pk=notice.pk)
    else:
        form = NoticeForm()
    return render(request, 'notice/notice_form.html', {'form': form})

@staff_required
def notice_update(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if request.method == 'POST':
        form = NoticeForm(request.POST, instance=notice)
        if form.is_valid():
            form.save()
            messages.success(request, '공지사항이 성공적으로 수정되었습니다.')
            return redirect('notice_detail', pk=notice.pk)
    else:
        form = NoticeForm(instance=notice)
    return render(request, 'notice/notice_form.html', {'form': form})

@staff_required
def notice_delete(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    if request.method == 'POST':
        notice.delete()
        messages.success(request, '공지사항이 삭제되었습니다.')
        return redirect('notice_list')
    return render(request, 'notice/notice_confirm_delete.html', {'notice': notice})


# --------------------
# 지도 API (map pins) 관련 뷰
# --------------------

@login_required
def map_pins_api(request):
    # 분실물 + 습득물 위치 좌표 데이터 JSON 반환 예시 (실제 위치 필드명 맞춰서 수정하세요)
    lost_items = LostItem.objects.all()
    found_items = FoundItem.objects.all()

    data = []

    for item in lost_items:
        data.append({
            'id': item.id,
            'type': 'lost',
            'name': item.name,
            'lat': item.latitude,    # 예: 위도 필드명
            'lng': item.longitude,   # 예: 경도 필드명
            'date': item.lost_date.strftime('%Y-%m-%d'),
        })

    for item in found_items:
        data.append({
            'id': item.id,
            'type': 'found',
            'name': item.name,
            'lat': item.latitude,    # 예: 위도 필드명
            'lng': item.longitude,   # 예: 경도 필드명
            'date': item.found_date.strftime('%Y-%m-%d'),
        })

    return JsonResponse({'items': data})


# --------------------
# 회원 탈퇴(quit) 관련 뷰 추가 시작
# --------------------

@login_required
def quit_account_view(request):
    """
    GET: 탈퇴 동의 및 비밀번호 입력 화면 표시
    POST: 비밀번호 확인 후 회원 탈퇴 처리
    """
    if request.method == 'POST':
        password = request.POST.get('password', '')
        agree = request.POST.get('agree')

        if not agree:
            messages.error(request, "탈퇴 동의에 체크해주세요.")
            return render(request, 'quit/quit.html')

        user = request.user

        # 비밀번호 확인
        if not user.check_password(password):
            messages.error(request, "비밀번호가 올바르지 않습니다.")
            return render(request, 'quit/quit.html')

        # 회원 탈퇴 처리
        user.delete()

        # 로그아웃 처리
        logout(request)

        # 탈퇴 완료 페이지로 이동
        return redirect('meetagain:quit_done')

    else:
        return render(request, 'quit/quit.html')


@login_required
def quit_done_view(request):
    """
    탈퇴 완료 페이지 표시
    """
    return render(request, 'quit/quit_done.html')

