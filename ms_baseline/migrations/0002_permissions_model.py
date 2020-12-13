
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("ms_baseline", "0001_initial")]

    operations = [
        migrations.CreateModel(
            name="UserStorePermission",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("can_manage_products", models.BooleanField(default=True)),
                ("can_manage_maps", models.BooleanField(default=True)),
                ("can_manage_deals", models.BooleanField(default=False)),
                ("can_view_stats", models.BooleanField(default=False)),
                ("can_manage_employees", models.BooleanField(default=False)),
            ],
        ),
        migrations.AddField(model_name="msuser", name="is_manager", field=models.BooleanField(default=False)),
        migrations.AddField(
            model_name="msuser", name="can_manage_global_products", field=models.BooleanField(default=False)
        ),
        migrations.AddField(model_name="msuser", name="can_manage_users", field=models.BooleanField(default=False)),
        migrations.AlterField(model_name="store", name="date_added", field=models.DateTimeField(auto_now_add=True)),
        migrations.DeleteModel(name="UserPermission"),
        migrations.AddField(
            model_name="userstorepermission",
            name="store",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="ms_baseline.store"),
        ),
        migrations.AddField(
            model_name="userstorepermission",
            name="user",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
