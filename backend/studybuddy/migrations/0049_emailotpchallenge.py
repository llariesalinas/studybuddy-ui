import uuid

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('studybuddy', '0048_booking_cancellation_reason_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailOTPChallenge',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('challenge_id', models.UUIDField(db_index=True, default=uuid.uuid4, unique=True)),
                ('purpose', models.CharField(choices=[('login', 'Login')], default='login', max_length=20)),
                ('code_hash', models.CharField(max_length=64)),
                ('expires_at', models.DateTimeField()),
                ('consumed_at', models.DateTimeField(blank=True, null=True)),
                ('attempt_count', models.PositiveSmallIntegerField(default=0)),
                ('resend_count', models.PositiveSmallIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='email_otp_challenges', to='auth.user')),
            ],
            options={
                'ordering': ['-created_at'],
                'indexes': [
                    models.Index(fields=['user', 'purpose', 'created_at'], name='studybuddy__user_id_9a1546_idx'),
                    models.Index(fields=['expires_at'], name='studybuddy__expires_c5b6b4_idx'),
                ],
            },
        ),
    ]
