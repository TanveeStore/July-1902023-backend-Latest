# Generated by Django 3.2.11 on 2022-12-05 11:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Wallet', '0002_alter_mywallet_walletbalance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mywallet',
            name='walletBalance',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, editable=False, max_digits=12, null=True, verbose_name='Wallet Balance'),
        ),
    ]