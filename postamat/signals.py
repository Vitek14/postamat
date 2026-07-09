import os

from django.db.models.signals import post_migrate
from django.contrib.auth import get_user_model
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from django.contrib.auth.models import Group

User = get_user_model()


@receiver(post_migrate)
def create_superuser(sender, **kwargs):
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            username=os.getenv('SUPERUSER_NICKNAME'),
            email=os.getenv('SUPERUSER_EMAIL'),
            password=os.getenv('SUPERUSER_PASSWORD'),
        )
