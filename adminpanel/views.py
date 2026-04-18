import json
import io
import logging
import functools

from django.core.management import call_command
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.http import HttpResponseForbidden

from .models import Donation, Seva, SevaBooking, Event, Payment, CmsPage, PageSection, ThemeSettings
from django.contrib.auth.models import User
from .forms import (
    SevaForm, EventForm, CmsPageForm,
    UserCreateForm, UserEditForm, UserPasswordForm,
    PageSectionForm, ThemeSettingsForm,
)

# ── STEP 11: Security Logger ─────────────────────────────────────
security_logger = logging.getLogger('security')


# ── STEP 3: staff_required decorator ──────────────────────────────
# Combines @login_required with an is_staff check.
# Non-staff users see 403 Forbidden instead of the admin panel.

def staff_required(view_func):
    """Decorator: requires user to be authenticated AND is_staff=True."""
    @functools.wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f'/admin-panel/login/?next={request.path}')
        if not request.user.is_staff:
            security_logger.warning(
                'ACCESS DENIED: user=%s (id=%s) tried to access %s — not staff',
                request.user.username, request.user.pk, request.path,
            )
            return HttpResponseForbidden(
                '<h1>403 Forbidden</h1>'
                '<p>You do not have permission to access this page.</p>'
            )
        return view_func(request, *args, **kwargs)
    return _wrapped


# ── Auth ──────────────────────────────────────────────────────────

def admin_login(request):
    if request.user.is_authenticated:
        return redirect('ap:dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # STEP 10: Basic rate limiting via django-ratelimit
        # Import here so the decorator doesn't break if ratelimit is missing
        try:
            from django_ratelimit.decorators import ratelimit
            from django_ratelimit.exceptions import Ratelimited
        except ImportError:
            ratelimit = None
            Ratelimited = None

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if not user.is_staff:
                security_logger.warning(
                    'LOGIN REJECTED: user=%s is not staff — IP=%s',
                    username, _get_client_ip(request),
                )
                messages.error(request, 'You do not have admin access.')
                return render(request, 'adminpanel/login.html')

            login(request, user)
            security_logger.info(
                'LOGIN SUCCESS: user=%s — IP=%s',
                username, _get_client_ip(request),
            )
            return redirect(request.GET.get('next', 'ap:dashboard'))

        # STEP 11: Log failed login attempts
        security_logger.warning(
            'LOGIN FAILED: username=%s — IP=%s',
            username, _get_client_ip(request),
        )
        messages.error(request, 'Invalid username or password.')

    return render(request, 'adminpanel/login.html')


# Apply rate limiting to the login view (5 attempts per minute per IP)
try:
    from django_ratelimit.decorators import ratelimit as _ratelimit
    admin_login = _ratelimit(key='ip', rate='5/m', method='POST', block=True)(admin_login)
except ImportError:
    pass  # django-ratelimit not installed — login works without rate limiting


def admin_logout(request):
    if request.user.is_authenticated:
        security_logger.info(
            'LOGOUT: user=%s — IP=%s',
            request.user.username, _get_client_ip(request),
        )
    logout(request)
    return redirect('ap:login')


def _get_client_ip(request):
    """Extract the client IP from the request, considering proxies."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', 'unknown')


# ── Dashboard ─────────────────────────────────────────────────────

@staff_required
def dashboard(request):
    total_donations  = Donation.objects.count()
    payments_amount  = Payment.objects.aggregate(t=Sum('amount'))['t'] or 0

    # Donut: donations by status
    dsm = {x['status']: x['c'] for x in Donation.objects.values('status').annotate(c=Count('id'))}

    # Bar: payments by method (total amount)
    pm_qs = Payment.objects.values('method').annotate(total=Sum('amount'))
    method_label = dict(Payment.METHOD_CHOICES)
    pm_labels  = [method_label.get(x['method'], x['method']) for x in pm_qs]
    pm_amounts = [float(x['total'] or 0) for x in pm_qs]

    ctx = {
        'total_donations':  total_donations,
        'donations_amount': Donation.objects.aggregate(t=Sum('amount'))['t'] or 0,
        'total_seva':       SevaBooking.objects.count(),
        'total_events':     Event.objects.count(),
        'total_payments':   Payment.objects.count(),
        'payments_amount':  payments_amount,
        'recent_donations': Donation.objects.order_by('-date')[:6],
        'recent_bookings':  SevaBooking.objects.order_by('-booked_at')[:5],
        'upcoming_events':  Event.objects.filter(is_active=True).order_by('start_date')[:4],
        # chart data
        'don_completed':    dsm.get('completed', 0),
        'don_pending':      dsm.get('pending',   0),
        'don_failed':       dsm.get('failed',    0),
        'pm_labels_json':   json.dumps(pm_labels),
        'pm_amounts_json':  json.dumps(pm_amounts),
    }
    return render(request, 'adminpanel/dashboard.html', ctx)


# ── Donations ─────────────────────────────────────────────────────

@staff_required
def donations_list(request):
    qs = Donation.objects.all()

    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter in ('pending', 'completed', 'failed'):
        qs = qs.filter(status=status_filter)

    # Filter by date range
    date_from = request.GET.get('date_from', '')
    date_to   = request.GET.get('date_to', '')
    if date_from:
        qs = qs.filter(date__date__gte=date_from)
    if date_to:
        qs = qs.filter(date__date__lte=date_to)

    total_amount = qs.aggregate(t=Sum('amount'))['t'] or 0

    ctx = {
        'donations':     qs,
        'status_filter': status_filter,
        'date_from':     date_from,
        'date_to':       date_to,
        'total_amount':  total_amount,
    }
    return render(request, 'adminpanel/donations/list.html', ctx)


# ── Seva ──────────────────────────────────────────────────────────

@staff_required
def seva_list(request):
    sevas    = Seva.objects.all()
    bookings = SevaBooking.objects.select_related('seva').all()
    return render(request, 'adminpanel/seva/list.html', {'sevas': sevas, 'bookings': bookings})


@staff_required
def seva_create(request):
    form = SevaForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Seva added successfully.')
        return redirect('ap:seva_list')
    return render(request, 'adminpanel/seva/create.html', {'form': form, 'title': 'Add Seva'})


@staff_required
def seva_edit(request, pk):
    seva = get_object_or_404(Seva, pk=pk)
    form = SevaForm(request.POST or None, instance=seva)
    if form.is_valid():
        form.save()
        messages.success(request, 'Seva updated.')
        return redirect('ap:seva_list')
    return render(request, 'adminpanel/seva/create.html', {'form': form, 'title': 'Edit Seva', 'obj': seva})


@staff_required
def seva_delete(request, pk):
    seva = get_object_or_404(Seva, pk=pk)
    if request.method == 'POST':
        seva.delete()
        messages.success(request, 'Seva deleted.')
        return redirect('ap:seva_list')
    return render(request, 'adminpanel/confirm_delete.html', {'obj': seva, 'back': 'ap:seva_list'})


# ── Events ────────────────────────────────────────────────────────

@staff_required
def events_list(request):
    events = Event.objects.all()
    return render(request, 'adminpanel/events/list.html', {'events': events})


@staff_required
def events_create(request):
    form = EventForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Event added successfully.')
        return redirect('ap:events_list')
    return render(request, 'adminpanel/events/create.html', {'form': form, 'title': 'Add Event'})


@staff_required
def events_edit(request, pk):
    event = get_object_or_404(Event, pk=pk)
    form  = EventForm(request.POST or None, instance=event)
    if form.is_valid():
        form.save()
        messages.success(request, 'Event updated.')
        return redirect('ap:events_list')
    return render(request, 'adminpanel/events/create.html', {'form': form, 'title': 'Edit Event', 'obj': event})


@staff_required
def events_delete(request, pk):
    event = get_object_or_404(Event, pk=pk)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'Event deleted.')
        return redirect('ap:events_list')
    return render(request, 'adminpanel/confirm_delete.html', {'obj': event, 'back': 'ap:events_list'})


# ── Donations update ──────────────────────────────────────────────

@staff_required
def donations_update_status(request, pk):
    donation = get_object_or_404(Donation, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status', '')
        if new_status in ('pending', 'completed', 'failed'):
            donation.status = new_status
            donation.save()
            messages.success(request, f'Donation #{pk} updated to {donation.get_status_display()}.')
        else:
            messages.error(request, 'Invalid status.')
    return redirect('ap:donations_list')


# ── Payments ──────────────────────────────────────────────────────

@staff_required
def payments_list(request):
    payments = Payment.objects.all()
    total    = payments.aggregate(t=Sum('amount'))['t'] or 0
    return render(request, 'adminpanel/payments/list.html', {'payments': payments, 'total': total})


# ── CMS Pages ─────────────────────────────────────────────────────

@staff_required
def pages_list(request):
    choices = CmsPage.PAGE_CHOICES
    section_counts = {
        x['page_slug']: x['c']
        for x in PageSection.objects.values('page_slug').annotate(c=Count('id'))
    }
    return render(request, 'adminpanel/pages/list.html', {
        'choices': choices,
        'section_counts': section_counts,
    })


@staff_required
def pages_edit(request, page_slug):
    obj, _ = CmsPage.objects.get_or_create(
        page=page_slug,
        defaults={'title': page_slug.capitalize(), 'content': ''}
    )
    form = CmsPageForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, f'"{obj.get_page_display()}" page updated.')
        return redirect('ap:pages_list')
    return render(request, 'adminpanel/pages/edit.html', {'form': form, 'obj': obj})


# ── Users ─────────────────────────────────────────────────────────

@staff_required
def users_list(request):
    users = User.objects.all().order_by('-date_joined')
    return render(request, 'adminpanel/users/list.html', {'users': users})


@staff_required
def users_create(request):
    form = UserCreateForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'User created successfully.')
        return redirect('ap:users_list')
    return render(request, 'adminpanel/users/form.html', {'form': form, 'title': 'Add User'})


@staff_required
def users_edit(request, pk):
    obj = get_object_or_404(User, pk=pk)
    form = UserEditForm(request.POST or None, instance=obj)
    if form.is_valid():
        form.save()
        messages.success(request, 'User updated.')
        return redirect('ap:users_list')
    return render(request, 'adminpanel/users/form.html', {'form': form, 'title': 'Edit User', 'obj': obj})


@staff_required
def users_password(request, pk):
    obj = get_object_or_404(User, pk=pk)
    form = UserPasswordForm(request.POST or None)
    if form.is_valid():
        obj.set_password(form.cleaned_data['password1'])
        obj.save()
        messages.success(request, f'Password changed for {obj.username}.')
        return redirect('ap:users_list')
    return render(request, 'adminpanel/users/password.html', {'form': form, 'obj': obj})


@staff_required
def users_delete(request, pk):
    obj = get_object_or_404(User, pk=pk)
    if obj == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('ap:users_list')
    if request.method == 'POST':
        obj.delete()
        messages.success(request, 'User deleted.')
        return redirect('ap:users_list')
    return render(request, 'adminpanel/confirm_delete.html', {'obj': obj, 'back': 'ap:users_list'})


# ── Page Sections ─────────────────────────────────────────────────

@staff_required
def sections_list(request):
    sections = PageSection.objects.all()
    return render(request, 'adminpanel/sections/list.html', {'sections': sections})


@staff_required
def section_create(request):
    form = PageSectionForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Section created.')
        return redirect('ap:sections_list')
    return render(request, 'adminpanel/sections/form.html', {'form': form, 'title': 'Add Section'})


@staff_required
def section_edit(request, pk):
    section = get_object_or_404(PageSection, pk=pk)
    form = PageSectionForm(request.POST or None, request.FILES or None, instance=section)
    if form.is_valid():
        form.save()
        messages.success(request, 'Section updated.')
        return redirect('ap:sections_list')
    return render(request, 'adminpanel/sections/form.html', {
        'form': form, 'title': 'Edit Section', 'obj': section,
    })


@staff_required
def section_delete(request, pk):
    section = get_object_or_404(PageSection, pk=pk)
    if request.method == 'POST':
        section.delete()
        messages.success(request, 'Section deleted.')
        return redirect('ap:sections_list')
    return render(request, 'adminpanel/confirm_delete.html', {'obj': section, 'back': 'ap:sections_list'})


# ── Theme ──────────────────────────────────────────────────────────

@staff_required
def theme_edit(request):
    obj = ThemeSettings.get_active() or ThemeSettings()
    form = ThemeSettingsForm(request.POST or None, instance=obj)
    if form.is_valid():
        ThemeSettings.objects.all().update(is_active=False)
        theme = form.save(commit=False)
        theme.is_active = True
        theme.save()
        messages.success(request, 'Theme saved. Changes are live across the website.')
        return redirect('ap:theme_edit')
    return render(request, 'adminpanel/theme/edit.html', {'form': form, 'obj': obj})


# ── Seed Data ─────────────────────────────────────────────────────

@staff_required
def seed_data(request):
    if not request.user.is_superuser:
        messages.error(request, 'Only superusers can run the data seeder.')
        return redirect('ap:dashboard')

    output = None
    error  = None

    if request.method == 'POST':
        flush = request.POST.get('flush') == '1'
        buf = io.StringIO()
        try:
            call_command('seed_data', flush=flush, stdout=buf, no_color=True)
            output = buf.getvalue()
        except Exception as e:
            error = str(e)

    return render(request, 'adminpanel/seed_data.html', {'output': output, 'error': error})
