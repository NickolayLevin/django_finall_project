from django.utils import timezone
from django.views.generic import FormView, View
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import *
from .models import *
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.core.exceptions import PermissionDenied
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse


class RegistrationView(FormView):
    """
    View Регистрации
    """
    template_name='registration/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('verify')

    def form_valid(self, form):
        user = form.save()
        self.request.session['user_id'] = user.id
        return super().form_valid(form)
    
class VerificationView(FormView):
    """
    View Верификации
    """
    template_name = 'registration/verify.html'
    form_class = VerificationForm

    def form_valid(self, form):
        user_id = self.request.session.get('user_id')
        if not user_id:
            return redirect('register')

        user = User.objects.get(id=user_id)
        if form.cleaned_data['code'] == user.verification_code and timezone.now() < user.verification_code_expires:
            user.is_verified = True
            user.verification_code = None
            user.verification_code_expires = None
            user.save()
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
            self.request.session.pop('user_id', None) 
            messages.success(self.request, 'Регистрация подтверждена!')
            return redirect('home') 
        else:
            messages.error(self.request, 'Неверный код или истёк срок.')
            return self.form_invalid(form)
        

class AdListView(ListView):
    """
    View Главной страницы(список объявлений)
    """
    model = Advertisement
    template_name = 'ads/list.html'
    context_object_name = 'ads'
    queryset = Advertisement.objects.filter(is_active=True).order_by('-created_at')
    paginate_by = 10
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.GET.get('category')
        if category:
            queryset =queryset.filter(category=category)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = Category.choices
        return context
        
class AdDetailView(DetailView):
    """
    View Детального просмотра объявления 
    """
    model = Advertisement
    template_name = 'ads/detail.html'
    context_object_name = 'ad'

    def get_object(self, queryset = None):
        obj = super().get_object(queryset)
        if self.request.user.is_authenticated and self.request.user not in obj.viewed_by.all():
            obj.viewed_by.add(self.request.user)
        return obj
        
 
     



class AdCreateView(LoginRequiredMixin, CreateView):
    """
    View Создания объявления
    """
    model = Advertisement
    template_name = 'ads/create_ad.html'
    form_class = AdvertisementForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    


class AdUpdateView(LoginRequiredMixin, UpdateView):
    """
    View Изменения объявления
    """
    model = Advertisement
    form_class = AdvertisementForm
    template_name = 'ads/update_ad.html'
    success_url = reverse_lazy('home')  

    def get_object(self):
        obj = get_object_or_404(Advertisement, pk=self.kwargs['pk'])
        if obj.author != self.request.user:
            raise PermissionDenied('Вы не автор этого объявления')
        return obj
    
class CustomLoginView(LoginView):
    """
    View Кастомной страницы логина пользователей
    """
    template_name = 'registration/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        if not user.is_verified:
            messages.error(self.request, 'Ваш email не подтвержден. Проверьте почту.')
            return self.form_invalid('form')
        return super().form_valid(form)

class CustomLogoutView(LogoutView):
    """
    View Кастомной страницы подтверждения выхода пользователей из аккаунта
    """
    template_name = 'registration/logout_confirm.html'
    next_page = '/'
    http_method_names = ['get', 'post', 'options'] 


class ResponseCreateView(LoginRequiredMixin, CreateView):
    """
    View Создания отклика на объявление
    """
    model = Response
    form_class = ResponseForm
    template_name = 'ads/response_ad.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['advertisement'] = get_object_or_404(Advertisement, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        ad = get_object_or_404(Advertisement, pk=self.kwargs['pk'])
        if ad.author == self.request.user:
            messages.error(self.request, 'Нельзя сделать отклик на собственное объявление!')
            return redirect('ads_detail', pk=ad.pk)
        
        if Response.objects.filter(advertisement=ad, author=self.request.user).exists():
            messages.warning(self.request, 'Вы уже отправляли отклик на это объявление.')
            return self.render_to_response(self.get_context_data(form=form))
        
        form.instance.advertisement = ad
        form.instance.author = self.request.user
        response = form.save()

        send_mail(
            subject=f'Новый отклик на «{ad.title}»',
            message=f'Пользователь {self.request.user} оставил отклик:\n{response.text}\n'
                    f'Ссылка: http://127.0.0.1:8000{reverse_lazy('my_responses')}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[ad.author.email],
            fail_silently=False
        )
        messages.success(self.request, 'Отклик отправлен!')
        return redirect('ads_detail', pk=ad.pk)
    

class MyResponsesView(LoginRequiredMixin, ListView):
    """
    View Страницы со всеми отлкиками пользователя на его объявления
    """
    template_name = 'ads/my_responses.html'
    context_object_name = 'responses'

    def get_queryset(self):
        return Response.objects.filter(
            advertisement__author=self.request.user,
            is_deleted=False
            ).select_related('advertisement', 'author')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["ads"] = Advertisement.objects.filter(author=self.request.user)
        context['ad_filter'] = self.request.GET.get('ad', '')
        if context['ad_filter']:
            context['responses'] = context['responses'].filter(advertisement_id=context['ad_filter'])
        return context
    
class ResponseAcceptView(LoginRequiredMixin, View):
    """
    View Принятия отклика на свое объявление 
    """
    def post(self, request, pk):
        response = get_object_or_404(Response, pk=pk)
        if response.advertisement.author != request.user:
            raise PermissionDenied
        response.is_accepted = True
        response.save()

        send_mail(
            subject=f'Ваш отклик принят!',
            message=f'Автор объявления {response.advertisement.title} принял Ваш отклик.\n'
                    f'Ваш текст:\n{response.text}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[response.author.email]
        )
        messages.success(request, 'Отклик принят.')
        return redirect('my_responses')
    
class ResponseDeleteView(LoginRequiredMixin, View):
    """
    View Удаление отклика на свое объявление 
    """
    def post(self, request, pk):
        response = get_object_or_404(Response, pk=pk)
        if response.advertisement.author != request.user:
            raise PermissionError
        response.is_deleted = True
        response.save()
        messages.success(request, 'Отклик удалён.')
        return redirect('my_responses')
    
class LikeAdView(LoginRequiredMixin, View):
    """
    View Поставить лайк на объявление
    """
    def post(self, request, pk):
        ad = get_object_or_404(Advertisement, pk=pk)
        liked = False
        if request.user in ad.liked_by.all():
            ad.liked_by.remove(request.user)
        else:
            ad.liked_by.add(request.user)
            liked = True
        
        data = {
            'liked': liked,
            'likes_count': ad.likes_count()
        }
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':  # Для AJAX
            return JsonResponse(data)
        else: 
            return redirect('ad_detail', pk=pk)