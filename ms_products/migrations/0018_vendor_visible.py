
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ms_products", "0017_standardmetafield_remove_slug"),
    ]

    operations = [
        migrations.AddField(
            model_name="vendor",
            name="visible",
            field=models.BooleanField(default=True, verbose_name="visible"),
        ),
    ]
