
import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ms_baseline', '0010_update_field_verbose_names'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ms_products', '0019_vendor_date_ranged'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('date_added', models.DateTimeField(auto_now_add=True, verbose_name='date added')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='date modified')),
                ('date_started', models.DateTimeField(blank=True, null=True, verbose_name='valid from')),
                ('date_ended', models.DateTimeField(blank=True, null=True, verbose_name='valid until')),
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_global', models.BooleanField(default=False, verbose_name='is global')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='price')),
                ('one_use', models.BooleanField(default=True, verbose_name='is one use only')),
                ('require_account', models.BooleanField(default=False, verbose_name='require log in')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ms_products.product', verbose_name='product')),
                ('stores', models.ManyToManyField(blank=True, to='ms_baseline.Store', verbose_name='stores')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='user')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='coupon code')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Deal',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True, verbose_name='date added')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='date modified')),
                ('date_started', models.DateTimeField(blank=True, null=True, verbose_name='valid from')),
                ('date_ended', models.DateTimeField(blank=True, null=True, verbose_name='valid until')),
                ('is_global', models.BooleanField(default=False, verbose_name='is global')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10, verbose_name='price')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ms_products.product', verbose_name='product')),
                ('stores', models.ManyToManyField(blank=True, to='ms_baseline.Store', verbose_name='stores')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='user')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CouponSet',
            fields=[
                ('date_added', models.DateTimeField(auto_now_add=True, verbose_name='date added')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='date modified')),
                ('date_started', models.DateTimeField(blank=True, null=True, verbose_name='valid from')),
                ('date_ended', models.DateTimeField(blank=True, null=True, verbose_name='valid until')),
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('one_use', models.BooleanField(default=False, verbose_name='is one use only')),
                ('require_account', models.BooleanField(default=False, verbose_name='require log in')),
                ('coupons', models.ManyToManyField(to='ms_deals.Coupon', verbose_name='coupons')),
                ('is_global', models.BooleanField(default=False, verbose_name='is global')),
                ('stores', models.ManyToManyField(blank=True, to='ms_baseline.Store', verbose_name='stores')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, verbose_name='coupon code')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
