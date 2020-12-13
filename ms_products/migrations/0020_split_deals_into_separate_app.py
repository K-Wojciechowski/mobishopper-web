
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ms_userdata', '0001_initial'),
        ('ms_products', '0019_vendor_date_ranged'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='couponset',
            name='coupons',
        ),
        migrations.RemoveField(
            model_name='deal',
            name='product',
        ),
        migrations.RemoveField(
            model_name='deal',
            name='stores',
        ),
        migrations.RemoveField(
            model_name='deal',
            name='user',
        ),
        migrations.RemoveField(
            model_name='vendor',
            name='visible',
        ),
        migrations.DeleteModel(
            name='Coupon',
        ),
        migrations.DeleteModel(
            name='CouponSet',
        ),
        migrations.DeleteModel(
            name='Deal',
        ),
    ]
