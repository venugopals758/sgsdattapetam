from django.db import models


class Donation(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('completed', 'Completed'),
        ('failed',    'Failed'),
    ]
    name              = models.CharField(max_length=200)
    email             = models.EmailField(blank=True)
    amount            = models.DecimalField(max_digits=10, decimal_places=2)
    purpose           = models.CharField(max_length=300, blank=True)
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_id        = models.CharField(max_length=200, blank=True)
    razorpay_order_id = models.CharField(max_length=200, blank=True)
    date              = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.name} — ₹{self.amount}"


class Seva(models.Model):
    name        = models.CharField(max_length=200)
    price       = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SevaBooking(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    devotee_name = models.CharField(max_length=200)
    email        = models.EmailField(blank=True)
    mobile       = models.CharField(max_length=20, blank=True)
    seva         = models.ForeignKey(Seva, on_delete=models.SET_NULL, null=True)
    date         = models.DateField()
    gotram       = models.CharField(max_length=200, blank=True)
    notes        = models.TextField(blank=True)
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    payment_status    = models.CharField(
        max_length=20,
        choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')],
        default='pending',
    )
    razorpay_order_id = models.CharField(max_length=200, blank=True)
    payment_id        = models.CharField(max_length=200, blank=True)
    booked_at         = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-booked_at']

    def __str__(self):
        return f"{self.devotee_name} — {self.seva}"


class Event(models.Model):
    title       = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    start_date  = models.DateField()
    end_date    = models.DateField(null=True, blank=True)
    location    = models.CharField(max_length=300, blank=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.title


class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending',   'Pending'),
        ('success',   'Success'),
        ('failed',    'Failed'),
        ('refunded',  'Refunded'),
    ]
    METHOD_CHOICES = [
        ('upi',          'UPI'),
        ('card',         'Card'),
        ('net_banking',  'Net Banking'),
        ('cash',         'Cash'),
        ('other',        'Other'),
    ]
    reference   = models.CharField(max_length=100, blank=True)
    amount      = models.DecimalField(max_digits=10, decimal_places=2)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='success')
    method      = models.CharField(max_length=20, choices=METHOD_CHOICES, default='upi')
    description = models.CharField(max_length=300, blank=True)
    date        = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.reference} — ₹{self.amount}"


class CmsPage(models.Model):
    PAGE_CHOICES = [
        ('about',   'About Us'),
        ('contact', 'Contact'),
    ]
    page       = models.CharField(max_length=20, choices=PAGE_CHOICES, unique=True)
    title      = models.CharField(max_length=300)
    content    = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.get_page_display()


class PageSection(models.Model):
    SECTION_KEYS = [
        ('hero',    'Hero Banner'),
        ('about',   'About Section'),
        ('seva',    'Seva Section'),
        ('events',  'Events Section'),
        ('gallery', 'Gallery Section'),
        ('contact', 'Contact Section'),
        ('custom',  'Custom Section'),
    ]
    IMAGE_HINTS = {
        'hero':    '1920×800 px',
        'about':   '800×600 px',
        'seva':    '400×300 px',
        'events':  '400×300 px',
        'gallery': '600×400 px',
        'contact': '800×600 px',
    }
    page_slug   = models.CharField(max_length=50)
    section_key = models.CharField(max_length=50, choices=SECTION_KEYS)
    title       = models.CharField(max_length=300, blank=True)
    content     = models.TextField(blank=True)
    image       = models.FileField(upload_to='cms/sections/', blank=True, null=True)
    image_alt   = models.CharField(max_length=300, blank=True)
    order       = models.PositiveIntegerField(default=0)
    is_active   = models.BooleanField(default=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['page_slug', 'order', 'section_key']

    def __str__(self):
        return f"{self.page_slug} / {self.section_key}"

    @property
    def image_size_hint(self):
        return self.IMAGE_HINTS.get(self.section_key, '800×600 px')


class ThemeSettings(models.Model):
    FONT_CHOICES = [
        ("'Playfair Display', serif", 'Playfair Display (Serif)'),
        ("'Poppins', sans-serif",     'Poppins (Sans-serif)'),
        ('Georgia, serif',            'Georgia (Serif)'),
        ('system-ui, sans-serif',     'System Default'),
    ]
    primary_color    = models.CharField(max_length=20, default='#c8930a')
    secondary_color  = models.CharField(max_length=20, default='#ff7a00')
    background_color = models.CharField(max_length=20, default='#fffbf0')
    text_color       = models.CharField(max_length=20, default='#2d1b0e')
    accent_color     = models.CharField(max_length=20, default='#8b1a1a')
    font_family      = models.CharField(
        max_length=100, choices=FONT_CHOICES,
        default="'Playfair Display', serif", blank=True,
    )
    is_active  = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Theme Settings'

    def __str__(self):
        return f"Theme ({self.primary_color})"

    @classmethod
    def get_active(cls):
        return cls.objects.filter(is_active=True).first()

    def save(self, *args, **kwargs):
        if self.is_active:
            qs = ThemeSettings.objects.filter(is_active=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            qs.update(is_active=False)
        super().save(*args, **kwargs)
