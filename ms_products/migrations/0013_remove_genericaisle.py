
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ms_maps", "0001_initial"),
        ("ms_products", "0012_standardmetafield_units_subcategories"),
    ]

    operations = [
        migrations.RemoveField(model_name="genericsubaisle", name="parent"),
        migrations.AlterField(
            model_name="product",
            name="extra_metadata_dict",
            field=models.JSONField(blank=True, default=dict, verbose_name="properties (cache)"),
        ),
        migrations.AlterField(
            model_name="product",
            name="extra_metadata_raw",
            field=models.JSONField(blank=True, default=list, verbose_name="properties"),
        ),
        migrations.DeleteModel(name="GenericAisle"),
    ]
