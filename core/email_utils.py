import logging
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

logger = logging.getLogger('core.views')


def send_donation_email(donation):
    """Send HTML + plain-text receipt email after a successful donation.
    Silently logs and returns on failure so the payment flow is never blocked."""
    if not donation.email:
        return

    try:
        subject = 'Donation Receipt – Temple'
        context = {'donation': donation}
        html_body = render_to_string('emails/donation_receipt.html', context)
        date_str = donation.date.strftime('%d %b %Y, %I:%M %p')
        text_body = (
            f"Dear {donation.name},\n\n"
            f"Thank you for your generous donation to the Temple.\n\n"
            f"Donation Amount : ₹{donation.amount}\n"
            f"Purpose         : {donation.purpose or 'General Donation'}\n"
            f"Transaction ID  : {donation.payment_id or '—'}\n"
            f"Date            : {date_str}\n\n"
            "May you be blessed.\n\n"
            "Temple Team"
        )
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[donation.email],
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send()
        logger.info('Donation receipt sent to %s (donation #%s)', donation.email, donation.pk)
    except Exception:
        logger.exception('Failed to send donation receipt for donation #%s', donation.pk)


def send_seva_email(booking, amount):
    """Send HTML + plain-text confirmation email after a successful seva booking.
    Silently logs and returns on failure so the payment flow is never blocked."""
    if not booking.email:
        return

    try:
        subject = 'Seva Booking Confirmed – Temple'
        context = {'booking': booking, 'amount': amount}
        html_body = render_to_string('emails/seva_receipt.html', context)
        date_str = booking.booked_at.strftime('%d %b %Y, %I:%M %p')
        text_body = (
            f"Dear {booking.devotee_name},\n\n"
            f"Your seva booking has been confirmed.\n\n"
            f"Seva            : {booking.seva}\n"
            f"Date            : {booking.date}\n"
            f"Amount Paid     : ₹{amount}\n"
            f"Transaction ID  : {booking.payment_id or '—'}\n"
            f"Booked On       : {date_str}\n\n"
            "May you be blessed.\n\n"
            "Temple Team"
        )
        msg = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[booking.email],
        )
        msg.attach_alternative(html_body, 'text/html')
        msg.send()
        logger.info('Seva receipt sent to %s (booking #%s)', booking.email, booking.pk)
    except Exception:
        logger.exception('Failed to send seva receipt for booking #%s', booking.pk)
