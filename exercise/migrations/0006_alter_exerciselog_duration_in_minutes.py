# Generated by Django 3.2.25 on 2024-11-12 01:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exercise', '0005_exerciselog_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exerciselog',
            name='duration_in_minutes',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]