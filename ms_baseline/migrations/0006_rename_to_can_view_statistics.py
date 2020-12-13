
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [("ms_baseline", "0005_name_required")]

    operations = [
        migrations.RenameField(
            model_name="userstorepermission", old_name="can_view_stats", new_name="can_view_statistics"
        )
    ]
