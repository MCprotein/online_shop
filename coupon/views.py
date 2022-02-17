from django.shortcuts import render
from django.shortcuts import redirect
from django.utils import timezone # datetime은 컴퓨터시간을 읽는데, timezone은 서버시간 정확
from django.views.decorators.http import require_POST # post로 접근할때만 사용하겠따
from .models import Coupon
from .forms import AddCouponForm
# Create your views here.

@require_POST
def add_coupon(request):
    now = timezone.now()
    form = AddCouponForm(request.POST)
    if form.is_valid():
        code = form.cleaned_data['code']

        try:
            coupon = Coupon.objects.get(code__iexact=code, use_from__lte=now, use_to__gte =now, active=True) # 대소문자 구분 없이 일치, 사용시간보다 나중, 사용시간보다 이전, 활성화
            request.session['coupon_id'] = coupon.id

        except Coupon.DoesNotExist:
            request.session['coupon_id'] = None

    return redirect('cart:detail')