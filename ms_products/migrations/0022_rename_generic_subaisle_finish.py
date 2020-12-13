
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ms_maps', '0001_initial'),
        ('ms_products', '0021_rename_generic_subaisle_start'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='GenericSubaisle2',
            new_name='GenericSubaisle',
        ),
    ]
