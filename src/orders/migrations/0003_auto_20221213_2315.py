# Generated by Django 3.2.11 on 2022-12-13 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20221011_1325'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderproductdetail',
            name='adminRemarkStatus',
            field=models.CharField(choices=[('None', 'None'), ('Rejected', 'Rejected'), ('Approved', 'Approved')], default='None', max_length=100, verbose_name='Admin Remark'),
        ),
        migrations.AddField(
            model_name='orderproductdetail',
            name='taxRate',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, editable=False, max_digits=12, null=True, verbose_name='Tax Rate'),
        ),
        migrations.AddField(
            model_name='orderproductdetail',
            name='userOrderedProductStatus',
            field=models.CharField(choices=[('None', 'None'), ('Pending', 'Pending'), ('Order Placed', 'Order Placed'), ('On The Way', 'On The Way'), ('Delivered', 'Delivered'), ('Cancelled', 'Cancelled'), ('Returned', 'Returned'), ('Replace', 'Replace')], default='None', max_length=100, verbose_name='User Order Status'),
        ),
    ]
