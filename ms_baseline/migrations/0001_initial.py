
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import ms_baseline.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [("auth", "0011_update_proxy_permissions")]

    operations = [
        migrations.CreateModel(
            name="MsUser",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                ("first_name", models.CharField(blank=True, max_length=30, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
                ("email", models.EmailField(max_length=255, unique=True)),
            ],
            options={"verbose_name": "user", "verbose_name_plural": "users", "abstract": False},
            managers=[("objects", ms_baseline.models.MsUserManager())],
        ),
        migrations.CreateModel(
            name="Store",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("address", models.CharField(max_length=150)),
                ("city", models.CharField(max_length=50)),
                ("region_code", models.CharField(max_length=2)),
                ("date_added", models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now)),
                ("date_modified", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="UserPermission",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("permission", models.CharField(choices=[("admin", "Full admin access")], max_length=5)),
                ("store", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="ms_baseline.store")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name="msuser",
            name="default_store",
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to="ms_baseline.store"),
        ),
        migrations.AddField(
            model_name="msuser",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                related_name="user_set",
                related_query_name="user",
                to="auth.Group",
                verbose_name="groups",
            ),
        ),
        migrations.AddField(
            model_name="msuser",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                to="auth.Permission",
                verbose_name="user permissions",
            ),
        ),
        migrations.AlterField(
            model_name="msuser",
            name="first_name",
            field=models.CharField(blank=True, max_length=150, verbose_name="first name"),
        ),
    ]
