from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import Seva, Event, CmsPage, PageSection, ThemeSettings


# ── STEP 5: FILE UPLOAD SECURITY ─────────────────────────────────
# Allowed image types and max size for CMS uploads.

ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/webp', 'image/gif']
ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
MAX_UPLOAD_SIZE_MB = 2
MAX_UPLOAD_SIZE_BYTES = MAX_UPLOAD_SIZE_MB * 1024 * 1024


def validate_image_file(file_obj):
    """Validate uploaded image: type + size."""
    if file_obj is None:
        return

    # Check file size
    if file_obj.size > MAX_UPLOAD_SIZE_BYTES:
        raise ValidationError(
            f'File too large. Maximum size is {MAX_UPLOAD_SIZE_MB} MB. '
            f'Your file is {file_obj.size / (1024 * 1024):.1f} MB.'
        )

    # Check content type
    content_type = getattr(file_obj, 'content_type', '')
    if content_type and content_type not in ALLOWED_IMAGE_TYPES:
        raise ValidationError(
            f'Unsupported file type: {content_type}. '
            f'Allowed types: JPEG, PNG, WebP, GIF.'
        )

    # Check file extension
    import os
    ext = os.path.splitext(file_obj.name)[1].lower()
    if ext and ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            f'Invalid file extension: {ext}. '
            f'Allowed extensions: {", ".join(ALLOWED_IMAGE_EXTENSIONS)}.'
        )


# ── Seva Form ─────────────────────────────────────────────────────

class SevaForm(forms.ModelForm):
    class Meta:
        model  = Seva
        fields = ['name', 'price', 'description', 'is_active']
        widgets = {
            'name':        forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Rudrabhishekam'}),
            'price':       forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0.00'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'is_active':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ── Event Form ────────────────────────────────────────────────────

class EventForm(forms.ModelForm):
    class Meta:
        model  = Event
        fields = ['title', 'description', 'start_date', 'end_date', 'location', 'is_active']
        widgets = {
            'title':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Event title'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'start_date':  forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date':    forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'location':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Main Sanctum'}),
            'is_active':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


# ── CMS Page Form ────────────────────────────────────────────────

class CmsPageForm(forms.ModelForm):
    class Meta:
        model  = CmsPage
        fields = ['title', 'content']
        widgets = {
            'title':   forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 12}),
        }


# ── Page Section Form (with image upload validation) ─────────────

class PageSectionForm(forms.ModelForm):
    class Meta:
        model  = PageSection
        fields = ['page_slug', 'section_key', 'title', 'content', 'image', 'image_alt', 'order', 'is_active']
        widgets = {
            'page_slug':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. home, about, contact'}),
            'section_key': forms.Select(attrs={'class': 'form-select'}),
            'title':       forms.TextInput(attrs={'class': 'form-control'}),
            'content':     forms.Textarea(attrs={'class': 'form-control', 'id': 'id_section_content', 'rows': 8}),
            'image_alt':   forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Image description for accessibility'}),
            'order':       forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'is_active':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_image(self):
        """STEP 5: Validate uploaded image file type and size."""
        image = self.cleaned_data.get('image')
        if image and hasattr(image, 'size'):  # New upload (not existing file)
            validate_image_file(image)
        return image


# ── Theme Settings Form ──────────────────────────────────────────

class ThemeSettingsForm(forms.ModelForm):
    class Meta:
        model  = ThemeSettings
        fields = ['primary_color', 'secondary_color', 'background_color', 'text_color', 'accent_color', 'font_family']
        widgets = {
            'primary_color':    forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'secondary_color':  forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'background_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'text_color':       forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'accent_color':     forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
            'font_family':      forms.Select(attrs={'class': 'form-select'}),
        }


# ── User Forms (with password strength validation) ───────────────

_fc = {'class': 'form-control'}


class UserCreateForm(forms.ModelForm):
    """STEP 3: Enforces Django AUTH_PASSWORD_VALIDATORS on new users."""
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={**_fc, 'placeholder': 'Enter password'}),
        help_text='Must be at least 8 characters, not too common, and not entirely numeric.',
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={**_fc, 'placeholder': 'Repeat password'}),
    )

    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active']
        widgets = {
            'username':   forms.TextInput(attrs={**_fc, 'placeholder': 'username'}),
            'first_name': forms.TextInput(attrs={**_fc, 'placeholder': 'First name'}),
            'last_name':  forms.TextInput(attrs={**_fc, 'placeholder': 'Last name'}),
            'email':      forms.EmailInput(attrs={**_fc, 'placeholder': 'email@example.com'}),
            'is_staff':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active':  forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            validate_password(password, user=self.instance)
        return password

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user


class UserEditForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active']
        widgets = {
            'username':   forms.TextInput(attrs=_fc),
            'first_name': forms.TextInput(attrs=_fc),
            'last_name':  forms.TextInput(attrs=_fc),
            'email':      forms.EmailInput(attrs=_fc),
            'is_staff':   forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active':  forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class UserPasswordForm(forms.Form):
    """STEP 3: Enforces password validators on password changes."""
    password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={**_fc, 'placeholder': 'New password'}),
        help_text='Must be at least 8 characters, not too common, and not entirely numeric.',
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={**_fc, 'placeholder': 'Repeat password'}),
    )

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if password:
            validate_password(password)
        return password

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return p2
