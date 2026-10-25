from django.urls import path
from django.views.generic import TemplateView

from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('health/', views.health, name='health'),
    path('sitemap.xml', views.sitemap, name='sitemap'),
    path('robots.txt', views.robots, name='robots'),
    path('contact/', TemplateView.as_view(template_name='pages/contact.html'), name='contact'),
    path('privacy/', TemplateView.as_view(template_name='pages/privacy.html'), name='privacy'),
    path('terms/', TemplateView.as_view(template_name='pages/terms.html'), name='terms'),
    path('destinations/', views.destinations, name='destinations'),
    path('photo-credits/', views.photo_credits, name='photo_credits'),
    path('enquiry/', views.enquiry, name='enquiry'),
    path('thank-you/', views.thank_you, name='thank_you'),
    # Must stay last: any other single-segment address is looked up as a published ContentPage slug.
    path('<slug:slug>/', views.content_page, name='content_page'),
]
