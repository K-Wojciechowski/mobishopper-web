
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ms_deals', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='couponset',
            name='one_use',
            field=models.BooleanField(default=True, verbose_name='is one use only'),
        ),
    ]
