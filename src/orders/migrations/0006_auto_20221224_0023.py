# Generated by Django 3.2.11 on 2022-12-23 18:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_remove_orderproductdetail_userorderedproductstatus'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderproductdetail',
            name='adminRemarkStatus',
        ),
        migrations.RemoveField(
            model_name='orderproductdetail',
            name='returnId',
        ),
        migrations.RemoveField(
            model_name='orderproductdetail',
            name='returnQty',
        ),
        migrations.RemoveField(
            model_name='orderproductdetail',
            name='userRemarkStatus',
        ),
        migrations.AlterField(
            model_name='orderdetail',
            name='order_status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('Order Placed', 'Order Placed'), ('On The Way', 'On The Way'), ('Delivered', 'Delivered'), ('Fully Return', 'Fully Return'), ('Partially Return', 'Partially Return'), ('Replace', 'Replace'), ('Cancelled', 'Cancelled')], default='Pending', max_length=100, verbose_name='Order Status'),
        ),
        migrations.AlterField(
            model_name='orderdetail',
            name='userRemark',
            field=models.CharField(blank=True, choices=[('None', 'None'), ('Fully Return', 'Fully Return'), ('Partially Return', 'Partially Return'), ('Replace', 'Replace'), ('Cancelled', 'Cancelled')], default='None', max_length=100, null=True, verbose_name='User Remark'),
        ),
        migrations.CreateModel(
            name='ReturnProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('orderNumber', models.CharField(blank=True, max_length=30, null=True)),
                ('return_id', models.CharField(blank=True, editable=False, max_length=25, null=True, unique=True, verbose_name='Return Number')),
                ('returnQty', models.PositiveIntegerField(blank=True, default=0, null=True, verbose_name='Return Quantity')),
                ('userRemarkStatus', models.CharField(choices=[('None', 'None'), ('Fully Return', 'Fully Return'), ('Partially Return', 'Partially Return'), ('Replace', 'Replace'), ('Cancelled', 'Cancelled')], default='None', max_length=100, verbose_name='User Remark Status')),
                ('refundAmt', models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=10, null=True, verbose_name='Refund Amount')),
                ('adminRemarkStatus', models.CharField(choices=[('None', 'None'), ('Rejected', 'Rejected'), ('Approved', 'Approved')], default='None', max_length=100, verbose_name='Admin Remark')),
                ('orderedProduct', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.orderproductdetail')),
            ],
            options={
                'verbose_name_plural': 'Return Product',
                'ordering': ['-created_at'],
            },
        ),
    ]