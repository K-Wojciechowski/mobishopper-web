
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("ms_baseline", "0010_update_field_verbose_names"), ("ms_products", "0014_category_visibility")]

    operations = [
        migrations.AlterField(
            model_name="category", name="name", field=models.CharField(max_length=50, verbose_name="name")
        ),
        migrations.AlterField(
            model_name="genericsubaisle", name="name", field=models.CharField(max_length=50, verbose_name="name")
        ),
        migrations.AlterField(
            model_name="subcategory", name="name", field=models.CharField(max_length=50, verbose_name="name")
        ),
        migrations.AlterField(
            model_name="vendor", name="name", field=models.CharField(max_length=100, verbose_name="name")
        ),
    ]
