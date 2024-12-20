# Generated by Django 5.1 on 2024-11-22 16:30

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('biblioteca', '0004_rename_partituras_partitura_alter_partitura_table'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='partitura',
            name='usuario',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='partituras', to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
