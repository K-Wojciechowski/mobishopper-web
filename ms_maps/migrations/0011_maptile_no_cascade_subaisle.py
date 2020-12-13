
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ms_maps', '0010_add_aisle_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maptile',
            name='subaisle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ms_maps.subaisle', verbose_name='subaisle'),
        ),
    ]
