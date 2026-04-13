from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Static pages
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),
    path('faq/', views.FAQView.as_view(), name='faq'),
    # path('size-guide/', views.SizeGuideView.as_view(), name='size_guide'),
    path('shipping/', views.ShippingInfoView.as_view(), name='shipping_info'),
    path('returns/', views.ReturnsView.as_view(), name='returns'),
    path('privacy/', views.PrivacyPolicyView.as_view(), name='privacy_policy'),
    path('terms/', views.TermsOfServiceView.as_view(), name='terms_of_service'),
    
    # Newsletter
    # path('newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter_subscribe'),
]
