# Generated by Django 3.0.4 on 2020-04-13 21:24

import colorinput.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    replaces = [('django_taggsonomy', '0001_initial'), ('django_taggsonomy', '0002_auto_20190121_1952'), ('django_taggsonomy', '0003_auto_20190204_2135'), ('django_taggsonomy', '0004_auto_20190204_2231'), ('django_taggsonomy', '0005_tag__exclusions'), ('django_taggsonomy', '0006_tag__inclusions'), ('django_taggsonomy', '0007_tag_color'), ('django_taggsonomy', '0008_auto_20190627_2130')]

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, unique=True)),
                ('_exclusions', models.ManyToManyField(related_name='_tag__exclusions_+', to='django_taggsonomy.Tag')),
                ('_inclusions', models.ManyToManyField(to='django_taggsonomy.Tag')),
                ('color', colorinput.models.ColorField(default='d0d0d0')),
            ],
        ),
        migrations.CreateModel(
            name='TagSet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('_tags', models.ManyToManyField(related_name='tagsets', to='django_taggsonomy.Tag')),
                ('content_type', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('object_id', models.PositiveIntegerField(null=True)),
            ],
            options={
                'unique_together': {('content_type', 'object_id')},
            },
        ),
    ]