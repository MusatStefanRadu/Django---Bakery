# Generated by Django 5.1.1 on 2024-12-09 11:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Brutarie', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='address',
        ),
        migrations.AlterField(
            model_name='customuser',
            name='birth_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
