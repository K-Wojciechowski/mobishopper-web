
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("ms_baseline", "0010_update_field_verbose_names"), ("ms_products", "0015_standardize_name")]

    operations = [
        migrations.AddField(
            model_name="productgroup",
            name="photo",
            field=models.ImageField(blank=True, upload_to="", verbose_name="photo"),
        ),
        migrations.AddField(
            model_name="productgroup",
            name="store",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="ms_baseline.store",
                verbose_name="store",
            ),
        ),
    ]
