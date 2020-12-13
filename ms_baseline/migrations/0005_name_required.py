
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("ms_baseline", "0004_msuser_is_global_manager")]

    operations = [
        migrations.AlterField(
            model_name="msuser", name="first_name", field=models.CharField(max_length=150, verbose_name="first name")
        ),
        migrations.AlterField(
            model_name="msuser", name="last_name", field=models.CharField(max_length=150, verbose_name="last name")
        ),
    ]
