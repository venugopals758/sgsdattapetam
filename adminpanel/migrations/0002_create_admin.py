from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_admin(apps, schema_editor):
    User = apps.get_model('auth', 'User')

    if not User.objects.filter(username='admin').exists():
        User.objects.create(
            username='admin',
            email='admin@gmail.com',
            password=make_password('admin123'),  # ✅ FIX
            is_superuser=True,
            is_staff=True,
            is_active=True
        )

class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(create_admin),
    ]