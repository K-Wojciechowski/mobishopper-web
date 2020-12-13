
import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ms_deals', '0001_initial'),
        ('ms_products', '0001_initial'),
        ('ms_baseline', '0010_update_field_verbose_names'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ShoppingList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True, verbose_name='date added')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='date modified')),
                ('price_cached', models.DecimalField(decimal_places=2, max_digits=10)),
                ('sharing_uuid', models.UUIDField(default=None, null=True, unique=True)),
                ('shared_with', models.ManyToManyField(related_name='shared_with', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('store', models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to='ms_baseline.store')),
                ('completion', models.IntegerField(default=0)),
                ('name', models.CharField(blank=True, max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CouponUse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True, verbose_name='date added')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='date modified')),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ms_deals.coupon')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ms_baseline.store')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CouponSetUse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True, verbose_name='date added')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='date modified')),
                ('coupon_set', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ms_deals.couponset')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ms_baseline.store')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ShoppingListEntry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True, verbose_name='date added')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='date modified')),
                ('amount', models.DecimalField(decimal_places=3, max_digits=10)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='entries', to='ms_userdata.shoppinglist')),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ms_products.product')),
                ('product_upgraded_from', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='ms_products.product')),
                ('bought', models.BooleanField(default=False)),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='ms_baseline.msuser')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ShoppingListInvite',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('date_added', models.DateTimeField(auto_now_add=True, verbose_name='date added')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='date modified')),
                ('email', models.EmailField(max_length=254)),
                ('used', models.BooleanField()),
                ('list', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ms_userdata.shoppinglist')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddConstraint(
            model_name='shoppinglistentry',
            constraint=models.UniqueConstraint(fields=('list', 'product'), name='unique_product'),
        ),
        migrations.RemoveField(
            model_name='couponsetuse',
            name='id',
        ),
        migrations.RemoveField(
            model_name='couponuse',
            name='id',
        ),
        migrations.RemoveField(
            model_name='shoppinglistentry',
            name='price',
        ),
        migrations.AddField(
            model_name='couponsetuse',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False),
        ),
        migrations.AddField(
            model_name='couponuse',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='couponsetuse',
            name='user',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='couponuse',
            name='user',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='shoppinglistinvite',
            name='used',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='shoppinglist',
            name='price_cached',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='shoppinglist',
            name='shared_with',
            field=models.ManyToManyField(blank=True, related_name='shared_with', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='shoppinglist',
            name='sharing_uuid',
            field=models.UUIDField(blank=True, default=None, null=True, unique=True),
        ),
    ]
