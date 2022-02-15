from django.db import models
from django.urls import reverse

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True) # indexing 가능하게 설정
    meta_description = models.TextField(blank=True) # 필수값이 아님
    slug = models.SlugField(max_length=200, db_index=True, unique=True, allow_unicode=True) # pk로 사용될 가능성이 있기 때문에 인덱싱 가능하게, 다른애들이랑 안겹치게, 한글작성 가능

    class Meta:
        ordering = ['name']
        verbose_name = 'category' # 노출될때 단수형 이름
        verbose_name_plural = 'categories' # 노출될때 복수형 이름

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_in_category', args=self.slug) # 상세페이지로 가게

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products') # 카테고리가 지워져도 게시글은 남아있다. 대신 카테고리는 null로 설정
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True, unique=True, allow_unicode=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    meta_description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField
    available_display = models.BooleanField('Display', default=True)
    available_order = models.BooleanField('Order', default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created', '-updated']
        index_together = [['id', 'slug']] # 두개를 병합해서 인덱스에 넣어줌

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', args=[self.id, self.slug])