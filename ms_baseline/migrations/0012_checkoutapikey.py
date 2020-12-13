
import uuid

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ms_baseline', '0011_msuser_can_view_global_statistics'),
    ]

    operations = [
        migrations.CreateModel(
            name='CheckoutApiKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True, verbose_name='date added')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='date modified')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('key', models.UUIDField(default=uuid.uuid4)),
                ('is_active', models.BooleanField(default=True, verbose_name='is active')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ms_baseline.store', verbose_name='store')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
