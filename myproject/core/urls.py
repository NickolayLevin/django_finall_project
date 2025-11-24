from django.urls import path, include
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('verify/', VerificationView.as_view(), name='verify'),
    path('', AdListView.as_view(), name='home'),
    path('ads/<int:pk>/', AdDetailView.as_view(), name='ads_detail'),
    path('ads/create/', AdCreateView.as_view(), name='ads_create'),
    path('ads/<int:pk>/edit/', AdUpdateView.as_view(), name='ad_update'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('ads/<int:pk>/respond', ResponseCreateView.as_view(), name='response_create'),
    path('my-responses', MyResponsesView.as_view(), name='my_responses'),
    path('response/<int:pk>/accept', ResponseAcceptView.as_view(), name='response_accept'),
    path('response/<int:pk>/delete', ResponseDeleteView.as_view(), name='response_delete'),
    path('ads/<int:pk>/like/', LikeAdView.as_view(), name='ad_like')
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)