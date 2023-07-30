# Generated by Django 3.2.11 on 2022-12-26 15:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_auto_20221226_2119'),
        ('orders', '0006_auto_20221224_0023'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderproductdetail',
            name='product_weight',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='product_Weight', to='products.productweight'),
        ),
        migrations.AddField(
            model_name='orderproductdetail',
            name='uom',
            field=models.CharField(blank=True, default='N/A', max_length=20, null=True, verbose_name='Unit of Measure'),
        ),
    ]
