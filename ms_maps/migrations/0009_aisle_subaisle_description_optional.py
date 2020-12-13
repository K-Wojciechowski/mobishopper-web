
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ms_maps', '0008_map_tiles_related_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='aisle',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='subaisle',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='description'),
        ),
    ]
