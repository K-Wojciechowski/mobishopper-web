
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("ms_products", "0011_productgroup_standardize_on_name")]

    operations = [
        migrations.AlterField(
            model_name="standardmetafield",
            name="expected_units",
            field=models.CharField(
                choices=[
                    ("_number", "number"),
                    ("_str", "text"),
                    ("_bool", "yes/no"),
                    ("weight", "weight"),
                    ("volume", "volume"),
                    ("area", "area"),
                    ("size", "size"),
                    ("_custom_set", "custom from list"),
                    ("_user", "custom user-provided"),
                ],
                max_length=16,
                verbose_name="expected units",
            ),
        ),
        migrations.RemoveField(model_name="standardmetafield", name="expected_units_custom"),
        migrations.AlterField(
            model_name="standardmetafield",
            name="expected_units",
            field=models.CharField(
                choices=[
                    ("_number", "number"),
                    ("_str", "text"),
                    ("_bool", "yes/no"),
                    ("_custom_set", "custom from list"),
                    ("_user", "custom user-provided"),
                    ("weight", "weight"),
                    ("volume", "volume"),
                    ("area", "area"),
                    ("size", "size"),
                ],
                max_length=16,
                verbose_name="expected units",
            ),
        ),
        migrations.AddField(
            model_name="standardmetafield",
            name="expected_units_custom_set",
            field=models.JSONField(blank=True, default=list, verbose_name="expected units (custom names)"),
        ),
        migrations.AlterField(
            model_name="standardmetafield",
            name="subcategories_recommended",
            field=models.ManyToManyField(
                blank=True,
                related_name="_standardmetafield_subcategories_recommended_+",
                to="ms_products.Subcategory",
                verbose_name="subcategories where recommended",
            ),
        ),
        migrations.AlterField(
            model_name="standardmetafield",
            name="subcategories_required",
            field=models.ManyToManyField(
                blank=True,
                related_name="_standardmetafield_subcategories_required_+",
                to="ms_products.Subcategory",
                verbose_name="subcategories where required",
            ),
        ),
    ]
