
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ms_maps', '0006_aisle_subaisle_no_date_ranges'),
    ]

    operations = [
        migrations.AddField(
            model_name='maptile',
            name='color',
            field=models.CharField(default='#ff0000', max_length=7, verbose_name='color'),
        ),
        migrations.AddField(
            model_name='maptile',
            name='color_is_light',
            field=models.BooleanField(default=True, verbose_name='color is light'),
        ),
        migrations.AlterField(
            model_name='maptile',
            name='tile_type',
            field=models.CharField(choices=[('entrance', 'entrance'), ('exit', 'exit'), ('ee', 'entrance + exit'), ('register', 'register'), ('product', 'product'), ('subaisle', 'subaisle'), ('space', 'space'), ('block', 'block')], max_length=10, verbose_name='tile type'),
        ),
    ]
