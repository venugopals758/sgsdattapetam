from adminpanel.models import ThemeSettings


def theme(request):
    return {'site_theme': ThemeSettings.get_active()}
