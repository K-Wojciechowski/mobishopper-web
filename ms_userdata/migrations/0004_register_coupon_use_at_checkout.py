
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ms_baseline', '0012_checkoutapikey'),
        ('ms_userdata', '0003_coupon_validity_use_tracking'),
    ]

    operations = [
        migrations.AddField(
            model_name='couponsetuse',
            name='used_date',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='couponsetuse',
            name='used_with',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ms_baseline.checkoutapikey'),
        ),
        migrations.AddField(
            model_name='couponuse',
            name='used_date',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='couponuse',
            name='used_with',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='ms_baseline.checkoutapikey'),
        ),
    ]
