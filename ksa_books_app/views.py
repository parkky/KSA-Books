from django.shortcuts import render
from django.views.generic import UpdateView, DeleteView, ListView
from .models import Book, Course, Subject, Offer, Comment, StudentUser, Notification
from .models import COMMENT, NEW_OFFER, SOLD_TO_USER, SOLD_TO_OTHER, NEW_WANT
from django.urls import reverse_lazy
from django.contrib.auth.decorators import permission_required, login_required
from .forms import SearchForm, CommentForm, OfferForm, OfferUpdateForm, NotificationSettingForm
from .forms import NEW, CHEAP
from .forms import UNSOLD, UNEXCHANGED, ALL
from django.core.paginator import Paginator
from django.contrib.auth.mixins import UserPassesTestMixin


def create_notification(user_qs, type, user1=None, offer1=None):
    ntf = Notification.objects.create(type=type, data_user1=user1, data_offer1=offer1)
    for user in user_qs:
        if (type == COMMENT and not user.notify_comment) or \
                (type == NEW_OFFER and not user.notify_new_offer) or \
                (type == SOLD_TO_USER and not user.notify_sold_to_user) or \
                (type == SOLD_TO_OTHER and not user.notify_sold_to_other) or \
                (type == NEW_WANT and not user.notify_new_want):
            continue
        if type == NEW_OFFER:
            if not user.notify_books.filter(id=offer1.book.id).exists():
                continue
        user.notifications.add(ntf)
        user.unread_notification += 1
        user.save()


def home_view(request):
    context = {
        'user': request.user
    }
    return render(request, 'home.html', context=context)


def about_view(request):
    context = dict()
    return render(request, 'about.html', context=context)


class BookListView(ListView):
    model = Book
    template_name = 'book_list.html'


@login_required
def offer_create(request):
    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            offer = Offer.objects.create(seller=request.user, book=data['book'], price=data['price'],
                                         worn_degree=data['worn_degree'], worn_explain=data['worn_explain'],
                                         note_degree=data['note_degree'], note_explain=data['note_explain'])
            notify_users = StudentUser.objects.filter(notify_books=request.POST.get('book')).exclude(id=request.user.id)
            create_notification(notify_users, NEW_OFFER, user1=request.user, offer1=offer)
            form = OfferForm()
    else:
        form = OfferForm()
    context = {
        'form': form,
    }
    return render(request, 'offer_form.html', context=context)


class OfferUpdate(UserPassesTestMixin, UpdateView):
    template_name = 'offer_form.html'
    model = Offer
    form_class = OfferUpdateForm

    def test_func(self):
        return self.get_object().seller == self.request.user


class OfferDelete(UserPassesTestMixin, DeleteView):
    template_name = 'offer_confirm_delete.html'
    model = Offer
    success_url = reverse_lazy('home')

    def test_func(self):
        return self.get_object().seller == self.request.user


def search_view(request):
    qs = Offer.objects.all()
    if request.user.is_authenticated:
        qs = qs.exclude(seller=request.user)
    form = SearchForm(request.GET)
    if form.is_valid():
        data = form.cleaned_data
        if data['book'] and data['book'] != '0':
            qs = qs.filter(book_id=data['book'])
        if data['min_worn_degree']:
            qs = qs.filter(worn_degree__in=data['min_worn_degree'])
        if data['min_note_degree']:
            qs = qs.filter(note_degree__in=data['min_note_degree'])
        if data['state'] == UNSOLD:
            qs = qs.filter(buyer=None)
        elif data['state'] == UNEXCHANGED:
            qs = qs.exclude(seller_done=True, buyer_done=True)
        elif data['state'] == ALL:
            pass
        if data['sort'] == NEW:
            qs = qs.order_by('date_time')
        elif data['sort'] == CHEAP:
            qs = qs.order_by('price')
    paginator = Paginator(qs, 30)
    page = request.GET.get('page')
    offers = paginator.get_page(page)
    context = {
        'form': form,
        'page_obj': offers,
        'is_paginated': True,
    }
    return render(request, 'search.html', context=context)


@login_required
def offer_view(request, pk):
    offer = Offer.objects.get(pk=pk)
    want_users = offer.want_users.all()
    if offer.seller == request.user:
        if 'receiver' in request.GET:
            receiver = StudentUser.objects.get(student_id=request.GET.get('receiver'))
        else:
            receiver = None
    else:
        receiver = offer.seller
    if receiver:
        secret = True
    else:
        secret = False
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            Comment.objects.create(sender=request.user, receiver=receiver, text=data['text'],
                                   secret=data['secret'], offer=offer)
            create_notification(StudentUser.objects.filter(id=offer.seller.id), COMMENT, user1=request.user, offer1=offer)
        if 'want' in request.POST:
            offer.want_users.add(request.user)
            if request.user != offer.seller:
                create_notification(StudentUser.objects.filter(id=offer.seller.id), NEW_WANT, user1=request.user, offer1=offer)
        elif 'want-cancel' in request.POST:
            offer.want_users.remove(request.user)
            if offer.buyer == request.user:
                offer.buyer = None
        elif 'sell-to' in request.POST:
            offer.buyer = StudentUser.objects.get(id=request.POST.get('sell-to'))
            create_notification(StudentUser.objects.filter(id=offer.buyer.id), SOLD_TO_USER, user1=request.user, offer1=offer)
            create_notification(want_users.exclude(id=offer.buyer.id), SOLD_TO_OTHER, user1=request.user, offer1=offer)
        elif 'sell-cancel' in request.POST:
            offer.buyer = None
        elif 'sell-done' in request.POST:
            offer.seller_done = True
        elif 'sell-done-cancel' in request.POST:
            offer.seller_done = False
        elif 'buy-done' in request.POST:
            offer.buyer_done = True
        elif 'buy-done-cancel' in request.POST:
            offer.buyer_done = False
        elif 'delete_comment' in request.POST:
            delete_comment = Comment.objects.get(id=request.POST['delete_comment'])
            delete_comment.is_deleted = True
            delete_comment.save()
        offer.save()
    comment_form = CommentForm(initial={'receiver': str(receiver), 'secret': secret})
    comment_list = Comment.objects.filter(offer=offer, is_deleted=False)
    context = {
        'offer': offer,
        'comment_form': comment_form,
        'comment_list': comment_list,
        'want_users': want_users,
    }
    return render(request, 'offer_view.html', context=context)


@login_required
def my_offers(request):
    sell_offers = Offer.objects.filter(seller=request.user).filter(seller_done=False)
    buy_offers = Offer.objects.filter(buyer=request.user).filter(buyer_done=False)
    context = {
        'sell_offers': sell_offers,
        'buy_offers': buy_offers,
    }
    return render(request, 'my_offers.html', context=context)


@login_required
def past_transaction(request):
    past_sell_offers = Offer.objects.filter(seller=request.user).filter(seller_done=True)
    past_buy_offers = Offer.objects.filter(buyer=request.user).filter(buyer_done=True)
    context = {
        'past_sell_offers': past_sell_offers,
        'past_buy_offers': past_buy_offers,
    }
    return render(request, 'past_transaction.html', context=context)


@login_required
def notification(request):
    qs = request.user.notifications.order_by('-date_time')
    paginator = Paginator(qs, 10)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    object_qs = page_obj.object_list
    html_list = [a.html_form() for a in object_qs]
    new_notification = request.user.unread_notification
    request.user.unread_notification = 0
    request.user.save()
    context = {
        'page_obj': page_obj,
        'html_list': html_list,
        'object_qs': object_qs,
        'new_notification': new_notification,
        'is_paginated': True,
    }
    return render(request, 'notifications.html', context=context)


@login_required
def setting(request):
    if request.method == 'POST':
        notify_form = NotificationSettingForm(request.POST)
        if notify_form.is_valid():
            data = notify_form.cleaned_data
            if data['notify_books']:
                request.user.notify_books.set(data['notify_books'])
            request.user.notify_comment = data['notify_comment']
            request.user.notify_new_offer = data['notify_new_offer']
            request.user.notify_sold_to_user = data['notify_sold_to_user']
            request.user.notify_sold_to_other = data['notify_sold_to_other']
            request.user.notify_new_want = data['notify_new_want']
            request.user.save()
    else:
        notify_form = NotificationSettingForm(initial={
            'notify_books': request.user.notify_books.all(),
            'notify_comment': request.user.notify_comment,
            'notify_new_offer': request.user.notify_new_offer,
            'notify_sold_to_user': request.user.notify_sold_to_user,
            'notify_sold_to_other': request.user.notify_sold_to_other,
            'notify_new_want': request.user.notify_new_want,
        })
    context = {
        'notify_form': notify_form,
    }
    return render(request, 'setting.html', context=context)


@permission_required('load_data')
def load_data(request):
    f_subject = open('ksa_books_app/data/subject.txt', 'r', encoding='utf-8')
    subjects = f_subject.read().splitlines()
    subjects_inst = []
    for s in subjects:
        subjects_inst.append(Subject(name=s))
    Subject.objects.all().delete()
    Subject.objects.bulk_create(subjects_inst)

    COURSE_VARIABLE_NUM = 2
    (SUBJECT, NAME) = tuple(range(COURSE_VARIABLE_NUM))
    f_course = open('ksa_books_app/data/course.txt', 'r', encoding='utf-8')
    courses = f_course.read().splitlines()
    c = [courses[i:i+COURSE_VARIABLE_NUM+1] for i in range(0, len(courses), COURSE_VARIABLE_NUM+1)]
    # plus 1 for blank lines
    courses_inst = []
    for i in range(len(c)):
        courses_inst.append(Course(subject=Subject.objects.get(name=c[i][SUBJECT]), name=c[i][NAME], open=True))
    Course.objects.all().delete()
    Course.objects.bulk_create(courses_inst)

    BOOK_VARIABLE_NUM = 7
    (TITLE, AUTHOR, COURSES, PUBLISHER, ISBN, LIST_PRICE, GROUP_PRICE) = tuple(range(BOOK_VARIABLE_NUM))
    f_book = open('ksa_books_app/data/book.txt', 'r', encoding='utf-8')
    books = f_book.read().splitlines()
    b = [books[i:i+BOOK_VARIABLE_NUM+1] for i in range(0, len(books), BOOK_VARIABLE_NUM+1)]  # plus 1 for blank lines
    books_inst = []
    Book.objects.all().delete()
    for i in range(len(b)):
        list_price = None if int(b[i][LIST_PRICE]) == 0 else int(b[i][LIST_PRICE])
        group_price = None if int(b[i][GROUP_PRICE]) == 0 else int(b[i][GROUP_PRICE])
        books_inst.append(Book(title=b[i][TITLE], author=b[i][AUTHOR], publisher=b[i][PUBLISHER], isbn=b[i][ISBN],
                               list_price=list_price, group_price=group_price, using=True))
        books_inst[i].save()
        course_list = b[i][COURSES].split(',')
        books_inst[i].subject = Course.objects.get(name=course_list[0]).subject
        for c in course_list:
            books_inst[i].courses.add(Course.objects.get(name=c))
        books_inst[i].save()
    context = dict()
    return render(request, 'load_data.html', context=context)