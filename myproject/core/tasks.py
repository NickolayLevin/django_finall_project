from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import NewsLetter, User

@shared_task
def send_newsletter_task(newsletter_id):
    """
    Таска отправки эл. письма
    """
    newsletter = NewsLetter.objects.get(id=newsletter_id)
    
    if newsletter.is_sent:
        return 'Already sent!'
    
    users = User.objects.filter(is_verified=True)

    for user in users:
        send_mail(
            subject=newsletter.subject,
            message=newsletter.content,
            html_message=newsletter.content,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True
        )
    
    newsletter.is_sent = True
    newsletter.sent_at = timezone.now()
    newsletter.save()

    return 'Sent to {} users'.format(users.count())
