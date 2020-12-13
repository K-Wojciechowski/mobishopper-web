
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ms_products', '0018_vendor_visible'),
    ]

    operations = [
        migrations.AddField(
            model_name='vendor',
            name='date_ended',
            field=models.DateTimeField(blank=True, null=True, verbose_name='valid until'),
        ),
        migrations.AddField(
            model_name='vendor',
            name='date_started',
            field=models.DateTimeField(blank=True, null=True, verbose_name='valid from'),
        ),
        migrations.AddField(
            model_name='vendor',
            name='replaced_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ms_products.vendor', verbose_name='replaced by'),
        ),
    ]
