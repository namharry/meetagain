# backend/meetagain/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import logout
from django.core.paginator import Paginator  # ➕ 페이지네이션
from .models import Inquiry, LostItem, FoundItem, Keyword, Notification, Notice
from .forms import InquiryForm, LostItemForm, FoundItemForm, NoticeForm
from django.views.decorators.http import require_http_methods
from django.db.models import Q
from datetime import timedelta
from django.utils import timezone
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from .forms import LOCATION_CHOICES

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

    # 최신순 정렬 (지도/초기 노출용 — 화면에는 AJAX로 다시 채움)
    items = items.order_by('-found_date', '-id')

    return render(request, 'pages/index.html', {
    'items': items,
    'location_choices': LOCATION_CHOICES,
    'category': category,
    'name': name,
    'start_date': start_date,
    'end_date': end_date,
    'location': location,
    })

    


# --------------------
# 분실물 (LostItem) 뷰
# --------------------

@login_required
def lost_register_view(request):
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user          # ✅ 작성자 저장 (중요!)
            obj.save()
            # ✅ 성공 페이지로 이동'
            return render(request, 'lost/lost_register_success.html', {'item_id':obj.id})
        else:
            return render(request, 'lost/lost_register.html', {'form': form, 'mode': 'create'})
    else:
        form = LostItemForm()
    return render(request, 'lost/lost_register.html', {'form': form, 'mode': 'create'})

@login_required
def lost_edit_view(request, item_id):
    item = get_object_or_404(LostItem, id=item_id, user=request.user)  # 본인 글만 수정
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, "분실물 정보가 수정되었습니다.")
            return redirect('meetagain:lost_detail', item_id=item.id)
    else:
        form = LostItemForm(instance=item)
    # 🔽 등록 폼 템플릿 재사용 (파일이 이미 존재한다고 가정)
    return render(request, 'lost/lost_register.html', {'form': form, 'item': item, 'mode': 'update'})


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
            obj.user = request.user  
            # 셀렉트에서 'true'/'false' 문자열로 넘어오는 경우 보정
            raw = request.POST.get('is_returned', '')
            obj.is_returned = (str(raw).lower() in ('true', '1', 'on', 'yes'))
            obj.save()
            # 키워드 알림
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
            return redirect('meetagain:found_detail', item_id=obj.id)
    else:
        form = FoundItemForm(instance=item)
    return render(request, 'found/found_register.html', {'form': form, 'item': item, 'edit_mode': True})


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


@login_required
def found_list_api(request):
    """
    메인(index)에서 페이지 이동 없이 숫자 버튼으로 넘기기 위한 JSON API
    - 페이지당 6개
    - index의 검색 파라미터(category/name/start_date/end_date/location) 그대로 반영
    """
    page = int(request.GET.get('page', 1))
    per_page = 6

    qs = FoundItem.objects.all()

    category = request.GET.get('category')
    name = request.GET.get('name')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    location = request.GET.get('location')

    if category:
        qs = qs.filter(category=category)
    if name:
        qs = qs.filter(name__icontains=name)
    if start_date:
        qs = qs.filter(found_date__gte=start_date)
    if end_date:
        qs = qs.filter(found_date__lte=end_date)
    if location:
        qs = qs.filter(found_location__icontains=location)

    qs = qs.order_by('-found_date', '-id')
    paginator = Paginator(qs, per_page)
    page_obj = paginator.get_page(page)

    def to_dict(it):
        return {
            'id': it.id,
            'name': it.name,
            'found_date': it.found_date.strftime('%Y-%m-%d') if it.found_date else '',
            'found_location': it.found_location,
            'image_url': (it.image.url if it.image else None),
        }

    return JsonResponse({
        'items': [to_dict(i) for i in page_obj.object_list],
        'page': page_obj.number,
        'total_pages': paginator.num_pages,
        'has_prev': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
    })

@login_required
def found_edit(request, pk):
    found_item = get_object_or_404(FoundItem, pk=pk, user=request.user)
    if request.method == 'POST':
        form = FoundItemForm(request.POST, request.FILES, instance=found_item)
        if form.is_valid():
            form.save()
            return redirect('found_detail', pk=found_item.pk)
        else:
            form = FoundItemForm(instance=found_item)
        return render(request, 'found/found_register.html', {'form': form, 'edit_mode': True})

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
    print(f"keyword_add 호출됨, word: {word}, user: {request.user}")  # 디버깅용 출력
    if not word:
        return JsonResponse({'error': '키워드를 입력해주세요.'}, status=400)

    keyword, created = Keyword.objects.get_or_create(user=request.user, word=word)
    if created:
        print(f"키워드 생성됨: {keyword.word}")
        return JsonResponse({'success': f"'{word}' 키워드가 등록되었습니다."})
    else:
        print(f"이미 존재하는 키워드: {keyword.word}")
        return JsonResponse({'info': f"이미 '{word}' 키워드를 등록하셨습니다."})


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
def get_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    data = []
    for n in notifications:
        item_name = str(n.item).replace('[습득물] ', '')
        data.append({
            'id': n.id,
            'keyword': n.keyword,
            'content_type': n.content_type.model,
            'object_id': n.object_id,
            'is_read': n.is_read,
            'created_at': n.created_at.strftime('%Y-%m-%d %H:%M'),
            'item_name': item_name,
        })
    return JsonResponse({'notifications': data})

@login_required
@require_POST
def mark_notifications_read(request):
    user = request.user
    user.notification_set.filter(is_read=False).update(is_read=True)
    return JsonResponse({'status': 'success'})


# --------------------
# 공지사항 관련 뷰(관리자만 접근 가능)
# --------------------

def notice_list(request):
    notices = Notice.objects.order_by('-created_at')
    return render(request, 'notice/notice_list.html', {'notices': notices})


def notice_detail(request, pk):
    notice = get_object_or_404(Notice, pk=pk)
    return render(request, 'notice/notice_detail.html', {'notice': notice})


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
    # ✅ 양쪽 파라미터 키 모두 지원
    category   = request.GET.get('category', '')
    name       = request.GET.get('name') or request.GET.get('q') or ''
    location   = request.GET.get('location', '')
    start_date = request.GET.get('start_date') or request.GET.get('date_from') or ''
    end_date   = request.GET.get('end_date')   or request.GET.get('date_to')   or ''

    filters_present = any([category, name, location, start_date, end_date])

    qs = FoundItem.objects.all()

    # ✅ 기본 진입(필터 없음)일 때만 최근 2주 제한
    if not filters_present:
        today = timezone.localdate()
        two_weeks_ago = today - timedelta(days=14)
        qs = qs.filter(found_date__gte=two_weeks_ago)

    # ✅ 기간 필터(둘 다 지원)
    sd = parse_date(start_date) if start_date else None
    ed = parse_date(end_date)   if end_date   else None
    if sd:
        qs = qs.filter(found_date__gte=sd)
    if ed:
        qs = qs.filter(found_date__lte=ed)

    # ✅ 기타 필터
    if category:
        qs = qs.filter(category=category)
    if name:
        qs = qs.filter(name__icontains=name)
    if location:
        qs = qs.filter(found_location__icontains=location)

    # ✅ 지도 가능한 데이터만
    qs = qs.filter(lat__isnull=False, lng__isnull=False).order_by('-found_date', '-id')

    data = [{
        'id': item.id,
        'type': 'found',
        'name': item.name,
        'lat': item.lat,
        'lng': item.lng,
        'date': item.found_date.strftime('%Y-%m-%d') if item.found_date else '',
        'thumbnail_url': (item.image.url if item.image else None),  # ✅ 썸네일 URL 추가
    } for item in qs]

    return JsonResponse({'items': data})

# --------------------
# 회원 탈퇴(quit) 관련 뷰
# --------------------

@login_required
def quit_account_view(request):
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
    inquiry = get_object_or_404(Inquiry, pk=pk, user=request.user)
    return render(request, "help/help_myinquiries_detail.html", {"inquiry": inquiry})

@login_required
def inquiry_edit_view(request, pk):
    inquiry = get_object_or_404(Inquiry, pk=pk, user=request.user)

    if request.method == 'POST':
        form = InquiryForm(request.POST, instance=inquiry)
        if form.is_valid():
            form.save()
            messages.success(request, '문의가 수정되었습니다.')
            return redirect('meetagain:inquiry_detail', pk=inquiry.pk)
    else:
        form = InquiryForm(instance=inquiry)

    return render(request, "help/help_inquiry.html", {"form": form, "inquiry": inquiry})


# --------------------
# 관리자용 문의사항 관련 뷰
# --------------------
@staff_member_required
@login_required
def admin_inquiry_create(request):
    if request.method == 'POST':
        form = InquiryForm(request.POST)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.user = request.user
            inquiry.save()
            return redirect('meetagain:admin_inquiry_success')
    else:
        form = InquiryForm()
    return render(request, 'meetagain/inquiry_form.html', {'form': form})

@staff_member_required
def admin_inquiry_success(request):
    return render('meetagain:admin_inquiry_success')
