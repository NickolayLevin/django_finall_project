from django.contrib import admin
from .models import NewsLetter
from .tasks import send_newsletter_task
# Register your models here.

class NewsLetterAdmin(admin.ModelAdmin):
    """
    Регистрация в панели админа новостной рассылки
    """
    list_display = ('subject', 'created_at', 'send_at', 'is_sent')
    readonly_fields = ('send_at', 'is_sent')
    fields = ('subject', 'content')

    actions = ['send_newsletter']

    def send_newsletter(self, request, queryset):
        for newsletter in queryset:
            if not newsletter.is_sent:
                send_newsletter_task.delay(newsletter.id)
                self.message_user(request, f'Рассылка "{newsletter.subject}" поставлена в очередь на отправку.')
            else:
                self.message_user(request, f'Рассылка "{newsletter.subject}" уже отправлена.', level='warning')
    
    send_newsletter.short_description = 'Отправить выбранные рассылки'
    
admin.site.register(NewsLetter, NewsLetterAdmin)