
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("ms_baseline", "0009_msuser_can_manage_global_deals")]

    operations = [
        migrations.AlterField(
            model_name="msuser",
            name="can_manage_global_deals",
            field=models.BooleanField(default=False, verbose_name="can manage global deals"),
        ),
        migrations.AlterField(
            model_name="msuser",
            name="can_manage_global_products",
            field=models.BooleanField(default=False, verbose_name="can manage global products"),
        ),
        migrations.AlterField(
            model_name="msuser",
            name="can_manage_stores",
            field=models.BooleanField(default=False, verbose_name="can manage stores"),
        ),
        migrations.AlterField(
            model_name="msuser",
            name="can_manage_users",
            field=models.BooleanField(default=False, verbose_name="can manage users"),
        ),
        migrations.AlterField(
            model_name="msuser", name="first_name", field=models.CharField(max_length=150, verbose_name="first name")
        ),
        migrations.AlterField(
            model_name="msuser",
            name="is_global_manager",
            field=models.BooleanField(default=False, verbose_name="is global manager"),
        ),
        migrations.AlterField(
            model_name="msuser", name="is_manager", field=models.BooleanField(default=False, verbose_name="is manager")
        ),
        migrations.AlterField(
            model_name="msuser", name="last_name", field=models.CharField(max_length=150, verbose_name="last name")
        ),
        migrations.AlterField(
            model_name="store", name="address", field=models.CharField(max_length=150, verbose_name="address")
        ),
        migrations.AlterField(
            model_name="store", name="city", field=models.CharField(max_length=50, verbose_name="city")
        ),
        migrations.AlterField(
            model_name="store",
            name="date_added",
            field=models.DateTimeField(auto_now_add=True, verbose_name="date added"),
        ),
        migrations.AlterField(
            model_name="store",
            name="date_modified",
            field=models.DateTimeField(auto_now=True, verbose_name="date modified"),
        ),
        migrations.AlterField(
            model_name="store", name="hidden", field=models.BooleanField(default=False, verbose_name="hidden")
        ),
        migrations.AlterField(
            model_name="store", name="name", field=models.CharField(max_length=100, verbose_name="name")
        ),
        migrations.AlterField(
            model_name="store", name="region_code", field=models.CharField(max_length=2, verbose_name="region code")
        ),
        migrations.AlterField(
            model_name="userstorepermission",
            name="can_manage_deals",
            field=models.BooleanField(default=False, verbose_name="can manage deals"),
        ),
        migrations.AlterField(
            model_name="userstorepermission",
            name="can_manage_employees",
            field=models.BooleanField(default=False, verbose_name="can manage employees"),
        ),
        migrations.AlterField(
            model_name="userstorepermission",
            name="can_manage_maps",
            field=models.BooleanField(default=True, verbose_name="can manage maps"),
        ),
        migrations.AlterField(
            model_name="userstorepermission",
            name="can_manage_products",
            field=models.BooleanField(default=True, verbose_name="can manage products"),
        ),
        migrations.AlterField(
            model_name="userstorepermission",
            name="can_view_statistics",
            field=models.BooleanField(default=False, verbose_name="can view statistics"),
        ),
        migrations.AlterField(
            model_name="userstorepermission",
            name="store",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="ms_baseline.store", verbose_name="store"
            ),
        ),
        migrations.AlterField(
            model_name="userstorepermission",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name="user"
            ),
        ),
    ]
