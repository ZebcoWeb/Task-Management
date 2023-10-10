# Generated by Django 4.2.5 on 2023-10-09 08:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('1', 'Publish'), ('0', 'Unpublish'), ('-1', 'Trash')], default='1', max_length=100)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(max_length=500)),
                ('deadline', models.DateTimeField()),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(editable=False, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='task_creator', to=settings.AUTH_USER_MODEL)),
                ('functor', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='task_functor', to=settings.AUTH_USER_MODEL)),
                ('modified_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='task_modifier', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Task',
                'verbose_name_plural': 'Tasks',
                'db_table': 'task',
            },
        ),
    ]