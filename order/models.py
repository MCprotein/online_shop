from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.
from coupon.models import Coupon
from shop.models import Product

class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False) # 사용자한테 입력받을때는 blank=True 있어야함

    coupon = models.ForeignKey(Coupon, on_delete=models.PROTECT, related_name='order_coupon', null=True, blank=True)
    discount = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100000)])

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'Order {self.id}'

    def get_total_product(self):
        return sum(item.get_item_price() for item in self.items.all())

    def get_total_price(self):
        total_product = self.get_total_product()
        return total_product - self.discount

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items') # 다른 값들을 참조, 주문이 지워지면 주문아이템도 다 지워져야 한다.
    # Order의 입장에서 OrderItem을 뭐라고 부를꺼냐? -> order.items라고 부른다.
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='order_products') # Product 입장에서 OrderItem을 뭐라고 부를거냐
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return str(self.id)

    def get_item_price(self):
        return self.price * self.quantity

# 결제 관련 transaction매니저
from .iamport import payments_prepare, find_transaction
# 주문하기 버튼을 누르면 결제미완료를 기록하고 주문이 완료되면 결제완료로 상태바꿈 -> 그래야 주문 취소해도 기록남음
import hashlib
class OrderTranscationManager(models.Manager):
    def create_new(self, order, amount, success=None, transaction_status=None):
        if not order:
            raise ValueError("주문 정보 오류")

        order_hash = hashlib.sha1(str(order.id).encode('utf-8')).hexdigest() # order.id를 utf-8로 인코딩 한 후 8진수로 바꿈
        email_hash = str(order.email).split("@")[0]
        final_hash = hashlib.sha1((order_hash+email_hash).encode('utf-8')).hexdigest()[:10] # 유니크한 주문번호 -> 아이엠포트쪽에 보내는 구분번호로 사용
        merchant_order_id = str(final_hash)
        payments_prepare(merchant_order_id, amount)

        transaction = self.model(# 매니저라서 self에 모델이 있다
            order=order,
            merchant_order_id=merchant_order_id,
            amount=amount
        )

        if success is not None:
            transaction.success = success
            transaction.transaction_status = transaction_status

        try:
            transaction.save()
        except Exception as e:
            print("save error", e)

        return transaction.merchant_order_id

    def get_transaction(self, merchant_order_id): #매니저에 메소드가 추가된거라서 orm.object. 머라고 부를 수 있는걸 추가
        result = find_transaction(merchant_order_id)
        if result['status'] == 'paid':
            return result
        else:
            return None

class OrderTransaction(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE) # Order 정보가 없으면 결제정보도 없어져야 한다.
    merchant_order_id = models.CharField(max_length=120, null=True, blank=True)
    transaction_id = models.CharField(max_length=120, null=True, blank=True) # 회사에 남아있는 프라이머리키
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    transaction_status = models.CharField(max_length=220, null=True, blank=True)
    type = models.CharField(max_length=120, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    # success = models.BooleanField(default=False)
    objects = OrderTranscationManager()

    def __str__(self):
        return str(self.order.id)

    class Meta:
        ordering = ['-created']

# signal
def order_payment_validation(sender, instance, created, *args, **kwargs):
        if instance.transaction_id:
            import_transaction = OrderTransaction.objects.get_transaction(merchant_order_id=instance.merchant_order_id)
            merchant_order_id = import_transaction['merchant_order_id']
            imp_id = import_transaction['imp_id']
            amount = import_transaction['amount']

            local_transaction = OrderTransaction.objects.filter(merchant_order_id=merchant_order_id, transaction_id=imp_id, amount=amount).exists()
            if not import_transaction or not local_transaction:
                raise ValueError("비정상 거래입니다.")

from django.db.models.signals import post_save # model save가 된 다음에 뭘 하겠다
post_save.connect(order_payment_validation, sender=OrderTransaction) # ordertransaction에 세이브가 일어날때만 이 일을 처리함