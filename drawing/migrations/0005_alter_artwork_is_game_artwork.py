# Generated by Django 4.2.18 on 2025-01-29 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drawing', '0004_artwork_processing'),
    ]

    operations = [
        migrations.AlterField(
            model_name='artwork',
            name='is_game_artwork',
            field=models.BooleanField(default=False),
        ),
    ]
