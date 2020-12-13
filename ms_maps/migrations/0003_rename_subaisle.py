
from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ms_products', '0022_rename_generic_subaisle_finish'),
        ('ms_baseline', '0010_update_field_verbose_names'),
        ('ms_maps', '0002_redefine_map_models'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Subaisle2',
            new_name='Subaisle',
        ),
    ]
