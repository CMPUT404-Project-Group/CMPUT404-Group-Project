# Generated by Django 3.2.8 on 2021-10-24 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_sharedpost'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='image_link',
            field=models.TextField(blank=True, null=True),
        ),
    ]
