from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('adminpanel', '0003_payment_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageSection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('page_slug',   models.CharField(max_length=50)),
                ('section_key', models.CharField(
                    max_length=50,
                    choices=[
                        ('hero',    'Hero Banner'),
                        ('about',   'About Section'),
                        ('seva',    'Seva Section'),
                        ('events',  'Events Section'),
                        ('gallery', 'Gallery Section'),
                        ('contact', 'Contact Section'),
                        ('custom',  'Custom Section'),
                    ],
                )),
                ('title',      models.CharField(blank=True, max_length=300)),
                ('content',    models.TextField(blank=True)),
                ('image',      models.FileField(blank=True, null=True, upload_to='cms/sections/')),
                ('image_alt',  models.CharField(blank=True, max_length=300)),
                ('order',      models.PositiveIntegerField(default=0)),
                ('is_active',  models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['page_slug', 'order', 'section_key'],
            },
        ),
        migrations.CreateModel(
            name='ThemeSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('primary_color',    models.CharField(default='#c8930a', max_length=20)),
                ('secondary_color',  models.CharField(default='#ff7a00', max_length=20)),
                ('background_color', models.CharField(default='#fffbf0', max_length=20)),
                ('text_color',       models.CharField(default='#2d1b0e', max_length=20)),
                ('accent_color',     models.CharField(default='#8b1a1a', max_length=20)),
                ('font_family', models.CharField(
                    blank=True,
                    choices=[
                        ("'Playfair Display', serif", 'Playfair Display (Serif)'),
                        ("'Poppins', sans-serif",     'Poppins (Sans-serif)'),
                        ('Georgia, serif',            'Georgia (Serif)'),
                        ('system-ui, sans-serif',     'System Default'),
                    ],
                    default="'Playfair Display', serif",
                    max_length=100,
                )),
                ('is_active',  models.BooleanField(default=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name_plural': 'Theme Settings',
            },
        ),
    ]
