
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("ms_baseline", "0007_msuser_can_manage_stores")]

    operations = [migrations.AddField(model_name="store", name="hidden", field=models.BooleanField(default=False))]
