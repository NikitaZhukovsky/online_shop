# Generated by Django 5.0.3 on 2024-04-10 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0004_alter_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='is_notif_sent',
            field=models.BooleanField(default=False),
        ),
    ]
