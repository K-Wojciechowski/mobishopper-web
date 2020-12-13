
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ("ms_products", "0002_extra_meta_blank")]

    operations = [
        migrations.AddField(
            model_name="coupon",
            name="user",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="deal",
            name="user",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="product",
            name="user",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="productgroup", name="date_ended", field=models.DateTimeField(blank=True, null=True)
        ),
        migrations.AddField(
            model_name="productgroup", name="date_started", field=models.DateTimeField(blank=True, null=True)
        ),
        migrations.AddField(
            model_name="productgroup",
            name="replaced_by",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="ms_products.productgroup"
            ),
        ),
        migrations.AddField(
            model_name="productgroup",
            name="user",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="productoverride",
            name="user",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL
            ),
        ),
        migrations.AddField(
            model_name="vendor",
            name="user",
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL
            ),
        ),
    ]
