# Generated by Django 4.2.18 on 2025-01-29 04:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('drawing', '0003_artwork_description_alter_artwork_image_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='artwork',
            name='processing',
            field=models.BooleanField(default=False),
        ),
    ]
