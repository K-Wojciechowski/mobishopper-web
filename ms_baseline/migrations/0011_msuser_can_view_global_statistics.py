
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ms_baseline', '0010_update_field_verbose_names'),
    ]

    operations = [
        migrations.AddField(
            model_name='msuser',
            name='can_view_global_statistics',
            field=models.BooleanField(default=False, verbose_name='can view global statistics'),
        ),
    ]
