
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('ms_baseline', '0008_store_hidden'),
        ('ms_products', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aisle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('date_started', models.DateTimeField(blank=True, null=True)),
                ('date_ended', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=50, verbose_name='Aisle')),
                ('description', models.TextField(verbose_name='Description')),
                ('generic_aisle', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ms_products.genericaisle')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ms_baseline.store')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('date_started', models.DateTimeField(blank=True, null=True)),
                ('date_ended', models.DateTimeField(blank=True, null=True)),
                ('image', models.FileField(upload_to='')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ms_baseline.store')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='MapTile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('svg_id', models.CharField(max_length=20)),
                ('tile_type', models.CharField(choices=[('entrance', 'entrance'), ('exit', 'exit'), ('ee', 'entrance + exit'), ('aisle', 'aisle'), ('space', 'space')], max_length=10)),
                ('map', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ms_maps.map')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SubAisle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('date_started', models.DateTimeField(blank=True, null=True)),
                ('date_ended', models.DateTimeField(blank=True, null=True)),
                ('name', models.CharField(max_length=50, verbose_name='Subaisle')),
                ('description', models.TextField(verbose_name='Description')),
                ('generic_subaisle', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='ms_products.genericsubaisle')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ms_maps.aisle')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ms_baseline.store')),
                ('tiles', models.ManyToManyField(to='ms_maps.MapTile')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProductLocation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('date_started', models.DateTimeField(blank=True, null=True)),
                ('date_ended', models.DateTimeField(blank=True, null=True)),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ms_products.product')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ms_baseline.store')),
                ('subaisle', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ms_maps.subaisle')),
                ('tile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='ms_maps.maptile')),
            ],
        ),
        migrations.AddIndex(
            model_name='productlocation',
            index=models.Index(fields=['product', 'store'], name='ms_maps_pro_product_2a9f79_idx'),
        ),
        migrations.AlterField(
            model_name='aisle',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, verbose_name='date added'),
        ),
        migrations.AlterField(
            model_name='aisle',
            name='date_ended',
            field=models.DateTimeField(blank=True, null=True, verbose_name='valid until'),
        ),
        migrations.AlterField(
            model_name='aisle',
            name='date_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='date modified'),
        ),
        migrations.AlterField(
            model_name='aisle',
            name='date_started',
            field=models.DateTimeField(blank=True, null=True, verbose_name='valid from'),
        ),
        migrations.AlterField(
            model_name='map',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, verbose_name='date added'),
        ),
        migrations.AlterField(
            model_name='map',
            name='date_ended',
            field=models.DateTimeField(blank=True, null=True, verbose_name='valid until'),
        ),
        migrations.AlterField(
            model_name='map',
            name='date_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='date modified'),
        ),
        migrations.AlterField(
            model_name='map',
            name='date_started',
            field=models.DateTimeField(blank=True, null=True, verbose_name='valid from'),
        ),
        migrations.AlterField(
            model_name='maptile',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, verbose_name='date added'),
        ),
        migrations.AlterField(
            model_name='maptile',
            name='date_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='date modified'),
        ),
        migrations.AlterField(
            model_name='productlocation',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, verbose_name='date added'),
        ),
        migrations.AlterField(
            model_name='productlocation',
            name='date_ended',
            field=models.DateTimeField(blank=True, null=True, verbose_name='valid until'),
        ),
        migrations.AlterField(
            model_name='productlocation',
            name='date_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='date modified'),
        ),
        migrations.AlterField(
            model_name='productlocation',
            name='date_started',
            field=models.DateTimeField(blank=True, null=True, verbose_name='valid from'),
        ),
        migrations.AlterField(
            model_name='subaisle',
            name='date_added',
            field=models.DateTimeField(auto_now_add=True, verbose_name='date added'),
        ),
        migrations.AlterField(
            model_name='subaisle',
            name='date_ended',
            field=models.DateTimeField(blank=True, null=True, verbose_name='valid until'),
        ),
        migrations.AlterField(
            model_name='subaisle',
            name='date_modified',
            field=models.DateTimeField(auto_now=True, verbose_name='date modified'),
        ),
        migrations.AlterField(
            model_name='subaisle',
            name='date_started',
            field=models.DateTimeField(blank=True, null=True, verbose_name='valid from'),
        ),
        migrations.RemoveField(
            model_name='aisle',
            name='generic_aisle',
        ),
    ]
