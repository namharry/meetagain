from django.shortcuts import render, redirect
from .forms import LostItemForm
from .models import LostItem, FoundItem


def register_lost_item(request):
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES)  # 이미지도 받으니까 request.FILES도 필요
        if form.is_valid():
            form.save()  # DB에 저장
            return redirect('meetagain:register')  # 임시로 등록 페이지로 다시 이동
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


# ✅ 지도용 핀 데이터 API
from django.http import JsonResponse

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