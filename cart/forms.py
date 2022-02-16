from django import forms

# 클라이언트 화면에 입력 폼을 만들어주려고
# 클라이언트가 입력한 데이터에 대한 전처리

# modelForm : 회원가입, 글쓰기, 원래 모델이 있는데 입력받을때
# form : 이메일발송, 일정한 양식만 가져다가 쓰겠다

class AddProductForm(forms.Form):
    quantity = forms.IntegerField()
    is_update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput) # BooleanField는 required=False 해야함, widget은 사용자에게 안보이게함