
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ms_maps', '0007_map_tile_color_block'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maptile',
            name='map',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tiles', to='ms_maps.map', verbose_name='map'),
        ),
    ]
