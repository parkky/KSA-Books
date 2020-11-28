from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='home/')),
    path('home/', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('book-list/', views.BookListView.as_view(), name='book-list'),
    path('sell/', views.offer_create, name='sell'),
    path('search/', views.search_view, name='search'),
    path('offer/<int:pk>', views.offer_view, name='check-offer'),
    path('offer/<int:pk>/update', views.OfferUpdate.as_view(), name='update-offer'),
    path('offer/<int:pk>/delete', views.OfferDelete.as_view(), name='delete-offer'),
    path('my-offers/', views.my_offers, name='my-offers'),
    path('past-transaction/', views.past_transaction, name='past-transaction'),
    path('notification/', views.notification, name='notification'),
    path('setting/', views.setting, name='setting'),
    path('load-data/', views.load_data, name='load-data'),
    path('change-name', views.name_update, name='change-name'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
]
