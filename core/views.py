from django.shortcuts import render, redirect
from django.views.generic import TemplateView, View
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .forms import PasswordResetForm
from orders.models import Order
import json


class LoginView(View):
    template_name = 'core/login.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('products:home')
        form = AuthenticationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'products:home')
                messages.success(request, f'Welcome back, {user.username}!')
                return redirect(next_url)
        return render(request, self.template_name, {'form': form})


class RegisterView(View):
    template_name = 'core/register.html'
    
    def get(self, request):
        if request.user.is_authenticated:
            return redirect('products:home')
        form = UserCreationForm()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            messages.success(request, 'Account created successfully!')
            return redirect('products:home')
        return render(request, self.template_name, {'form': form})


class LogoutView(View):
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('products:home')


from .models import StaticPage

class AboutView(TemplateView):
    template_name = 'core/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = StaticPage.objects.filter(slug='about').first()
        return context


class ContactView(View):
    template_name = 'core/contact.html'
    
    def get(self, request):
        page = StaticPage.objects.filter(slug='contact').first()
        return render(request, self.template_name, {'page': page})
    
    def post(self, request):
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        page = StaticPage.objects.filter(slug='contact').first()
        
        if name and email and message:
            try:
                # Send email notification
                subject = f'Contact Form Message from {name}'
                email_message = f'Name: {name}\nEmail: {email}\n\nMessage:\n{message}'
                
                send_mail(
                    subject=subject,
                    message=email_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
                messages.success(request, 'Your message has been sent successfully!')
            except Exception as e:
                messages.error(request, 'There was an error sending your message. Please try again.')
        else:
            messages.error(request, 'Please fill in all required fields.')
        
        return render(request, self.template_name, {'page': page})


class FAQView(TemplateView):
    template_name = 'core/faq.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = StaticPage.objects.filter(slug='faq').first()
        return context


@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    template_name = 'core/profile.html'
    
    def get(self, request):
        # Order model currently does not have a 'user' field
        # recent_orders = Order.objects.filter(user=request.user).order_by('-created_at')[:5]
        context = {
            'recent_orders': [],
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class PasswordResetView(View):
    def post(self, request):
        form = PasswordResetForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            # Update the session to prevent the user from being logged out
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been updated successfully!')
            return redirect('core:profile')
        else:
            # Get error message from form
            error = list(form.errors.values())[0][0] if form.errors else "Invalid form submission."
            messages.error(request, error)
            return redirect('core:profile')


class SizeGuideView(TemplateView):
    template_name = 'core/size_guide.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = StaticPage.objects.filter(slug='size-guide').first()
        return context


class ShippingInfoView(TemplateView):
    template_name = 'core/shipping_info.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = StaticPage.objects.filter(slug='shipping').first()
        return context


class ReturnsView(TemplateView):
    template_name = 'core/returns.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = StaticPage.objects.filter(slug='returns').first()
        return context


class PrivacyPolicyView(TemplateView):
    template_name = 'core/privacy_policy.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = StaticPage.objects.filter(slug='privacy').first()
        return context


class TermsOfServiceView(TemplateView):
    template_name = 'core/terms_of_service.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page'] = StaticPage.objects.filter(slug='terms').first()
        return context


# TrackOrderView moved to orders app


class ProfileView(TemplateView):
    template_name = 'core/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # if self.request.user.is_authenticated:
        #     from orders.models import Order
        #     context['recent_orders'] = Order.objects.filter(
        #         user=self.request.user
        #     ).order_by('-created_at')[:5]
        context['recent_orders'] = []
        return context


# class NewsletterSubscribeView(View):
#     def post(self, request):
#         try:
#             data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
#             email = data.get('email')
            
#             if email:
#                 # Here you would typically save to a newsletter model
#                 # For now, we'll just send a confirmation email
#                 try:
#                     send_mail(
#                         subject='Newsletter Subscription Confirmed',
#                         message=f'Thank you for subscribing to our newsletter with email: {email}',
#                         from_email=settings.DEFAULT_FROM_EMAIL,
#                         recipient_list=[email],
#                         fail_silently=False,
#                     )
                    
#                     return JsonResponse({
#                         'success': True,
#                         'message': 'Successfully subscribed to newsletter!'
#                     })
#                 except Exception as e:
#                     return JsonResponse({
#                         'success': False,
#                         'error': 'Failed to send confirmation email.'
#                     })
#             else:
#                 return JsonResponse({
#                     'success': False,
#                     'error': 'Email is required.'
#                 })
#         except Exception as e:
#             return JsonResponse({
#                 'success': False,
#                 'error': 'Invalid request.'
#             })
