from django import forms
from adminpanel.models import Donation, SevaBooking, Seva


class DonationForm(forms.ModelForm):
    """Public donation form — status defaults to 'pending' until payment confirmed."""

    class Meta:
        model  = Donation
        fields = ['name', 'email', 'amount', 'purpose']
        widgets = {
            'name':    forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': 'Your full name', 'required': True,
            }),
            'email':   forms.EmailInput(attrs={
                'class': 'form-input', 'placeholder': 'you@example.com',
            }),
            'amount':  forms.NumberInput(attrs={
                'class': 'form-input', 'placeholder': 'Amount in ₹', 'min': '1',
                'id': 'id_amount',
            }),
            'purpose': forms.Select(attrs={'class': 'form-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Override purpose as a ChoiceField so it renders as a <select>
        CATEGORY_CHOICES = [
            ('', '— Select a category —'),
            ('Annadanam',           'Annadanam'),
            ('Go Seva',             'Go Seva'),
            ('Temple Development',  'Temple Development'),
            ('Vedic Education',     'Vedic Education'),
            ('Festival Sponsorship','Festival Sponsorship'),
            ('Medical Outreach',    'Medical Outreach'),
            ('General Donation',    'General Donation'),
        ]
        self.fields['purpose'] = forms.ChoiceField(
            choices=CATEGORY_CHOICES,
            required=False,
            widget=forms.Select(attrs={'class': 'form-input'}),
        )
        # Amount is not required in form (set via JS button); validate in view
        self.fields['amount'].required = False


class SevaBookingForm(forms.ModelForm):
    """Public seva booking form."""

    class Meta:
        model  = SevaBooking
        fields = ['devotee_name', 'email', 'mobile', 'seva', 'date', 'gotram', 'notes']
        widgets = {
            'devotee_name': forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': 'Your name', 'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input', 'placeholder': 'you@example.com',
            }),
            'mobile': forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': '+91 98765 43210',
            }),
            'seva': forms.Select(attrs={'class': 'form-input', 'id': 'id_seva'}),
            'date': forms.DateInput(attrs={
                'class': 'form-input', 'type': 'date', 'required': True,
            }),
            'gotram': forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': 'e.g., Bharadwaja / Rohini',
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-input', 'rows': 3,
                'placeholder': 'Any specific prayers or intentions...',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only show active sevas in the dropdown
        self.fields['seva'].queryset = Seva.objects.filter(is_active=True).order_by('name')
        self.fields['seva'].empty_label = '— Choose Seva —'
