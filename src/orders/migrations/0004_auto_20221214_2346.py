# Generated by Django 3.2.11 on 2022-12-14 18:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20221213_2315'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderdetail',
            name='totalOrderdQty',
            field=models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Total Orderd Quantity'),
        ),
        migrations.AddField(
            model_name='orderdetail',
            name='userRemark',
            field=models.CharField(blank=True, choices=[('None', 'None'), ('Fully Return', 'Fully Return'), ('Partially Return', 'Partially Return'), ('Replace', 'Replace')], default='None', max_length=100, null=True, verbose_name='User Remark'),
        ),
        migrations.AddField(
            model_name='orderproductdetail',
            name='returnId',
            field=models.CharField(blank=True, default='None', editable=False, max_length=25, null=True, verbose_name='Return Id'),
        ),
        migrations.AddField(
            model_name='orderproductdetail',
            name='returnQty',
            field=models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Return Quantity'),
        ),
        migrations.AddField(
            model_name='orderproductdetail',
            name='userRemarkStatus',
            field=models.CharField(choices=[('None', 'None'), ('Fully Return', 'Fully Return'), ('Partially Return', 'Partially Return'), ('Replace', 'Replace')], default='None', max_length=100, verbose_name='User Remark Status'),
        ),
        migrations.AlterField(
            model_name='orderproductdetail',
            name='userOrderedProductStatus',
            field=models.CharField(choices=[('None', 'None'), ('Pending', 'Pending'), ('Order Placed', 'Order Placed'), ('On The Way', 'On The Way'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled')], default='None', max_length=100, verbose_name='User Order Status'),
        ),
    ]
