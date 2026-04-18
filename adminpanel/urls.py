from django.urls import path
from . import views

app_name = 'ap'

urlpatterns = [
    # Auth
    path('login/',  views.admin_login,  name='login'),
    path('logout/', views.admin_logout, name='logout'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Donations
    path('donations/',                              views.donations_list,          name='donations_list'),
    path('donations/<int:pk>/update-status/',       views.donations_update_status, name='donations_update_status'),

    # Seva
    path('seva/',             views.seva_list,   name='seva_list'),
    path('seva/add/',         views.seva_create, name='seva_create'),
    path('seva/<int:pk>/edit/',   views.seva_edit,   name='seva_edit'),
    path('seva/<int:pk>/delete/', views.seva_delete, name='seva_delete'),

    # Events
    path('events/',               views.events_list,   name='events_list'),
    path('events/add/',           views.events_create, name='events_create'),
    path('events/<int:pk>/edit/',   views.events_edit,   name='events_edit'),
    path('events/<int:pk>/delete/', views.events_delete, name='events_delete'),

    # Payments
    path('payments/', views.payments_list, name='payments_list'),

    # CMS Pages
    path('pages/',              views.pages_list, name='pages_list'),
    path('pages/<slug:page_slug>/edit/', views.pages_edit, name='pages_edit'),

    # Page Sections
    path('sections/',                      views.sections_list,  name='sections_list'),
    path('sections/add/',                  views.section_create, name='section_create'),
    path('sections/<int:pk>/edit/',        views.section_edit,   name='section_edit'),
    path('sections/<int:pk>/delete/',      views.section_delete, name='section_delete'),

    # Theme
    path('theme/', views.theme_edit, name='theme_edit'),

    # Seed data
    path('seed-data/', views.seed_data, name='seed_data'),

    # Users
    path('users/',                       views.users_list,     name='users_list'),
    path('users/add/',                   views.users_create,   name='users_create'),
    path('users/<int:pk>/edit/',         views.users_edit,     name='users_edit'),
    path('users/<int:pk>/password/',     views.users_password, name='users_password'),
    path('users/<int:pk>/delete/',       views.users_delete,   name='users_delete'),
]
