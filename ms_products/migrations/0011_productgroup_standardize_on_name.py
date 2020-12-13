
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("ms_products", "0010_category_descriptions")]

    operations = [migrations.RenameField(model_name="productgroup", old_name="group_name", new_name="name")]
