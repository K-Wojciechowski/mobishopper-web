
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("ms_products", "0006_product_vendor")]

    operations = [
        migrations.RenameField(model_name="product", old_name="extra_metadata", new_name="extra_metadata_raw")
    ]
