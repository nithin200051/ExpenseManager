# Generated by Django 4.1.1 on 2023-04-03 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ExpenseMain', '0002_delete_userdetails'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserDetail',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('email', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=100)),
            ],
        ),
    ]