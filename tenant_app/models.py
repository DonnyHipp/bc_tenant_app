from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class User(AbstractUser):
    username = None
    email = models.EmailField(
        _("email address"),
        unique=True,
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.email


class Message(models.Model):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sent_messages"
    )
    recipients = models.ManyToManyField(User, related_name="received_messages")
    subject = models.CharField(max_length=255)
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True, verbose_name="Активный статус сообщения")
    file = models.FileField(upload_to="message_files/", null=True, blank=True)

    def __str__(self):
        return f"{self.subject} ({self.date_sent})"


class MesIn(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="mesin_user")
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, related_name="mesin_message"
    )
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} - {self.message}"


class MailingList(models.Model):
    name = models.CharField(max_length=255)
    members = models.ManyToManyField(User, related_name="mailing_lists")

    def __str__(self):
        return self.name


@receiver(m2m_changed, sender=Message.recipients.through)
def create_mesin(sender, instance, action, model, **kwargs):
    if action == "post_add":
        for user in instance.recipients.all():
            MesIn.objects.create(user=user, message=instance, active=True)
