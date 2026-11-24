from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models import Q
from django.utils import timezone


@shared_task
def send_welcome_email_task(user_id):
    user = get_user_model().objects.get(pk=user_id)
    send_mail(
        subject="Добро пожаловать!",
        message=f"Здравствуйте, {user.username}! Спасибо за регистрацию.",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
    )
    return f"Приветственное письмо отправлено: {user.email}"


@shared_task
def clean_inactive_users_task(days=30):
    if days < 0:
        raise ValueError("days должен быть неотрицательным числом")

    cutoff = timezone.now() - timedelta(days=days)
    inactive_users = get_user_model().objects.filter(is_active=False).filter(
        Q(last_login__lt=cutoff)
        | Q(last_login__isnull=True, date_joined__lt=cutoff)
    )
    count = inactive_users.count()
    inactive_users.delete()
    return f"Удалено неактивных пользователей: {count}"


@shared_task
def send_daily_admin_report_task():
    user_model = get_user_model()
    role_counts = {
        role: user_model.objects.filter(groups__name=role).distinct().count()
        for role in ("ADMIN", "MODERATOR", "USER")
    }
    report = "Статистика пользователей по ролям: " + ", ".join(
        f"{role}={count}" for role, count in role_counts.items()
    )
    print(report)
    return role_counts
