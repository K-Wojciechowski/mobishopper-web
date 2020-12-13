
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("ms_products", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="product", name="extra_metadata", field=models.JSONField(blank=True, default=list)
        )
    ]
