
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("ms_products", "0016_productgroup_photo_store")]

    operations = [
        migrations.RemoveField(model_name="standardmetafield", name="slug"),
        migrations.AlterField(
            model_name="standardmetafield",
            name="expected_units",
            field=models.CharField(
                choices=[
                    ("_number", "number"),
                    ("_str", "text"),
                    ("_bool", "yes/no"),
                    ("_custom_set", "custom, from list"),
                    ("_user", "custom, user-provided"),
                    ("weight", "weight"),
                    ("volume", "volume"),
                    ("area", "area"),
                    ("size", "size"),
                ],
                max_length=16,
                verbose_name="expected units",
            ),
        ),
    ]
