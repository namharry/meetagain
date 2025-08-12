# backend/meetagain/views.py
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

from .models import Inquiry, LostItem, FoundItem, Keyword, Notification, Notice
from .forms import InquiryForm, LostItemForm, FoundItemForm, NoticeForm
from users.forms import SignupForm
from django.contrib.auth.decorators import login_required
from .models import Notification

# staff_member_required를 직접 정의
def staff_member_required(view_func):
    """
    사용자 객체가 staff인지를 확인하는 데코레이터
    """
    return user_passes_test(lambda u: u.is_staff)(view_func)


# 메인 홈 화면용 뷰
def index_view(request):
    # 검색 파라미터 가져오기
    category = request.GET.get('category')
    name = request.GET.get('name')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    location = request.GET.get('location')

    # 기본 쿼리셋
    items = FoundItem.objects.all()

    # 필터 조건 적용
    if category:
        items = items.filter(category=category)
    if name:
        items = items.filter(name__icontains=name)
    if start_date:
        items = items.filter(found_date__gte=start_date)
    if end_date:
        items = items.filter(found_date__lte=end_date)
    if location:
        items = items.filter(found_location__icontains=location)  # 부분 검색 가능

    # 최신순 정렬
    items = items.order_by('-found_date')

    return render(request, 'pages/index.html', {
        'items': items
    })



# --------------------
# 분실물 (LostItem) 뷰
# --------------------

@login_required
def lost_register_view(request):
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save()
            # 저장 후 상세 페이지로 이동(안전)
            return redirect('meetagain:lost_detail', item_id=item.id)
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
        return redirect('meetagain:index')
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
            obj = form.save(commit=False)
            # 셀렉트에서 'true'/'false' 문자열로 넘어오는 경우 보정
            raw = request.POST.get('is_returned', '')
            obj.is_returned = (str(raw).lower() in ('true', '1', 'on', 'yes'))
            obj.save()
            print("저장완료", obj)  # 디버깅용 로그
            #등록되었습니다 메세지
            keywords = Keyword.objects.filter(user=request.user)
            content_type = ContentType.objects.get_for_model(obj)

            for keyword in keywords:
                if keyword.word in obj.name:
                    Notification.objects.create(
                        user=request.user,
                        keyword=keyword.word,
                        content_type=content_type,
                        object_id=obj.id,
                    )

            return render(request, 'found/found_register_success.html')
        else:
            print("폼 유효성 검사 실패", form.errors)
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
            obj = form.save(commit=False)
            raw = request.POST.get('is_returned', '')
            obj.is_returned = (str(raw).lower() in ('true', '1', 'on', 'yes'))
            obj.save()
            return redirect('meetagain:found_detail', item_id=item.id)
    else:
        form = FoundItemForm(instance=item)
    return render(request, 'found/found_update.html', {'form': form, 'item': item})


@login_required
def found_delete_view(request, item_id):
    item = get_object_or_404(FoundItem, id=item_id)
    if request.method == 'POST':
        item.delete()
        return redirect('meetagain:index')
    return render(request, 'found/confirm_delete.html', {'item': item})


@login_required
def found_detail_view(request, item_id):
    item = get_object_or_404(FoundItem, id=item_id)
    context = {'item': item}
    # 템플릿 경로: founditem_detail.html 사용
    return render(request, 'found/founditem_detail.html', context)


# --------------------
# 키워드 관련 뷰
# --------------------

@login_required
def keyword_list(request):
    keywords = Keyword.objects.filter(user=request.user).values_list('word', flat=True)
    return JsonResponse({'keywords': list(keywords)})


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
    # 실제 구현은 필요에 따라 작성
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
    # notification.read_at = datetime.now()
    notification.save()
    return redirect('meetagain:index')


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'pages/alert_sidebar.html', {'notifications': notifications})

@login_required
def notifications_api(request):
    # 현재 로그인한 사용자(user)의 알림(Notification) 데이터를 최신순으로 20개 가져옴
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:20]

    data = []
    for n in notifications:
        # 각 알림에 대해 필요한 정보들을 딕셔너리 형태로 정리
        data.append({
            'id': n.id,                         # 알림 고유 번호
            'keyword': n.keyword,               # 알림이 연관된 키워드
            'is_read': n.is_read,               # 읽었는지 여부 (True/False)
            'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),  # 생성일 (보기 좋게 문자열로 변환)
            'item_name': str(n.item),           # 연결된 물건 이름 (습득물 또는 분실물)
        })

    # JSON 형식으로 알림 데이터 보내기
    return JsonResponse({'notifications': data})

# --------------------
# 공지사항 관련 뷰(관리자만 접근 가능)
# --------------------

def notice_list(request):
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
    category = request.GET.get('category')
    name = request.GET.get('name')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    location = request.GET.get('location')

    found_items = FoundItem.objects.all()

    if category:
        found_items = found_items.filter(category=category)
    if name:
        found_items = found_items.filter(name__icontains=name)
    if start_date:
        found_items = found_items.filter(found_date__gte=start_date)
    if end_date:
        found_items = found_items.filter(found_date__lte=end_date)
    if location:
        found_items = found_items.filter(found_location__icontains=location)

    data = []
    for item in found_items:
        if item.lat is not None and item.lng is not None:
            data.append({
                'id': item.id,
                'type': 'found',
                'name': item.name,
                'lat': item.lat,
                'lng': item.lng,
                'date': item.found_date.strftime('%Y-%m-%d'),
            })

    return JsonResponse({'items': data})



# --------------------
# 회원 탈퇴(quit) 관련 뷰
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


# --------------------
# FAQ / Inquiry 단순 페이지
# --------------------

def faq_view(request):
    return render(request, "help/help_faq.html")


def notice_view(request):
    return render(request, "notice/notice_list.html")


def inquiry_view(request):
    return render(request, "help/help_inquiry.html")


def myinquiries_view(request):
    inquiries = Inquiry.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "help/help_myinquiries.html", {'inquiries': inquiries})

@login_required
def inquiry_detail_view(request, pk):
    inquiry = get_object_or_404(Inquiry, pk=pk, user=request.user)  # 본인 글만 접근
    return render(request, "help/help_myinquiries_detail.html", {"inquiry": inquiry})

@login_required
def inquiry_edit_view(request, pk):
    inquiry = get_object_or_404(Inquiry, pk=pk, user=request.user)  # 본인 글만

    if request.method == 'POST':
        form = InquiryForm(request.POST, instance=inquiry)  # ★ instance 지정
        if form.is_valid():
            form.save()  # user는 이미 설정돼 있으므로 다시 덮어쓸 필요 없음
            messages.success(request, '문의가 수정되었습니다.')
            return redirect('meetagain:inquiry_detail', pk=inquiry.pk)
    else:
        form = InquiryForm(instance=inquiry)

    return render(request, "help/help_inquiry.html", {"form": form, "inquiry": inquiry})


# --------------------
# 관리자용 문의사항 관련 뷰
# --------------------

@login_required
def inquiry_create(request):
    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.user = request.user
            inquiry.save()
            return redirect('inquiry_success')  # 성공 페이지 또는 목록 등으로 리다이렉트
    else:
        form = InquiryForm()
    return render(request, 'meetagain/inquiry_form.html', {'form': form})

def inquiry_success(request):
    return render(request, 'meetagain/inquiry_success.html')
