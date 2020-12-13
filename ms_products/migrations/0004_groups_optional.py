
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("ms_products", "0003_track_users_and_productgroup_dates")]

    operations = [
        migrations.RemoveField(model_name="productgroup", name="store"),
        migrations.AddField(model_name="product", name="description", field=models.TextField(blank=True)),
        migrations.AddField(
            model_name="product",
            name="subcategory",
            field=models.ForeignKey(
                default=1, on_delete=django.db.models.deletion.PROTECT, to="ms_products.subcategory"
            ),
            preserve_default=False,
        ),
        migrations.AddField(model_name="productgroup", name="description", field=models.TextField(blank=True)),
        migrations.AlterField(
            model_name="product",
            name="group",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="ms_products.productgroup"
            ),
        ),
    ]
