
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ms_maps', '0001_initial'),
        ('ms_products', '0020_split_deals_into_separate_app'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='GenericSubAisle',
            new_name='GenericSubaisle2',
        ),
    ]
