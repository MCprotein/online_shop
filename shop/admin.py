from django.contrib import admin
from .models import *


# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug']
    prepopulated_fields = {'slug': ['name']}  # 카테고리를만들때 뭐랑뭐랑 섞어서 자동으로  만들어줌


admin.site.register(Category, CategoryAdmin)


@admin.register(Product)  # 아래꺼보다 어노테이션을 먼저 실행하겠다
class ProdcutAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'category', 'price', 'stock', 'available_display', 'available_order', 'created', 'updated']
    list_filter = ['available_display', 'created', 'updated', 'category']
    prepopulated_fields = {'slug': ['name']}
    list_editable = ['price', 'stock', 'available_display', 'available_order']
