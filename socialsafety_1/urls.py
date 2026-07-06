from django.urls import path
from . import views

urlpatterns = [

    # AUTH
    path("", views.login_view, name="login"),
    path("signup/", views.signup, name="signup"),
    path("logout/", views.logout_view, name="logout"),

    # MAIN PAGES
    path("Home/", views.Home, name="Home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile, name="profile"),

    # FEATURES
    path("contacts/", views.contact, name="contacts"),
    path("report/", views.report, name="report"),
    path("location/", views.location, name="location"),

    # SOS API
    path("receive/", views.receive_sos, name="receive_sos"),

    # DELETE CONTACT
    path(
        "contacts/delete/<int:contact_id>/",
        views.delete_contact,
        name="delete_contact"
    ),
]