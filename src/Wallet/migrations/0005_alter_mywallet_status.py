# Generated by Django 3.2.11 on 2022-12-13 18:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Wallet', '0004_alter_mywallet_trasactionamt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mywallet',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('active', 'Active'), ('inactive', 'Inactive')], default='pending', editable=False, max_length=25, verbose_name='Wallet status'),
        ),
    ]
