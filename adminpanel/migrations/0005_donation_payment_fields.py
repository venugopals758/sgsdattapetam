from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0004_pagesection_themesettings'),
    ]

    operations = [
        migrations.AddField(
            model_name='donation',
            name='payment_id',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='donation',
            name='razorpay_order_id',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
