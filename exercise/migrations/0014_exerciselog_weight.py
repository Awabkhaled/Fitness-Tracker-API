# Generated by Django 3.2.25 on 2024-11-17 08:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exercise', '0013_remove_exercise_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='exerciselog',
            name='weight',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]