# Generated by Django 3.2.11 on 2022-12-12 14:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_product_discount_price'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductWeight',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('weight', models.CharField(blank=True, help_text='ex. 1, 1.5, 2, 5, 10.', max_length=10, null=True, verbose_name='Product Weight')),
                ('qty', models.PositiveIntegerField(default=1, verbose_name='Quantity')),
                ('price', models.FloatField(max_length=100)),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='products.product')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]