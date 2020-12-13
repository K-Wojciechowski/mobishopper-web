
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ms_products', '0023_genericsubaisle_multiple_subcategories'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='group',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='products', to='ms_products.productgroup', verbose_name='group'),
        ),
    ]
