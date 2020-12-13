
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ms_products', '0023_genericsubaisle_multiple_subcategories'),
        ('ms_maps', '0003_rename_subaisle'),
    ]

    operations = [
        migrations.AddField(
            model_name='subaisle',
            name='subcategories',
            field=models.ManyToManyField(blank=True, to='ms_products.Subcategory', verbose_name='subcategories'),
        ),
    ]
