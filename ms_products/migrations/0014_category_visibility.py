
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("ms_products", "0013_remove_genericaisle")]

    operations = [
        migrations.AddField(
            model_name="category", name="visible", field=models.BooleanField(default=True, verbose_name="visible")
        ),
        migrations.AddField(
            model_name="subcategory", name="visible", field=models.BooleanField(default=True, verbose_name="visible")
        ),
    ]
