
import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [("ms_baseline", "0008_store_hidden")]

    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                ("date_modified", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=50, verbose_name="Category")),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Coupon",
            fields=[
                ("date_added", models.DateTimeField(auto_now_add=True)),
                ("date_modified", models.DateTimeField(auto_now=True)),
                ("date_started", models.DateTimeField(blank=True, null=True)),
                ("date_ended", models.DateTimeField(blank=True, null=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("is_global", models.BooleanField()),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("one_use", models.BooleanField(default=True)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="GenericAisle",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                ("date_modified", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=50, verbose_name="Aisle")),
                ("description", models.TextField(verbose_name="Description")),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                ("date_modified", models.DateTimeField(auto_now=True)),
                ("date_started", models.DateTimeField(blank=True, null=True)),
                ("date_ended", models.DateTimeField(blank=True, null=True)),
                ("name", models.CharField(max_length=100, verbose_name="Name")),
                ("photo", models.ImageField(blank=True, upload_to="")),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("amount", models.DecimalField(decimal_places=3, max_digits=10)),
                (
                    "amount_unit",
                    models.CharField(
                        choices=[("1", "pc"), ("kg", "kg"), ("dag", "dag"), ("g", "g"), ("L", "L"), ("mL", "mL")],
                        max_length=3,
                    ),
                ),
                ("any_amount", models.BooleanField(default=False)),
                ("extra_metadata", models.JSONField()),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Vendor",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                ("date_modified", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100, verbose_name="Vendor")),
                ("logo", models.ImageField(blank=True, upload_to="")),
                ("description", models.TextField(blank=True)),
                ("website", models.URLField(blank=True)),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Subcategory",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                ("date_modified", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=50, verbose_name="Subcategory")),
                ("parent", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="ms_products.category")),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="StandardMetaField",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                ("date_modified", models.DateTimeField(auto_now=True)),
                ("slug", models.SlugField()),
                ("name", models.CharField(max_length=50)),
                (
                    "expected_units",
                    models.CharField(
                        choices=[
                            ("int", "int"),
                            ("text", "text"),
                            ("weight", "weight"),
                            ("volume", "volume"),
                            ("area", "area"),
                            ("size", "size"),
                            ("custom_set", "custom_set"),
                            ("custom", "custom"),
                        ],
                        max_length=10,
                    ),
                ),
                ("expected_units_custom", models.JSONField()),
                (
                    "subcategories_recommended",
                    models.ManyToManyField(
                        related_name="_standardmetafield_subcategories_recommended_+", to="ms_products.Subcategory"
                    ),
                ),
                (
                    "subcategories_required",
                    models.ManyToManyField(
                        related_name="_standardmetafield_subcategories_required_+", to="ms_products.Subcategory"
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="ProductOverride",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                ("date_modified", models.DateTimeField(auto_now=True)),
                ("date_started", models.DateTimeField(blank=True, null=True)),
                ("date_ended", models.DateTimeField(blank=True, null=True)),
                ("available", models.BooleanField(default=True)),
                ("price", models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ("note", models.TextField(blank=True)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="ms_products.product")),
                ("store", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="ms_baseline.store")),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="ProductGroup",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                ("date_modified", models.DateTimeField(auto_now=True)),
                ("group_name", models.CharField(max_length=100, verbose_name="Name")),
                (
                    "store",
                    models.ForeignKey(
                        blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="ms_baseline.store"
                    ),
                ),
                (
                    "subcategory",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="ms_products.subcategory"),
                ),
                ("vendor", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="ms_products.vendor")),
            ],
            options={"abstract": False},
        ),
        migrations.AddField(
            model_name="product",
            name="group",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="ms_products.productgroup"),
        ),
        migrations.AddField(
            model_name="product",
            name="replaced_by",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="ms_products.product"
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="store",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to="ms_baseline.store"
            ),
        ),
        migrations.CreateModel(
            name="GenericSubAisle",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                ("date_modified", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=50, verbose_name="Subaisle")),
                ("description", models.TextField(verbose_name="Description")),
                (
                    "parent",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="ms_products.genericaisle"),
                ),
                (
                    "subcategory",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="ms_products.subcategory"),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="Deal",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("date_added", models.DateTimeField(auto_now_add=True)),
                ("date_modified", models.DateTimeField(auto_now=True)),
                ("date_started", models.DateTimeField(blank=True, null=True)),
                ("date_ended", models.DateTimeField(blank=True, null=True)),
                ("is_global", models.BooleanField()),
                ("price", models.DecimalField(decimal_places=2, max_digits=10)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="ms_products.product")),
                ("stores", models.ManyToManyField(to="ms_baseline.Store")),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="CouponSet",
            fields=[
                ("date_added", models.DateTimeField(auto_now_add=True)),
                ("date_modified", models.DateTimeField(auto_now=True)),
                ("date_started", models.DateTimeField(blank=True, null=True)),
                ("date_ended", models.DateTimeField(blank=True, null=True)),
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("coupons", models.ManyToManyField(to="ms_products.Coupon")),
            ],
            options={"abstract": False},
        ),
        migrations.AddField(
            model_name="coupon",
            name="product",
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="ms_products.product"),
        ),
        migrations.AddField(model_name="coupon", name="stores", field=models.ManyToManyField(to="ms_baseline.Store")),
    ]
