# Generated by Django 4.2.5 on 2023-10-09 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0004_user_groups'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='status',
            field=models.CharField(choices=[('1', 'Publish'), ('0', 'Unpublish'), ('-1', 'Trash')], default='1', max_length=100),
        ),
    ]
