from django.urls import path
# from django.views.decorators.cache import cache_page
from . import views
from .views import ContactsView

app_name = 'contacts'

urlpatterns = [
    path('', ContactsView.as_view(), name='index'),
    path('contact-success/', views.ContactSuccessView.as_view(), name='contact_success'),
]