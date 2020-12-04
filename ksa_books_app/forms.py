from django import forms
from django.forms import ModelForm
from .models import Offer, Book, StudentUser

QUALITY_STANDARD = (
    '거의 새 것 같음',
    '다소 낡았지만 사용에는 지장이 없음',
    '구겨지거나 찢어져서 사용에 지장이 있음',
)


class OfferForm(ModelForm):
    price = forms.IntegerField(
        widget=forms.NumberInput(attrs={'step': 1000}),
    )

    class Meta:
        model = Offer
        fields = ['book', 'price', 'quality', 'explain']
        help_texts = {
            'quality': '<br>상: {}<br>중: {}<br>하: {}'.format(QUALITY_STANDARD[0], QUALITY_STANDARD[1],
                                                            QUALITY_STANDARD[2]),
        }


class OfferUpdateForm(OfferForm):
    book = forms.ModelChoiceField(queryset=Book.objects.all(), disabled=True)


MIN_QUALITY = (
    ('abc', '하 이상'),
    ('ab', '중 이상'),
    ('a', '상 이상'),
)

NEW, CHEAP = tuple([str(i) for i in range(2)])
SORT = (
    (NEW, '최신순'),
    (CHEAP, '가격순'),
)

UNSOLD, UNEXCHANGED, ALL = tuple([str(i) for i in range(3)])
STATE = (
    (UNSOLD, '판매되지 않은 책만'),
    (UNEXCHANGED, '거래되지 않은 책만'),
    (ALL, '모두'),
)


class SearchForm(forms.Form):
    book = forms.ModelChoiceField(label='책', queryset=Book.objects.all(), required=False)
    min_quality = forms.ChoiceField(label='보관 상태', choices=MIN_QUALITY, required=False)
    sort = forms.ChoiceField(label='정렬', choices=SORT, required=False)
    state = forms.ChoiceField(label='상태', choices=STATE, required=False)


class CommentForm(forms.Form):
    secret = forms.BooleanField(label='비밀글', required=False)
    receiver = forms.CharField(label='받는 사람', disabled=True, required=False)
    text = forms.CharField(widget=forms.Textarea(attrs={'placeholder': '카톡 사용을 권장'}), label='댓글 입력')


class NotificationSettingForm(forms.ModelForm):
    notify_books = forms.ModelMultipleChoiceField(
        queryset=Book.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label='원하는 책 선택',
        required=False
    )

    class Meta:
        model = StudentUser
        fields = ['notify_new_offer', 'notify_books', 'notify_comment', 'notify_sold_to_user', 'notify_sold_to_other',
                  'notify_new_want']


class ChangeNameForm(forms.ModelForm):
    class Meta:
        model = StudentUser
        fields = ['name']
