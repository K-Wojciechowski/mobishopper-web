
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ms_maps', '0005_aisle_codes_maptile_fixes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aisle',
            name='date_ended',
        ),
        migrations.RemoveField(
            model_name='aisle',
            name='date_started',
        ),
        migrations.RemoveField(
            model_name='subaisle',
            name='date_ended',
        ),
        migrations.RemoveField(
            model_name='subaisle',
            name='date_started',
        ),
        migrations.AddField(
            model_name='aisle',
            name='visible',
            field=models.BooleanField(default=True, verbose_name='visible'),
        ),
        migrations.AddField(
            model_name='map',
            name='replaced_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ms_maps.map', verbose_name='replaced by'),
        ),
        migrations.AddField(
            model_name='subaisle',
            name='visible',
            field=models.BooleanField(default=True, verbose_name='visible'),
        ),
        migrations.AlterField(
            model_name='aisle',
            name='code',
            field=models.CharField(blank=True, default='', max_length=10, verbose_name='code'),
        ),
        migrations.AlterField(
            model_name='productlocation',
            name='is_auto',
            field=models.BooleanField(default=False, verbose_name='is auto-generated'),
        ),
        migrations.AlterField(
            model_name='subaisle',
            name='code',
            field=models.CharField(blank=True, default='', max_length=10, verbose_name='code'),
        ),
    ]
