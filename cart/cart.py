from decimal import Decimal
from django.conf import settings
from shop.models import Product

class Cart(object):
    def __init__(self, request): # 초기화
        self.session = request.session
        cart = self.session.get(settings.CART_ID)
        if not cart:
            cart = self.session[settings.CART_ID] = {}
        self.cart = cart

    def __len__(self): # 수량 총 합
        return sum(item['quantity'] for item in self.cart.values())

    def __iter__(self): # 콜문 어떤요소를 어떻게건네줄거냐
        product_ids = self.cart.keys()

        products = Product.objects.filter(id__in=product_ids) # products_ids에 있는 id 제품들만 필터링 해서 줘라

        for product in products:
            self.cart[str(product.id)]['product'] = product

        for item in self.cart.values(): # 이미 가지고 있는 것들을 숫자로 바꿔서 아이템에 넣어줌
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']

            yield item

    def add(self, product, quantity=1, is_update=False): # update는 추가 하는게아니고 20->5로 설정
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}

        if is_update:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity

        self.save()

    def save(self):
        self.session[settings.CART_ID] = self.cart
        self.session.modified = True # 이렇게 해야 변동사항이 저장됨

    def remove(self, product):
        product_id = str(product.id)
        if product_id in self.cart:
            del(self.cart[product_id])
            self.save()

    def clear(self):
        self.session[settings.CART_ID] = {}
        self.session.modified = True

    def get_product_total(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
