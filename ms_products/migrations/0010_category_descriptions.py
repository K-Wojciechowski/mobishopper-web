
import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ms_baseline", "0010_update_field_verbose_names"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ms_products", "0009_rename_localproductoverride"),
    ]

    operations = [
        migrations.AddField(
            model_name="category", name="description", field=models.TextField(blank=True, verbose_name="description")
        ),
        migrations.AddField(
            model_name="subcategory", name="description", field=models.TextField(blank=True, verbose_name="description")
        ),
        migrations.AlterField(
            model_name="category",
            name="date_added",
            field=models.DateTimeField(auto_now_add=True, verbose_name="date added"),
        ),
        migrations.AlterField(
            model_name="category",
            name="date_modified",
            field=models.DateTimeField(auto_now=True, verbose_name="date modified"),
        ),
        migrations.AlterField(
            model_name="category", name="name", field=models.CharField(max_length=50, verbose_name="category")
        ),
        migrations.AlterField(
            model_name="coupon",
            name="date_added",
            field=models.DateTimeField(auto_now_add=True, verbose_name="date added"),
        ),
        migrations.AlterField(
            model_name="coupon",
            name="date_ended",
            field=models.DateTimeField(blank=True, null=True, verbose_name="valid until"),
        ),
        migrations.AlterField(
            model_name="coupon",
            name="date_modified",
            field=models.DateTimeField(auto_now=True, verbose_name="date modified"),
        ),
        migrations.AlterField(
            model_name="coupon",
            name="date_started",
            field=models.DateTimeField(blank=True, null=True, verbose_name="valid from"),
        ),
        migrations.AlterField(
            model_name="coupon", name="is_global", field=models.BooleanField(verbose_name="is global")
        ),
        migrations.AlterField(
            model_name="coupon", name="one_use", field=models.BooleanField(default=True, verbose_name="is one use only")
        ),
        migrations.AlterField(
            model_name="coupon",
            name="price",
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name="price"),
        ),
        migrations.AlterField(
            model_name="coupon",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="ms_products.product", verbose_name="product"
            ),
        ),
        migrations.AlterField(
            model_name="coupon",
            name="stores",
            field=models.ManyToManyField(to="ms_baseline.Store", verbose_name="stores"),
        ),
        migrations.AlterField(
            model_name="coupon",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="user",
            ),
        ),
        migrations.AlterField(
            model_name="couponset",
            name="coupons",
            field=models.ManyToManyField(to="ms_products.Coupon", verbose_name="coupons"),
        ),
        migrations.AlterField(
            model_name="couponset",
            name="date_added",
            field=models.DateTimeField(auto_now_add=True, verbose_name="date added"),
        ),
        migrations.AlterField(
            model_name="couponset",
            name="date_ended",
            field=models.DateTimeField(blank=True, null=True, verbose_name="valid until"),
        ),
        migrations.AlterField(
            model_name="couponset",
            name="date_modified",
            field=models.DateTimeField(auto_now=True, verbose_name="date modified"),
        ),
        migrations.AlterField(
            model_name="couponset",
            name="date_started",
            field=models.DateTimeField(blank=True, null=True, verbose_name="valid from"),
        ),
        migrations.AlterField(
            model_name="couponset",
            name="id",
            field=models.UUIDField(
                default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name="id"
            ),
        ),
        migrations.AlterField(
            model_name="deal",
            name="date_added",
            field=models.DateTimeField(auto_now_add=True, verbose_name="date added"),
        ),
        migrations.AlterField(
            model_name="deal",
            name="date_ended",
            field=models.DateTimeField(blank=True, null=True, verbose_name="valid until"),
        ),
        migrations.AlterField(
            model_name="deal",
            name="date_modified",
            field=models.DateTimeField(auto_now=True, verbose_name="date modified"),
        ),
        migrations.AlterField(
            model_name="deal",
            name="date_started",
            field=models.DateTimeField(blank=True, null=True, verbose_name="valid from"),
        ),
        migrations.AlterField(model_name="deal", name="is_global", field=models.BooleanField(verbose_name="is global")),
        migrations.AlterField(
            model_name="deal",
            name="price",
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name="price"),
        ),
        migrations.AlterField(
            model_name="deal",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="ms_products.product", verbose_name="product"
            ),
        ),
        migrations.AlterField(
            model_name="deal",
            name="stores",
            field=models.ManyToManyField(to="ms_baseline.Store", verbose_name="stores"),
        ),
        migrations.AlterField(
            model_name="deal",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="user",
            ),
        ),
        migrations.AlterField(
            model_name="genericaisle",
            name="date_added",
            field=models.DateTimeField(auto_now_add=True, verbose_name="date added"),
        ),
        migrations.AlterField(
            model_name="genericaisle",
            name="date_modified",
            field=models.DateTimeField(auto_now=True, verbose_name="date modified"),
        ),
        migrations.AlterField(
            model_name="genericaisle", name="description", field=models.TextField(verbose_name="description")
        ),
        migrations.AlterField(
            model_name="genericaisle", name="name", field=models.CharField(max_length=50, verbose_name="aisle")
        ),
        migrations.AlterField(
            model_name="genericsubaisle",
            name="date_added",
            field=models.DateTimeField(auto_now_add=True, verbose_name="date added"),
        ),
        migrations.AlterField(
            model_name="genericsubaisle",
            name="date_modified",
            field=models.DateTimeField(auto_now=True, verbose_name="date modified"),
        ),
        migrations.AlterField(
            model_name="genericsubaisle", name="description", field=models.TextField(verbose_name="description")
        ),
        migrations.AlterField(
            model_name="genericsubaisle", name="name", field=models.CharField(max_length=50, verbose_name="subaisle")
        ),
        migrations.AlterField(
            model_name="genericsubaisle",
            name="parent",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="ms_products.genericaisle", verbose_name="parent"
            ),
        ),
        migrations.AlterField(
            model_name="genericsubaisle",
            name="subcategory",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="ms_products.subcategory", verbose_name="subcategory"
            ),
        ),
        migrations.AlterField(
            model_name="localproductoverride",
            name="available",
            field=models.BooleanField(default=True, verbose_name="is available"),
        ),
        migrations.AlterField(
            model_name="localproductoverride",
            name="date_added",
            field=models.DateTimeField(auto_now_add=True, verbose_name="date added"),
        ),
        migrations.AlterField(
            model_name="localproductoverride",
            name="date_ended",
            field=models.DateTimeField(blank=True, null=True, verbose_name="valid until"),
        ),
        migrations.AlterField(
            model_name="localproductoverride",
            name="date_modified",
            field=models.DateTimeField(auto_now=True, verbose_name="date modified"),
        ),
        migrations.AlterField(
            model_name="localproductoverride",
            name="date_started",
            field=models.DateTimeField(blank=True, null=True, verbose_name="valid from"),
        ),
        migrations.AlterField(
            model_name="localproductoverride", name="note", field=models.TextField(blank=True, verbose_name="note")
        ),
        migrations.AlterField(
            model_name="localproductoverride",
            name="price",
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True, verbose_name="price"),
        ),
        migrations.AlterField(
            model_name="localproductoverride",
            name="product",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="ms_products.product", verbose_name="product"
            ),
        ),
        migrations.AlterField(
            model_name="localproductoverride",
            name="store",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="ms_baseline.store", verbose_name="store"
            ),
        ),
        migrations.AlterField(
            model_name="localproductoverride",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="user",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="amount",
            field=models.DecimalField(decimal_places=3, max_digits=10, verbose_name="amount"),
        ),
        migrations.AlterField(
            model_name="product",
            name="amount_unit",
            field=models.CharField(
                choices=[("1", "pc"), ("kg", "kg"), ("dag", "dag"), ("g", "g"), ("L", "L"), ("mL", "mL")],
                max_length=3,
                verbose_name="amount unit",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="any_amount",
            field=models.BooleanField(default=False, verbose_name="any amount possible"),
        ),
        migrations.AlterField(
            model_name="product",
            name="date_added",
            field=models.DateTimeField(auto_now_add=True, verbose_name="date added"),
        ),
        migrations.AlterField(
            model_name="product",
            name="date_ended",
            field=models.DateTimeField(blank=True, null=True, verbose_name="valid until"),
        ),
        migrations.AlterField(
            model_name="product",
            name="date_modified",
            field=models.DateTimeField(auto_now=True, verbose_name="date modified"),
        ),
        migrations.AlterField(
            model_name="product",
            name="date_started",
            field=models.DateTimeField(blank=True, null=True, verbose_name="valid from"),
        ),
        migrations.AlterField(
            model_name="product", name="description", field=models.TextField(blank=True, verbose_name="description")
        ),
        migrations.AlterField(
            model_name="product",
            name="extra_metadata_dict",
            field=models.JSONField(blank=True, default=dict, verbose_name="extra metadata cache"),
        ),
        migrations.AlterField(
            model_name="product",
            name="extra_metadata_raw",
            field=models.JSONField(blank=True, default=list, verbose_name="extra metadata"),
        ),
        migrations.AlterField(
            model_name="product",
            name="group",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="ms_products.productgroup",
                verbose_name="group",
            ),
        ),
        migrations.AlterField(
            model_name="product", name="name", field=models.CharField(max_length=100, verbose_name="name")
        ),
        migrations.AlterField(
            model_name="product", name="photo", field=models.ImageField(blank=True, upload_to="", verbose_name="photo")
        ),
        migrations.AlterField(
            model_name="product",
            name="price",
            field=models.DecimalField(decimal_places=2, max_digits=10, verbose_name="price"),
        ),
        migrations.AlterField(
            model_name="product",
            name="replaced_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="ms_products.product",
                verbose_name="replaced by",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="store",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="ms_baseline.store",
                verbose_name="store",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="subcategory",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="ms_products.subcategory", verbose_name="subcategory"
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="user",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="vendor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="ms_products.vendor", verbose_name="vendor"
            ),
        ),
        migrations.AlterField(
            model_name="productgroup",
            name="date_added",
            field=models.DateTimeField(auto_now_add=True, verbose_name="date added"),
        ),
        migrations.AlterField(
            model_name="productgroup",
            name="date_ended",
            field=models.DateTimeField(blank=True, null=True, verbose_name="valid until"),
        ),
        migrations.AlterField(
            model_name="productgroup",
            name="date_modified",
            field=models.DateTimeField(auto_now=True, verbose_name="date modified"),
        ),
        migrations.AlterField(
            model_name="productgroup",
            name="date_started",
            field=models.DateTimeField(blank=True, null=True, verbose_name="valid from"),
        ),
        migrations.AlterField(
            model_name="productgroup",
            name="description",
            field=models.TextField(blank=True, verbose_name="description"),
        ),
        migrations.AlterField(
            model_name="productgroup", name="group_name", field=models.CharField(max_length=100, verbose_name="name")
        ),
        migrations.AlterField(
            model_name="productgroup",
            name="replaced_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="ms_products.productgroup",
                verbose_name="replaced by",
            ),
        ),
        migrations.AlterField(
            model_name="productgroup",
            name="subcategory",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="ms_products.subcategory", verbose_name="subcategory"
            ),
        ),
        migrations.AlterField(
            model_name="productgroup",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="user",
            ),
        ),
        migrations.AlterField(
            model_name="productgroup",
            name="vendor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="ms_products.vendor", verbose_name="vendor"
            ),
        ),
        migrations.AlterField(
            model_name="standardmetafield",
            name="date_added",
            field=models.DateTimeField(auto_now_add=True, verbose_name="date added"),
        ),
        migrations.AlterField(
            model_name="standardmetafield",
            name="date_modified",
            field=models.DateTimeField(auto_now=True, verbose_name="date modified"),
        ),
        migrations.AlterField(
            model_name="standardmetafield",
            name="expected_units",
            field=models.CharField(
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
                verbose_name="expected units",
            ),
        ),
        migrations.AlterField(
            model_name="standardmetafield",
            name="expected_units_custom",
            field=models.JSONField(verbose_name="expected units (custom description)"),
        ),
        migrations.AlterField(
            model_name="standardmetafield", name="name", field=models.CharField(max_length=50, verbose_name="name")
        ),
        migrations.AlterField(model_name="standardmetafield", name="slug", field=models.SlugField(verbose_name="slug")),
        migrations.AlterField(
            model_name="standardmetafield",
            name="subcategories_recommended",
            field=models.ManyToManyField(
                related_name="_standardmetafield_subcategories_recommended_+",
                to="ms_products.Subcategory",
                verbose_name="subcategories where recommended",
            ),
        ),
        migrations.AlterField(
            model_name="standardmetafield",
            name="subcategories_required",
            field=models.ManyToManyField(
                related_name="_standardmetafield_subcategories_required_+",
                to="ms_products.Subcategory",
                verbose_name="subcategories where required",
            ),
        ),
        migrations.AlterField(
            model_name="subcategory",
            name="date_added",
            field=models.DateTimeField(auto_now_add=True, verbose_name="date added"),
        ),
        migrations.AlterField(
            model_name="subcategory",
            name="date_modified",
            field=models.DateTimeField(auto_now=True, verbose_name="date modified"),
        ),
        migrations.AlterField(
            model_name="subcategory", name="name", field=models.CharField(max_length=50, verbose_name="subcategory")
        ),
        migrations.AlterField(
            model_name="subcategory",
            name="parent",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="ms_products.category", verbose_name="parent"
            ),
        ),
        migrations.AlterField(
            model_name="vendor",
            name="date_added",
            field=models.DateTimeField(auto_now_add=True, verbose_name="date added"),
        ),
        migrations.AlterField(
            model_name="vendor",
            name="date_modified",
            field=models.DateTimeField(auto_now=True, verbose_name="date modified"),
        ),
        migrations.AlterField(
            model_name="vendor", name="description", field=models.TextField(blank=True, verbose_name="description")
        ),
        migrations.AlterField(
            model_name="vendor", name="logo", field=models.ImageField(blank=True, upload_to="", verbose_name="logo")
        ),
        migrations.AlterField(
            model_name="vendor", name="name", field=models.CharField(max_length=100, verbose_name="vendor")
        ),
        migrations.AlterField(
            model_name="vendor",
            name="store",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to="ms_baseline.store",
                verbose_name="store",
            ),
        ),
        migrations.AlterField(
            model_name="vendor",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.AUTH_USER_MODEL,
                verbose_name="user",
            ),
        ),
        migrations.AlterField(
            model_name="vendor", name="website", field=models.URLField(blank=True, verbose_name="website")
        ),
    ]
