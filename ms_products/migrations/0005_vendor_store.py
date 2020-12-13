
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("ms_baseline", "0008_store_hidden"), ("ms_products", "0004_groups_optional")]

    operations = [
        migrations.AddField(
            model_name="vendor",
            name="store",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="ms_baseline.store"
            ),
        )
    ]
