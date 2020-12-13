
from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('ms_userdata', '0002_clean_up_foreignkeys'),
    ]

    operations = [
        migrations.AddField(
            model_name='couponsetuse',
            name='is_used',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='couponsetuse',
            name='valid_until',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='couponuse',
            name='is_used',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='couponuse',
            name='valid_until',
            field=models.DateTimeField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
