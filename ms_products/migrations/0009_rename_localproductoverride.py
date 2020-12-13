
from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("ms_baseline", "0009_msuser_can_manage_global_deals"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("ms_products", "0008_product_extra_metadata_dict_cache"),
    ]

    operations = [migrations.RenameModel(old_name="ProductOverride", new_name="LocalProductOverride")]
