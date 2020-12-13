
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("ms_baseline", "0003_default_store_optional")]

    operations = [
        migrations.AddField(model_name="msuser", name="is_global_manager", field=models.BooleanField(default=False))
    ]
