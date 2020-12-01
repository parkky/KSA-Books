from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.conf import settings
from django.urls import reverse
from math import log, ceil


class Subject(models.Model):
    name = models.CharField(max_length=10, verbose_name='교과명')

    def __str__(self):
        return self.name


class Course(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, verbose_name='교과', null=True)
    name = models.CharField(max_length=50, verbose_name='과목명')
    open = models.BooleanField(verbose_name='수강 가능')

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=100, verbose_name='제목')
    author = models.CharField(max_length=100, verbose_name='저자')
    courses = models.ManyToManyField(Course, verbose_name='과목')
    subject = models.ForeignKey(Subject, verbose_name='교과', on_delete=models.SET_NULL, null=True)
    publisher = models.CharField(max_length=100, verbose_name='출판사')
    isbn = models.CharField(max_length=13, verbose_name='ISBN',
                            help_text='13 Character <a href="https://www.isbn-international.org/content/what-isbn">ISBN number</a>')
    # link = models.URLField(max_length=300, verbose_name='책 링크')
    list_price = models.PositiveIntegerField(verbose_name='정가', null=True, blank=True)
    group_price = models.PositiveIntegerField(verbose_name='공동구매 가격', null=True, blank=True)
    using = models.BooleanField(verbose_name='사용 여부')

    class Meta:
        permissions = (
            ('load_data', 'Can load data'),
        )
        ordering = ['subject']

    def __str__(self):
        return f'({self.subject}, {self.display_courses()}){self.title}'

    def display_courses(self):
        return ', '.join([str(c) for c in self.courses.all()])

    display_courses.short_description = '수업'


QUALITY = (
    ('a', '상'),
    ('b', '중'),
    ('c', '하'),
)


class Offer(models.Model):
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                               related_name='offer_seller')
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name='offer_buyer')
    want_users = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)
    seller_done = models.BooleanField(null=True, default=False)
    buyer_done = models.BooleanField(null=True, default=False)
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True, verbose_name='책')
    price = models.PositiveIntegerField(verbose_name='판매 가격')
    quality = models.CharField(choices=QUALITY, max_length=1, verbose_name='보관 상태', null=True)
    explain = models.TextField(verbose_name='내용', null=True, blank=True)
    date_time = models.DateTimeField(auto_now_add=True, null=True)
    views = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='views')

    def get_absolute_url(self):
        return reverse('check-offer', args=[str(self.id)])


class Comment(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
                               related_name='comment_sender')
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='comment_receiver')
    secret = models.BooleanField(null=True)
    text = models.TextField(verbose_name='댓글')
    date_time = models.DateTimeField(null=True, auto_now_add=True)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, null=True)
    is_deleted = models.BooleanField(default=False, null=True)

    class Meta:
        ordering = ['-date_time']

    def __str__(self):
        return self.text


notifications_list = ['Comment', 'New offer', 'Sold to user', 'Sold to other', 'New want', 'Buyer cancel',
                      'Seller cancel']
COMMENT, NEW_OFFER, SOLD_TO_USER, SOLD_TO_OTHER, NEW_WANT, BUYER_CANCEL, SELLER_CANCEL = \
    tuple([str(i) for i in range(len(notifications_list))])
NOTIFICATIONS = tuple([(str(i), notifications_list[i]) for i in range(len(notifications_list))])


class Notification(models.Model):
    type = models.CharField(choices=NOTIFICATIONS, max_length=ceil(log(len(NOTIFICATIONS)+1, 10)), null=True)
    date_time = models.DateTimeField(auto_now_add=True, null=True)

    data_offer1 = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, blank=True)
    data_user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='data_user1')

    def html_form(self):
        html = []
        TEXT, LINK = 'text', 'link'
        if self.type == COMMENT:
            html.append((TEXT, f'{self.data_user1}이(가) '))
            html.append((LINK, self.data_offer1.book.title, self.data_offer1.get_absolute_url()))
            html.append((TEXT, '에 댓글을 달았습니다.'))
        elif self.type == NEW_OFFER:
            html.append((TEXT, f'{self.data_user1}이(가) '))
            html.append((LINK, self.data_offer1.book.title, self.data_offer1.get_absolute_url()))
            html.append((TEXT, '을(를) 판매하고 있습니다.'))
        elif self.type == SOLD_TO_USER:
            html.append((TEXT, f'{self.data_user1}이(가) 사용자에게 '))
            html.append((LINK, self.data_offer1.book.title, self.data_offer1.get_absolute_url()))
            html.append((TEXT, '을(를) 판매했습니다.'))
        elif self.type == SOLD_TO_OTHER:
            html.append((TEXT, f'{self.data_user1}이(가) 다른 사람에게 '))
            html.append((LINK, self.data_offer1.book.title, self.data_offer1.get_absolute_url()))
            html.append((TEXT, '을(를) 판매했습니다.'))
        elif self.type == NEW_WANT:
            html.append((TEXT, f'{self.data_user1}이(가) '))
            html.append((LINK, self.data_offer1.book.title, self.data_offer1.get_absolute_url()))
            html.append((TEXT, '을(를) 구매 신청했습니다.'))
        elif self.type == BUYER_CANCEL:
            html.append((TEXT, f'{self.data_user1}이(가) '))
            html.append((LINK, self.data_offer1.book.title, self.data_offer1.get_absolute_url()))
            html.append((TEXT, ' 구매를 취소했습니다.'))
        elif self.type == SELLER_CANCEL:
            html.append((TEXT, f'{self.data_user1}이(가) '))
            html.append((LINK, self.data_offer1.book.title, self.data_offer1.get_absolute_url()))
            html.append((TEXT, ' 판매를 취소했습니다.'))
        html.append(self.date_time)
        return html


class StudentUserManager(BaseUserManager):
    def create_user(self, student_id, name, password):
        user = self.model(student_id=student_id, name=name)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, student_id, name, password):
        user = self.create_user(student_id, name, password)
        user.is_active = True
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class StudentUser(AbstractBaseUser, PermissionsMixin):
    objects = StudentUserManager()
    student_id = models.CharField(max_length=10, verbose_name='학번', help_text='00-000', unique=True)
    name = models.CharField(max_length=100, verbose_name='이름')
    email = models.EmailField()
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    notifications = models.ManyToManyField(Notification, blank=True)
    unread_notification = models.PositiveIntegerField(default=0)

    notify_books = models.ManyToManyField(Book, verbose_name='원하는 책', blank=True)
    notify_comment = models.BooleanField(default=True, verbose_name='자신에게 댓글을 썼을 때')
    notify_new_offer = models.BooleanField(default=True, verbose_name='원하는 책이 올라왔을 때')
    notify_sold_to_user = models.BooleanField(default=True, verbose_name='자신에게 책을 판매했을 때')
    notify_sold_to_other = models.BooleanField(default=True, verbose_name='구매 신청한 책이 다른 사람에게 판매되었을 때')
    notify_new_want = models.BooleanField(default=True, verbose_name='자신의 책을 누군가 구매 신청했을 때')

    USERNAME_FIELD = 'student_id'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return ' '.join([self.student_id, self.name])

    def is_international(self):
        return self.student_id[3] == '2'
