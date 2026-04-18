from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0005_donation_payment_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='sevabooking',
            name='razorpay_order_id',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='sevabooking',
            name='payment_id',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
