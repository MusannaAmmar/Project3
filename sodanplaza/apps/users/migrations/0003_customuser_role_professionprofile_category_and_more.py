# Generated by Django 5.1.3 on 2025-02-24 15:05

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('administration', '0001_initial'),
        ('agency', '0003_agencyhours'),
        ('users', '0002_professionprofile_agency_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('user', 'User'), ('profession', 'Profession'), ('agency', 'Agency'), ('admin', 'Admin')], default='user', max_length=15),
        ),
        migrations.AddField(
            model_name='professionprofile',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profession_category', to='administration.category'),
        ),
        migrations.AddField(
            model_name='professionselectedservice',
            name='services',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profession_services', to='administration.subcategory'),
        ),
        migrations.AddField(
            model_name='quote',
            name='agency',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='agency_quote', to='agency.agencyprofile'),
        ),
        migrations.AlterField(
            model_name='quote',
            name='profession',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profession_quote', to='users.professionprofile'),
        ),
        migrations.AlterField(
            model_name='quote',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='quote', to=settings.AUTH_USER_MODEL),
        ),
    ]
