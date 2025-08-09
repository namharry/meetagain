from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from datetime import datetime
import json
from .models import LostItem, FoundItem, Keyword, Notification
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
    return render(request, 'lost/lost_index.html', context)

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

@login_required
def keyword_list(request):
    keywords = Keyword.objects.filter(user=request.user)
    return render(request, 'keywords/keyword_list.html', {'keywords': keywords})

@require_POST
def keyword_add(request):
    word = request.POST.get('word', '').strip()

    if not word:
        messages.error(request, "키워드를 입력해주세요.")
        return redirect('meetagain:found_keyword_list')

    keyword, created = Keyword.objects.get_or_create(user=request.user, word=word)

    if created:
        messages.success(request, f"'{word}' 키워드가 등록되었습니다.")
    else:
        messages.info(request, f"이미 '{word}' 키워드를 등록하셨습니다.")

    return redirect('meetagain:found_keyword_list')

@require_POST
def keyword_delete(request, keyword_id):
    keyword = Keyword.objects.filter(id=keyword_id, user=request.user).first()
    if keyword:
        messages.success(request, f"'{keyword.word}' 키워드가 삭제되었습니다.")
        keyword.delete()
    else:
        messages.error(request, "해당 키워드를 찾을 수 없습니다.")
    return redirect('meetagain:found_keyword_list')
