
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ms_products', '0022_rename_generic_subaisle_finish'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='genericsubaisle',
            name='subcategory',
        ),
        migrations.AddField(
            model_name='genericsubaisle',
            name='subcategories',
            field=models.ManyToManyField(to='ms_products.Subcategory', verbose_name='subcategories'),
        ),
    ]
