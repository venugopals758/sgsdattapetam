from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0002_create_admin'),
    ]

    operations = [
        # Fix Donation.status default: completed → pending
        migrations.AlterField(
            model_name='donation',
            name='status',
            field=models.CharField(
                choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')],
                default='pending',
                max_length=20,
            ),
        ),
        # Add payment_status to SevaBooking
        migrations.AddField(
            model_name='sevabooking',
            name='payment_status',
            field=models.CharField(
                choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')],
                default='pending',
                max_length=20,
            ),
        ),
    ]
