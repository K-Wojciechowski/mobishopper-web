
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ms_maps', '0009_aisle_subaisle_description_optional'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='aisle',
            options={'ordering': ['code', 'name']},
        ),
    ]
