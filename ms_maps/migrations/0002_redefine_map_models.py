
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ms_baseline', '0010_update_field_verbose_names'),
        ('ms_products', '0022_rename_generic_subaisle_finish'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('ms_maps', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='map',
            name='image',
        ),
        migrations.RemoveField(
            model_name='maptile',
            name='svg_id',
        ),
        migrations.AddField(
            model_name='aisle',
            name='number',
            field=models.IntegerField(null=True, verbose_name='number'),
        ),
        migrations.AddField(
            model_name='aisle',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AddField(
            model_name='map',
            name='height',
            field=models.IntegerField(default=0, verbose_name='height'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='map',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AddField(
            model_name='map',
            name='width',
            field=models.IntegerField(default=0, verbose_name='width'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='maptile',
            name='subaisle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='ms_maps.aisle', verbose_name='aisle'),
        ),
        migrations.AddField(
            model_name='maptile',
            name='x',
            field=models.IntegerField(default=0, verbose_name='x coordinate'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='maptile',
            name='y',
            field=models.IntegerField(default=0, verbose_name='y coordinate'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productlocation',
            name='is_auto',
            field=models.BooleanField(default=False, verbose_name='is auto-generated'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='productlocation',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='user'),
        ),
        migrations.AlterField(
            model_name='aisle',
            name='description',
            field=models.TextField(verbose_name='description'),
        ),
        migrations.AlterField(
            model_name='aisle',
            name='name',
            field=models.CharField(max_length=100, verbose_name='name'),
        ),
        migrations.AlterField(
            model_name='aisle',
            name='store',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ms_baseline.store', verbose_name='store'),
        ),
        migrations.AlterField(
            model_name='map',
            name='store',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ms_baseline.store', verbose_name='store'),
        ),
        migrations.AlterField(
            model_name='maptile',
            name='map',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ms_maps.map', verbose_name='map'),
        ),
        migrations.AlterField(
            model_name='maptile',
            name='tile_type',
            field=models.CharField(choices=[('entrance', 'entrance'), ('exit', 'exit'), ('ee', 'entrance + exit'), ('subaisle', 'subaisle'), ('space', 'space')], max_length=10, verbose_name='tile type'),
        ),
        migrations.AlterField(
            model_name='productlocation',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ms_products.product', verbose_name='product'),
        ),
        migrations.AlterField(
            model_name='productlocation',
            name='store',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ms_baseline.store', verbose_name='store'),
        ),
        migrations.AlterField(
            model_name='productlocation',
            name='tile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ms_maps.maptile', verbose_name='tile'),
        ),
        migrations.CreateModel(
            name='Subaisle2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True, verbose_name='date added')),
                ('date_modified', models.DateTimeField(auto_now=True, verbose_name='date modified')),
                ('date_started', models.DateTimeField(blank=True, null=True, verbose_name='valid from')),
                ('date_ended', models.DateTimeField(blank=True, null=True, verbose_name='valid until')),
                ('name', models.CharField(max_length=100, verbose_name='name')),
                ('number', models.IntegerField(null=True, verbose_name='number')),
                ('description', models.TextField(verbose_name='description')),
                ('generic_subaisle', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ms_products.genericsubaisle', verbose_name='global subaisle')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ms_maps.aisle', verbose_name='parent')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ms_baseline.store', verbose_name='store')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='productlocation',
            name='subaisle',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ms_maps.subaisle2'),
        ),
        migrations.DeleteModel(
            name='SubAisle',
        ),
    ]
