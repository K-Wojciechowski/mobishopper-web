
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("ms_baseline", "0006_rename_to_can_view_statistics")]

    operations = [
        migrations.AddField(
            model_name="msuser",
            name="can_manage_stores",
            field=models.BooleanField(default=False, verbose_name="Can manage stores"),
        ),
        migrations.AlterField(
            model_name="msuser",
            name="can_manage_global_products",
            field=models.BooleanField(default=False, verbose_name="Can manage global products"),
        ),
        migrations.AlterField(
            model_name="msuser",
            name="can_manage_users",
            field=models.BooleanField(default=False, verbose_name="Can manage users"),
        ),
        migrations.AlterField(
            model_name="msuser", name="first_name", field=models.CharField(max_length=150, verbose_name="First name")
        ),
        migrations.AlterField(
            model_name="msuser",
            name="is_global_manager",
            field=models.BooleanField(default=False, verbose_name="Is global manager"),
        ),
        migrations.AlterField(
            model_name="msuser", name="is_manager", field=models.BooleanField(default=False, verbose_name="Is manager")
        ),
        migrations.AlterField(
            model_name="msuser", name="last_name", field=models.CharField(max_length=150, verbose_name="Last name")
        ),
    ]
