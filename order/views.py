from django.shortcuts import render, get_object_or_404
from .models import *
from cart.cart import Cart
from .forms import *
# Create your views here.

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        # 입력받은 정보를 후처리
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save() # modelform이기때문에 객체가 나온다.
            if cart.coupon:
                order.coupon = cart.coupon
                # order.discount = cart.coupon.amount
                order.discount = cart.get_discount_total()
                order.save()
            for item in cart: #제품처리
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'], quantity=item['quantity'])
            cart.clear()
            return render(request, 'order/created.html', {'order':order})
    else:
        # 주문자 정보를 입력받는 페이지
        form = OrderCreateForm
    return render(request, 'order/create.html', {'cart':cart, 'form':form})

# JS 동작하지 않는 환경에서도 주문은 가능해야 한다.
def order_complete(request): # 완료하는 로직은 없고 이미 완료된 것만 보여주는 뷰
    order_id = request.GET.get('order_id')
    # order = Order.objects.get(id=order_id)
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'order/created.html', {'order':order})


from django.views.generic.base import View
from django.http import JsonResponse
class OrderCreateAjaxView(View):
    # dispatcher : http response(post, get ..) 에 따라 분기해주는 것
    # 클래스형 뷰에서는 디스패처에서 이미 다 분기가 되어있다
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({"authenticated":False}, status=403)

        cart = Cart(request)
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)  # modelform이기때문에 객체가 나온다.
            if cart.coupon:
                order.coupon = cart.coupon
                order.discount = cart.get_discount_total()
            order.save()
            for item in cart:  # 제품처리
                OrderItem.objects.create(order=order, product=item['product'], price=item['price'],
                                         quantity=item['quantity'])
            cart.clear()
            data = {
                "order_id":order.id
            }
            return JsonResponse(data)
        else:
            return JsonResponse({}, status=401)

# transaction 생성, 단계를 만들어서 처리
class OrderCheckoutAjaxView(View):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated: # mixin 가능
            return JsonResponse({"authenticated":False}, status=403)

        order_id = request.POST.get('order_id')
        order = Order.objects.get(id=order_id)
        amount = request.POST.get('amount')

        try:
            merchant_order_id = OrderTransaction.objects.create_new(
                order=order,
                amount=amount
            )
        except:
            merchant_order_id = None

        if merchant_order_id is not None:
            data = {
                "works":True,
                "merchant_id":merchant_order_id
            }
            return JsonResponse(data)
        else:
            return JsonResponse({}, status=401)

class OrderImpAjaxView(View): # 제대로 주문됐는지 확인, 후처리
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated: # mixin 가능
            return JsonResponse({"authenticated":False}, status=403)

        order_id = request.POST.get('order_id')
        order = Order.objeects.get(id=order_id)

        merchant_id = request.POST.get('merchant_id')
        imp_id = request.POST.get('imp_id')
        amount = request.POST.get('amount')

        try:
            trans = OrderTransaction.objects.get(
                order=order,
                merchant_order_id=merchant_id,
                amount=amount
            )
        except:
            trans = None

        if trans is not None:
            trans.transaction_id = imp_id
            #trans.success = True
            trans.save()
            order.paid = True
            order.save()

            data = {
                "works":True
            }
            return JsonResponse(data)
        else:
            return JsonResponse({}, status=401)