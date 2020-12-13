
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ms_baseline', '0011_msuser_can_view_global_statistics'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ms_userdata', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoppinglist',
            name='store',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ms_baseline.store'),
        ),
        migrations.AlterField(
            model_name='shoppinglistentry',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
