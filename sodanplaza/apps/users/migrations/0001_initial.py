# Generated by Django 5.1.3 on 2025-02-20 12:29

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.CharField(max_length=100)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('otp', models.CharField(blank=True, max_length=6, null=True)),
                ('otp_created', models.DateTimeField(auto_now_add=True, null=True)),
                ('social_token', models.CharField(blank=True, max_length=100, null=True)),
                ('terms', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('fcm_token', models.CharField(blank=True, max_length=100, null=True)),
                ('device_id', models.CharField(blank=True, max_length=100, null=True)),
                ('device_name', models.CharField(blank=True, max_length=100, null=True)),
                ('login_device', models.CharField(blank=True, max_length=100, null=True)),
                ('app_version', models.CharField(blank=True, max_length=100, null=True)),
                ('build_number', models.CharField(blank=True, max_length=100, null=True)),
                ('push_notification', models.BooleanField(default=False)),
                ('notification_popup', models.BooleanField(default=False)),
                ('chat_notification', models.BooleanField(default=False)),
                ('community_notification', models.BooleanField(default=False)),
                ('tag_notification', models.BooleanField(default=False)),
                ('new_notification', models.BooleanField(default=False)),
                ('update_notification', models.BooleanField(default=False)),
                ('message_notification', models.BooleanField(default=False)),
                ('new_service', models.BooleanField(default=False)),
                ('new_business', models.BooleanField(default=False)),
                ('qr_code', models.UUIDField(blank=True, null=True)),
                ('qr_code_created_at', models.DateTimeField(blank=True, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ProfessionProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('full_name', models.CharField(max_length=100)),
                ('about', models.TextField()),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('contact', models.CharField(blank=True, max_length=100, null=True)),
                ('website', models.CharField(blank=True, max_length=100, null=True)),
                ('country', models.CharField(blank=True, max_length=100, null=True)),
                ('state', models.CharField(blank=True, max_length=50, null=True)),
                ('image', models.ImageField(upload_to='user/profession')),
                ('city', models.CharField(blank=True, max_length=50, null=True)),
                ('address', models.CharField(blank=True, max_length=100, null=True)),
                ('target_customer', models.CharField(blank=True, max_length=100, null=True)),
                ('cash_payment', models.CharField(blank=True, max_length=100, null=True)),
                ('offer_delivery', models.BooleanField(default=False)),
                ('cv', models.FileField(blank=True, null=True, upload_to='profession/cv')),
                ('logo', models.ImageField(blank=True, null=True, upload_to='profession/logo')),
                ('identity_pic', models.ImageField(blank=True, null=True, upload_to='profession/id')),
                ('certificate_pic', models.ImageField(blank=True, null=True, upload_to='prfoession/certificates')),
                ('certificate_type', models.CharField(blank=True, max_length=100, null=True)),
                ('online_payment', models.CharField(blank=True, max_length=100, null=True)),
                ('id_card', models.CharField(blank=True, max_length=100, null=True)),
                ('passport', models.CharField(blank=True, max_length=100, null=True)),
                ('lat', models.BooleanField(default=False)),
                ('lng', models.BooleanField(default=False)),
                ('steps', models.IntegerField(default=0)),
                ('profile_is_completed', models.BooleanField(default=False)),
                ('jobs_count', models.IntegerField(default=0)),
                ('ratings_count', models.IntegerField(default=0)),
                ('sum_ratings', models.FloatField(blank=True, default=0, null=True)),
                ('ratings', models.FloatField(blank=True, default=0, null=True)),
                ('one_star', models.IntegerField(default=0)),
                ('two_star', models.IntegerField(default=0)),
                ('three_star', models.IntegerField(default=0)),
                ('four_star', models.IntegerField(default=0)),
                ('five_star', models.IntegerField(default=0)),
                ('otp', models.CharField(blank=True, max_length=6, null=True)),
                ('otp_created_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='profession_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProfessionSelectedService',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('profession', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='selected_service', to='users.professionprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quotation', models.CharField(blank=True, max_length=200, null=True)),
                ('address', models.CharField(blank=True, max_length=200, null=True)),
                ('budget', models.FloatField(blank=True, null=True)),
                ('message', models.TextField()),
                ('profession', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profession_quote', to='users.professionprofile')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quote', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('address', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=100)),
                ('image', models.ImageField(blank=True, null=True, upload_to='user/image')),
                ('country_code', models.CharField(max_length=100)),
                ('phone_number', models.IntegerField()),
                ('id_type', models.CharField(choices=[('passport', 'Passport'), ('id_card', 'Idcard')], default='id_card', max_length=100)),
                ('id_number', models.CharField(blank=True, max_length=14, null=True)),
                ('id_image', models.ImageField(blank=True, null=True, upload_to='id/image')),
                ('profile_picture', models.ImageField(blank=True, null=True, upload_to='user/profile')),
                ('description', models.CharField(blank=True, max_length=1000, null=True)),
                ('steps', models.IntegerField(default=0)),
                ('profile_is_completed', models.BooleanField(default=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='user_profile', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
