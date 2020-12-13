
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("ms_baseline", "0008_store_hidden")]

    operations = [
        migrations.AddField(
            model_name="msuser",
            name="can_manage_global_deals",
            field=models.BooleanField(default=False, verbose_name="Can manage global deals"),
        )
    ]
