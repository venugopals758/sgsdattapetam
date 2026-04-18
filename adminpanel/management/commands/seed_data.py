"""
Seed the database with realistic sample data for demo / development.

Usage:
    python manage.py seed_data            # insert data (skips if already seeded)
    python manage.py seed_data --flush    # wipe all app data first, then re-seed
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from adminpanel.models import Donation, Seva, SevaBooking, Event, Payment, CmsPage
from datetime import date, timedelta
import random


class Command(BaseCommand):
    help = 'Seed the admin panel with sample demo data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--flush', action='store_true',
            help='Delete all existing app data before seeding'
        )

    def handle(self, *args, **options):
        if options['flush']:
            self._flush()

        self._seed_users()
        self._seed_donations()
        self._seed_seva()
        self._seed_events()
        self._seed_payments()
        self._seed_cms_pages()

        self.stdout.write(self.style.SUCCESS('\nSample data seeded successfully.\n'))

    # ── Helpers ────────────────────────────────────────────────────

    def _flush(self):
        self.stdout.write('Flushing existing data…')
        for Model in [Donation, SevaBooking, Seva, Event, Payment, CmsPage]:
            Model.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write(self.style.WARNING('  Data cleared.'))

    def _ok(self, label):
        self.stdout.write(self.style.SUCCESS(f'  [OK] {label}'))

    # ── Users ──────────────────────────────────────────────────────

    def _seed_users(self):
        self.stdout.write('\n[ Users ]')

        # Superuser
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin', password='admin123', email='admin@temple.org',
                first_name='Admin', last_name='User'
            )
            self._ok('Superuser  admin / admin123')
        else:
            self.stdout.write('  – admin already exists, skipped')

        # Staff user
        if not User.objects.filter(username='manager').exists():
            User.objects.create_user(
                username='manager', password='manager@123', email='manager@temple.org',
                first_name='Ravi', last_name='Sharma', is_staff=True
            )
            self._ok('Staff user  manager / manager@123')

        # Read-only user
        if not User.objects.filter(username='viewer').exists():
            User.objects.create_user(
                username='viewer', password='viewer@123', email='viewer@temple.org',
                first_name='Priya', last_name='Nair'
            )
            self._ok('Viewer user  viewer / viewer@123')

    # ── Donations ──────────────────────────────────────────────────

    def _seed_donations(self):
        self.stdout.write('\n[ Donations ]')
        if Donation.objects.exists():
            self.stdout.write('  – donations already exist, skipped')
            return

        records = [
            ('Ramesh Kumar',    'ramesh@example.com',   5100,  'General Donation',       'completed'),
            ('Sunita Devi',     'sunita@example.com',   11000, 'Temple Renovation',      'completed'),
            ('Anand Patel',     'anand@example.com',    2500,  'Annadanam',              'completed'),
            ('Meena Iyer',      'meena@example.com',    501,   'Festival Celebration',   'completed'),
            ('Vikram Singh',    'vikram@example.com',   21000, 'Gopuram Construction',   'completed'),
            ('Lakshmi Reddy',   'lakshmi@example.com',  1100,  'Cow Shelter',            'pending'),
            ('Deepak Nair',     'deepak@example.com',   3000,  'General Donation',       'pending'),
            ('Kavitha Menon',   'kavitha@example.com',  7500,  'Temple Renovation',      'completed'),
            ('Suresh Rao',      'suresh@example.com',   500,   'Annadanam',              'failed'),
            ('Priya Chandran',  'priya@example.com',    15000, 'Gopuram Construction',   'completed'),
            ('Arun Kumar',      'arun@example.com',     2100,  'Festival Celebration',   'completed'),
            ('Geetha Pillai',   'geetha@example.com',   800,   'General Donation',       'pending'),
        ]
        for name, email, amount, purpose, status in records:
            Donation.objects.create(name=name, email=email, amount=amount,
                                    purpose=purpose, status=status)
        self._ok(f'{len(records)} donations created')

    # ── Seva ───────────────────────────────────────────────────────

    def _seed_seva(self):
        self.stdout.write('\n[ Seva ]')
        if Seva.objects.exists():
            self.stdout.write('  – seva already exists, skipped')
            return

        seva_list = [
            ('Rudrabhishekam',     5100,  'Sacred bathing of Shiva Linga with holy water, milk, and bilva leaves.', True),
            ('Sahasranama Archana',1100,  'Recitation of 1000 names of the deity with flower offerings.',            True),
            ('Annadanam',          2500,  'Free food distribution to devotees and the needy.',                      True),
            ('Kalyanam',           11000, 'Divine wedding ceremony of the presiding deities.',                      True),
            ('Deepotsavam',        3100,  'Lighting of 1008 lamps around the temple premises.',                    True),
            ('Homam / Havan',      7500,  'Sacred fire ritual performed with Vedic chanting.',                     True),
            ('Vastram',            501,   'Offering of new clothes/silk to the deity.',                            True),
            ('Go Puja',            1500,  'Worship of cows as an offering to the divine.',                        False),
        ]
        sevas = []
        for name, price, desc, active in seva_list:
            sevas.append(Seva.objects.create(name=name, price=price, description=desc, is_active=active))
        self._ok(f'{len(sevas)} seva services created')

        # Bookings
        self.stdout.write('\n[ Seva Bookings ]')
        today = date.today()
        bookings = [
            ('Ramesh Kumar',   '9876543210', sevas[0], today + timedelta(days=3),  'confirmed'),
            ('Anita Sharma',   '9812345678', sevas[1], today + timedelta(days=5),  'pending'),
            ('Suresh Patel',   '9823456789', sevas[2], today + timedelta(days=1),  'confirmed'),
            ('Meena Devi',     '9834567890', sevas[3], today + timedelta(days=10), 'pending'),
            ('Ajay Singh',     '9845678901', sevas[0], today - timedelta(days=2),  'completed'),
            ('Vijaya Lakshmi', '9856789012', sevas[4], today + timedelta(days=7),  'confirmed'),
            ('Kiran Kumar',    '9867890123', sevas[5], today + timedelta(days=14), 'pending'),
            ('Padma Reddy',    '9878901234', sevas[2], today - timedelta(days=5),  'completed'),
            ('Arun Nair',      '9889012345', sevas[6], today + timedelta(days=4),  'confirmed'),
            ('Sarala Menon',   '9890123456', sevas[1], today - timedelta(days=1),  'cancelled'),
        ]
        for name, mobile, seva, bdate, status in bookings:
            SevaBooking.objects.create(
                devotee_name=name, mobile=mobile, seva=seva,
                date=bdate, status=status
            )
        self._ok(f'{len(bookings)} seva bookings created')

    # ── Events ─────────────────────────────────────────────────────

    def _seed_events(self):
        self.stdout.write('\n[ Events ]')
        if Event.objects.exists():
            self.stdout.write('  – events already exist, skipped')
            return

        today = date.today()
        events = [
            ('Maha Shivaratri',        today + timedelta(days=12), today + timedelta(days=12), 'Main Sanctum',        True),
            ('Ram Navami Celebrations', today + timedelta(days=25), today + timedelta(days=27), 'Temple Grounds',     True),
            ('Diwali Deepotsavam',      today + timedelta(days=45), today + timedelta(days=46), 'Full Temple Complex', True),
            ('Navratri Festival',       today + timedelta(days=60), today + timedelta(days=69), 'Main Hall',          True),
            ('Karthika Pournami',       today + timedelta(days=80), today + timedelta(days=80), 'Main Sanctum',       True),
            ('Annual Temple Utsavam',   today - timedelta(days=10), today - timedelta(days=8),  'Temple Grounds',     False),
        ]
        for title, start, end, location, active in events:
            Event.objects.create(
                title=title, start_date=start, end_date=end,
                location=location, is_active=active,
                description=f'Join us for the auspicious {title} celebration at our divine temple.'
            )
        self._ok(f'{len(events)} events created')

    # ── Payments ───────────────────────────────────────────────────

    def _seed_payments(self):
        self.stdout.write('\n[ Payments ]')
        if Payment.objects.exists():
            self.stdout.write('  – payments already exist, skipped')
            return

        records = [
            ('TXN001234', 5100,  'upi',         'success',  'Rudrabhishekam booking - Ramesh Kumar'),
            ('TXN001235', 11000, 'net_banking',  'success',  'Temple Renovation donation - Sunita Devi'),
            ('TXN001236', 2500,  'upi',          'success',  'Annadanam seva - Suresh Patel'),
            ('TXN001237', 501,   'upi',          'success',  'Festival donation - Meena Iyer'),
            ('TXN001238', 21000, 'card',         'success',  'Gopuram Construction - Vikram Singh'),
            ('TXN001239', 1100,  'upi',          'pending',  'Cow Shelter donation - Lakshmi Reddy'),
            ('TXN001240', 3000,  'cash',         'success',  'General donation - Deepak Nair'),
            ('TXN001241', 7500,  'card',         'success',  'Homam booking - Kiran Kumar'),
            ('TXN001242', 500,   'upi',          'failed',   'Annadanam - Suresh Rao'),
            ('TXN001243', 15000, 'net_banking',  'success',  'Gopuram Construction - Priya Chandran'),
            ('TXN001244', 3100,  'upi',          'success',  'Deepotsavam - Vijaya Lakshmi'),
            ('TXN001245', 2100,  'cash',         'success',  'Festival donation - Arun Kumar'),
            ('TXN001246', 11000, 'card',         'refunded', 'Kalyanam - cancelled booking'),
        ]
        for ref, amount, method, status, desc in records:
            Payment.objects.create(reference=ref, amount=amount, method=method,
                                   status=status, description=desc)
        self._ok(f'{len(records)} payments created')

    # ── CMS Pages ──────────────────────────────────────────────────

    def _seed_cms_pages(self):
        self.stdout.write('\n[ CMS Pages ]')

        about_content = """Sri Mahalakshmi Temple is a sacred shrine dedicated to Goddess Mahalakshmi,
the bestower of wealth, prosperity, and auspiciousness. Established in 1952, the temple
has been a beacon of spiritual light for devotees across generations.

The temple is renowned for its exquisite Dravidian architecture, intricate stone carvings,
and the serene atmosphere that envelopes every devotee in divine grace. Our priests perform
elaborate rituals twice daily following traditional Agama Shastra.

Temple Timings:
Morning: 6:00 AM – 12:00 PM
Evening: 4:00 PM – 9:00 PM

We welcome all devotees regardless of caste, creed, or background."""

        contact_content = """Temple Address:
Sri Mahalakshmi Temple
12, Temple Street, Mylapore
Chennai – 600 004, Tamil Nadu

Phone: +91 44 2345 6789
Email: info@mahalakshmi-temple.org

For Seva Bookings: +91 98765 43210
For Donations & Trust: +91 98765 43211

Temple Trust Office Hours:
Monday – Saturday: 9:00 AM to 5:00 PM
Sunday: 9:00 AM to 1:00 PM"""

        pages = [
            ('about',   'About Us',  about_content),
            ('contact', 'Contact',   contact_content),
        ]
        for slug, title, content in pages:
            obj, created = CmsPage.objects.update_or_create(
                page=slug, defaults={'title': title, 'content': content}
            )
            self._ok(f'CMS page "{title}" {"created" if created else "updated"}')
