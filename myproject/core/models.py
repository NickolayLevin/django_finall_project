from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from django.core.validators import MinLengthValidator
from django_ckeditor_5.fields import CKEditor5Field

class User(AbstractUser):
    """
    Модель пользователя. Расширение от модели AbstractUser
    """
    email = models.EmailField(
        unique=True,
        verbose_name='Email адрес'
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name='Email подтверждён'
    )
    verification_code = models.CharField(
        max_length=6,
        blank=True,
        null=True,
        verbose_name='Код подтверждения'
    )
    verification_code_expires = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Срок действия кода'
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.',
        related_name='%(app_label)s_%(class)s_groups',
        related_query_name='user'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permission',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='%(app_label)s_%(class)s_user_permissions',
        related_query_name='user',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

class Category(models.TextChoices):
    """
    Выбор категорий
    """
    TANKS = 'tanks', 'Танки'
    HEALERS = 'healers', 'Хилы'
    DD = 'dd', 'ДД'
    MERCHANTS = 'merchants', 'Торговцы'
    GUILDMASTERS = 'guildmasters', 'Гилдмастеры'
    QUESTGIVERS = 'questgivers', 'Квестгиверы'
    BLACKSMITHS = 'blacksmiths', 'Кузнецы'
    LEATHERWORKERS = 'leatherworkers', 'Кожевники'
    POTIONMAKERS = 'potionmakers', 'Зельевары'
    SPELLMASTERS = 'spellmasters', 'Мастера заклинаний'

class Advertisement(models.Model):
    """
    Модель объявления. 
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='advertisements',
        verbose_name='Автор'
    )
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(5)],
        verbose_name='Заголовок'
    )
    content = CKEditor5Field(
        verbose_name='Текст объявления',
        config_name='extends'  
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        verbose_name='Категория'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активно'
    )
    viewed_by = models.ManyToManyField(
        User,
        related_name='viewed_ad',
        blank=True,
        verbose_name='Количество просмотров'
    )
    liked_by = models.ManyToManyField(
        User,
        related_name='liked_ad',
        verbose_name='Лайки',
        blank=True
    )

    def __str__(self):
        return f'{self.title} ({self.category})'
    
    def views_count(self):
        return self.viewed_by.count() 

    def likes_count(self):
        return self.liked_by.count()  
    
    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at']

class Response(models.Model):
    """
    Модель отклика на объявления.
    """
    advertisement = models.ForeignKey(
        Advertisement,
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name='Объявление'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sent_responses',
        verbose_name='Автор отклика'
    )
    text = models.TextField(
        validators=[MinLengthValidator(10)],
        verbose_name='Текст отклика'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    is_accepted = models.BooleanField(
        default=False,
        verbose_name='Принят'
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='Удалён'
    )

    def __str__(self):
        return f'Отклик от {self.author} на {self.advertisement.title[:30]}...'
    
    class Meta:
        verbose_name = 'Отклик'
        verbose_name_plural = 'Отклики'
        ordering = ['-created_at']
        unique_together = ('advertisement', 'author')


class NewsLetter(models.Model):
    """
    Модель письма для рассылки
    """
    subject = models.CharField(max_length=200, verbose_name='Тема')
    content = CKEditor5Field(verbose_name='Содержание', config_name='extends')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    send_at = models.DateTimeField(null=True, blank=True, verbose_name='Отправлено')
    is_sent = models.BooleanField(default=False, verbose_name='Отправлено')

    def __str__(self):
        return self.subject
    
    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'
        ordering = ['-created_at']