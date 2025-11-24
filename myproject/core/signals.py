from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import User, Response
from django.utils import timezone

@receiver(post_save, sender=User)
def send_verification_code(sender, instance, created, **kwargs):
    """
    Отправка кода подтверждения при регистрации пользователя.
    """
    if created and not instance.is_verified:
        subject = 'Подтверждение регистрации'
        message = f'Ваш код: {instance.verification_code}. Действует 10 минут.'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.email])

@receiver(post_save, sender=Response)
def send_response_notification(sender, instance, created, **kwargs):
    """
    Уведомление автору о новом отклике
    """
    if created:
        ad = instance.advertisement
        subject = 'Новый отклик на объявление'
        message = f'На Ваше объявление "{ad.title}" оставлен отклик: {instance.text}'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [ad.author.email])

@receiver(post_save, sender=Response)
def send_accept_notification(sender, instance, created, **kwargs):
    """
    Уведомление об успешном принятии отклика.
    """
    if instance.is_accepted and kwargs.get('update_fields') == {'is_accepted'}:
        subject = 'Ваш отклик принят!'
        message = f'Ваш отклик на объявление "{instance.advertisement.title}" принят автором.'
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [instance.author.email])
