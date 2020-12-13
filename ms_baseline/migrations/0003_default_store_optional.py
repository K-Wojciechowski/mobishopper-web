
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("ms_baseline", "0002_permissions_model")]

    operations = [
        migrations.AlterField(
            model_name="msuser",
            name="default_store",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="ms_baseline.store"
            ),
        )
    ]
