# 프론트쪽에 노출될 소스코드
# 입력받은 데이터를 validation

from django import forms
from .models import Order


class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'address', 'postal_code', 'city']

