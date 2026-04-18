import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import activate, check_for_language
from django.conf import settings as django_settings
from django.views.decorators.csrf import csrf_exempt

from adminpanel.models import Donation, Seva, SevaBooking, Event, CmsPage, PageSection, Payment
from .forms import DonationForm, SevaBookingForm
from .email_utils import send_donation_email, send_seva_email

logger = logging.getLogger(__name__)


# ── Razorpay helpers ──────────────────────────────────────────

def _get_razorpay_client():
    key_id = getattr(django_settings, 'RAZORPAY_KEY_ID', '')
    key_secret = getattr(django_settings, 'RAZORPAY_KEY_SECRET', '')
    if key_id and key_secret:
        try:
            import razorpay
            return razorpay.Client(auth=(key_id, key_secret))
        except Exception:
            pass
    return None


def _razorpay_configured():
    return bool(
        getattr(django_settings, 'RAZORPAY_KEY_ID', '')
        and getattr(django_settings, 'RAZORPAY_KEY_SECRET', '')
    )


def _create_payment_record(donation):
    Payment.objects.create(
        reference=donation.payment_id or f'DON-{donation.pk}',
        amount=donation.amount,
        status='success',
        method='upi',
        description=f'Donation by {donation.name} — {donation.purpose or "General"}',
    )


def _create_seva_payment_record(booking):
    amount = booking.seva.price if booking.seva else 0
    Payment.objects.create(
        reference=booking.payment_id or f'SEVA-{booking.pk}',
        amount=amount,
        status='success',
        method='upi',
        description=f'Seva booking by {booking.devotee_name} — {booking.seva or "Seva"}',
    )


# ── Language Switch ───────────────────────────────────────────

def lang_switch(request):
    lang = request.GET.get('lang', 'en')
    if not check_for_language(lang):
        lang = 'en'
    next_url = request.GET.get('next', request.META.get('HTTP_REFERER', '/'))
    if not next_url or not next_url.startswith('/'):
        next_url = '/'
    activate(lang)
    response = redirect(next_url)
    response.set_cookie(
        django_settings.LANGUAGE_COOKIE_NAME,
        lang,
        max_age=365 * 24 * 3600,
        path='/',
    )
    return response


# ── Home ──────────────────────────────────────────────────────

def _sections(page_slug):
    return {s.section_key: s for s in PageSection.objects.filter(page_slug=page_slug, is_active=True)}


def home(request):
    upcoming_events = Event.objects.filter(is_active=True).order_by('start_date')[:3]
    featured_sevas  = Seva.objects.filter(is_active=True).order_by('name')[:4]
    return render(request, 'index.html', {
        'upcoming_events': upcoming_events,
        'featured_sevas':  featured_sevas,
        'sections':        _sections('home'),
    })


# ── Donations ─────────────────────────────────────────────────

def donations(request):
    form = DonationForm(request.POST or None)

    if request.method == 'POST':
        amount = request.POST.get('amount', '')
        post_data = request.POST.copy()
        if amount:
            post_data['amount'] = amount
        form = DonationForm(post_data)

        if form.is_valid():
            donation = form.save(commit=False)
            donation.status = 'pending'
            donation.save()

            if _razorpay_configured():
                return redirect('donations_pay', pk=donation.pk)

            donation.status = 'completed'
            donation.save(update_fields=['status'])
            _create_payment_record(donation)
            messages.success(
                request,
                f'Thank you {donation.name}! Your donation of ₹{donation.amount} '
                'has been recorded. Our team will contact you for payment details.'
            )
            return redirect('donations')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'donations.html', {'form': form})


def donations_pay(request, pk):
    donation = get_object_or_404(Donation, pk=pk, status='pending')

    client = _get_razorpay_client()
    if not client:
        donation.status = 'completed'
        donation.save(update_fields=['status'])
        _create_payment_record(donation)
        messages.success(
            request,
            f'Thank you {donation.name}! Your donation of ₹{donation.amount} has been recorded.'
        )
        return redirect('donations')

    order = client.order.create({
        'amount':          int(donation.amount * 100),
        'currency':        'INR',
        'receipt':         f'donation_{donation.pk}',
        'payment_capture': 1,
    })
    donation.razorpay_order_id = order['id']
    donation.save(update_fields=['razorpay_order_id'])
    return render(request, 'donations_pay.html', {
        'donation':     donation,
        'razorpay_key': django_settings.RAZORPAY_KEY_ID,
        'order_id':     order['id'],
        'amount_paise': int(donation.amount * 100),
        'callback_url': request.build_absolute_uri(reverse('donations_verify', args=[donation.pk])),
    })


@csrf_exempt
def donations_verify(request, pk):
    if request.method != 'POST':
        return redirect('donations')

    donation = get_object_or_404(Donation, pk=pk)

    razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
    razorpay_order_id   = request.POST.get('razorpay_order_id', '')
    razorpay_signature  = request.POST.get('razorpay_signature', '')

    client = _get_razorpay_client()
    if not client:
        messages.error(request, 'Payment service is not configured. Please contact the temple office.')
        return redirect('donations')

    import razorpay
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id':   razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature':  razorpay_signature,
        })
    except razorpay.errors.SignatureVerificationError:
        donation.status = 'failed'
        donation.save(update_fields=['status'])
        messages.error(request, 'Payment verification failed. Please contact support.')
        return redirect('donations')

    donation.payment_id = razorpay_payment_id
    donation.status     = 'completed'
    donation.save(update_fields=['payment_id', 'status'])
    _create_payment_record(donation)

    try:
        send_donation_email(donation)
    except Exception as e:
        logger.warning('Failed to send donation receipt email: %s', e)

    request.session['payment_success'] = {
        'name':        donation.name,
        'amount':      str(donation.amount),
        'reference':   razorpay_payment_id,
        'type':        'Donation',
        'description': donation.purpose or 'General Donation',
    }
    return redirect('payment_success')


# ── Seva ──────────────────────────────────────────────────────

def seva(request):
    active_sevas = Seva.objects.filter(is_active=True).order_by('name')
    form = SevaBookingForm(request.POST or None)

    if request.method == 'POST':
        if form.is_valid():
            booking = form.save(commit=False)
            booking.status         = 'pending'
            booking.payment_status = 'pending'
            booking.save()

            if _razorpay_configured():
                return redirect('seva_booking_pay', pk=booking.pk)

            # Offline fallback
            booking.payment_status = 'completed'
            booking.status         = 'confirmed'
            booking.save(update_fields=['payment_status', 'status'])
            _create_seva_payment_record(booking)
            messages.success(
                request,
                f'Seva booking confirmed for {booking.devotee_name}! '
                'Our team will contact you to finalise the details.'
            )
            return HttpResponseRedirect(reverse('seva') + '#book-form')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'seva.html', {
        'active_sevas': active_sevas,
        'form':         form,
    })


def seva_booking_pay(request, pk):
    booking = get_object_or_404(SevaBooking, pk=pk, payment_status='pending')

    client = _get_razorpay_client()
    if not client:
        booking.payment_status = 'completed'
        booking.status         = 'confirmed'
        booking.save(update_fields=['payment_status', 'status'])
        _create_seva_payment_record(booking)
        messages.success(
            request,
            f'Seva booking confirmed for {booking.devotee_name}! '
            'Our team will contact you to finalise the details.'
        )
        return redirect('seva')

    amount = booking.seva.price if booking.seva else 0
    order = client.order.create({
        'amount':          int(amount * 100),
        'currency':        'INR',
        'receipt':         f'seva_{booking.pk}',
        'payment_capture': 1,
    })
    booking.razorpay_order_id = order['id']
    booking.save(update_fields=['razorpay_order_id'])

    return render(request, 'seva_pay.html', {
        'booking':      booking,
        'razorpay_key': django_settings.RAZORPAY_KEY_ID,
        'order_id':     order['id'],
        'amount_paise': int(amount * 100),
        'amount':       amount,
        'callback_url': request.build_absolute_uri(reverse('seva_booking_verify', args=[booking.pk])),
    })


@csrf_exempt
def seva_booking_verify(request, pk):
    if request.method != 'POST':
        return redirect('seva')

    booking = get_object_or_404(SevaBooking, pk=pk)

    razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
    razorpay_order_id   = request.POST.get('razorpay_order_id', '')
    razorpay_signature  = request.POST.get('razorpay_signature', '')

    client = _get_razorpay_client()
    if not client:
        messages.error(request, 'Payment service is not configured. Please contact the temple office.')
        return redirect('seva')

    import razorpay
    try:
        client.utility.verify_payment_signature({
            'razorpay_order_id':   razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature':  razorpay_signature,
        })
    except razorpay.errors.SignatureVerificationError:
        booking.payment_status = 'failed'
        booking.save(update_fields=['payment_status'])
        messages.error(request, 'Payment verification failed. Please contact support.')
        return redirect('seva')

    booking.payment_id     = razorpay_payment_id
    booking.payment_status = 'completed'
    booking.status         = 'confirmed'
    booking.save(update_fields=['payment_id', 'payment_status', 'status'])
    _create_seva_payment_record(booking)

    amount = booking.seva.price if booking.seva else 0

    try:
        send_seva_email(booking, amount)
    except Exception as e:
        logger.warning('Failed to send seva receipt email: %s', e)

    request.session['payment_success'] = {
        'name':        booking.devotee_name,
        'amount':      str(amount),
        'reference':   razorpay_payment_id,
        'type':        'Seva Booking',
        'description': str(booking.seva) if booking.seva else 'Seva',
    }
    return redirect('payment_success')


# ── Payment Success ───────────────────────────────────────────

def payment_success(request):
    data = request.session.pop('payment_success', None)
    if not data:
        return redirect('home')
    return render(request, 'payment_success.html', {'data': data})


# ── Events ────────────────────────────────────────────────────

def events(request):
    upcoming = Event.objects.filter(is_active=True).order_by('start_date')
    return render(request, 'events.html', {'events_list': upcoming})


# ── About ─────────────────────────────────────────────────────

def about(request):
    cms = CmsPage.objects.filter(page='about').first()
    return render(request, 'about.html', {'cms_page': cms, 'sections': _sections('about')})


# ── Contact ───────────────────────────────────────────────────

def contact(request):
    cms = CmsPage.objects.filter(page='contact').first()

    if request.method == 'POST':
        name    = request.POST.get('name', '').strip()
        email   = request.POST.get('email', '').strip()
        subject = request.POST.get('subject', '').strip()
        message = request.POST.get('message', '').strip()

        if name and message:
            messages.success(
                request,
                f'Thank you {name}! Your message has been received. '
                'We will get back to you within 2 business days.'
            )
            return redirect('contact')
        else:
            messages.error(request, 'Name and message are required.')

    return render(request, 'contact.html', {'cms_page': cms, 'sections': _sections('contact')})


# ── Custom Error Handlers ─────────────────────────────────────

def custom_404(request, exception):
    return render(request, 'errors/404.html', status=404)


def custom_403(request, exception):
    return render(request, 'errors/403.html', status=403)


def custom_500(request):
    logger.error('500 Internal Server Error at %s', request.path, exc_info=True)
    return render(request, 'errors/500.html', status=500)
