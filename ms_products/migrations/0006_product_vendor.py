
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("ms_products", "0005_vendor_store")]

    operations = [
        migrations.AddField(
            model_name="product",
            name="vendor",
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, to="ms_products.vendor"),
            preserve_default=False,
        )
    ]
