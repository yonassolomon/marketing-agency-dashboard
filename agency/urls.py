from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.AgencyLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("", views.dashboard, name="dashboard"),
    path("users/", views.user_management, name="user_management"),
    path("clients/add/", views.client_create, name="client_create"),
    path("clients/<int:pk>/", views.client_detail, name="client_detail"),
    path("clients/<int:pk>/edit/", views.client_edit, name="client_edit"),
    path("clients/<int:pk>/delete/", views.client_delete, name="client_delete"),
    path(
        "clients/<int:pk>/campaigns/<int:campaign_id>/edit/",
        views.campaign_edit,
        name="campaign_edit",
    ),
    path(
        "clients/<int:pk>/campaigns/<int:campaign_id>/delete/",
        views.campaign_delete,
        name="campaign_delete",
    ),
    path(
        "clients/<int:pk>/notes/<int:note_id>/delete/",
        views.note_delete,
        name="note_delete",
    ),
    path(
        "clients/<int:pk>/tasks/<int:task_id>/delete/",
        views.task_delete,
        name="task_delete",
    ),
    path(
        "clients/<int:pk>/tasks/<int:task_id>/toggle/",
        views.task_toggle,
        name="task_toggle",
    ),
]
