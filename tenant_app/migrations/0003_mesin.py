# Generated by Django 4.2.1 on 2023-05-15 13:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('tenant_app', '0002_message_mailinglist'),
    ]

    operations = [
        migrations.CreateModel(
            name='MesIn',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('active', models.BooleanField(default=True)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mesin_message', to='tenant_app.message')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mesin_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
