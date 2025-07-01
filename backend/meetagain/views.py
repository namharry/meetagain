from django.shortcuts import render, redirect
from .forms import LostItemForm

# Create your views here.
def register_lost_item(request):
    if request.method == 'POST':
        form = LostItemForm(request.POST, request.FILES)  # 이미지도 받으니까 request.FILES도 필요
        if form.is_valid():
            form.save()  # DB에 저장
            return redirect('meetagain:register')  # 임시로 등록 페이지로 다시 이동
    else:
        form = LostItemForm()
    return render(request, 'register.html', {'form': form})