
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ms_maps', '0004_subaisle_subcategories'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aisle',
            name='number',
        ),
        migrations.RemoveField(
            model_name='subaisle',
            name='number',
        ),
        migrations.AddField(
            model_name='aisle',
            name='code',
            field=models.CharField(max_length=10, null=True, verbose_name='code'),
        ),
        migrations.AddField(
            model_name='subaisle',
            name='code',
            field=models.CharField(max_length=10, null=True, verbose_name='code'),
        ),
        migrations.AlterField(
            model_name='maptile',
            name='subaisle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ms_maps.subaisle', verbose_name='subaisle'),
        ),
        migrations.AlterField(
            model_name='maptile',
            name='tile_type',
            field=models.CharField(choices=[('entrance', 'entrance'), ('exit', 'exit'), ('ee', 'entrance + exit'), ('register', 'register'), ('product', 'product'), ('subaisle', 'subaisle'), ('space', 'space')], max_length=10, verbose_name='tile type'),
        ),
        migrations.AlterField(
            model_name='productlocation',
            name='subaisle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ms_maps.subaisle', verbose_name='subaisle'),
        ),
    ]
