
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("ms_products", "0007_extra_metadata_raw")]

    operations = [
        migrations.AddField(
            model_name="product", name="extra_metadata_dict", field=models.JSONField(blank=True, default=dict)
        )
    ]
