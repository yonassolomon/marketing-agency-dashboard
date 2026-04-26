import json

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.db.models import Count, Q, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST

from .forms import (
    AgencyAuthenticationForm,
    AdminUserCreateForm,
    CampaignForm,
    ClientForm,
    NoteForm,
    RegisterForm,
    TaskForm,
)
from .models import Campaign, Client, Note, Task


def _is_admin_user(user):
    return user.is_authenticated and user.is_staff


def _recent_user_activity(user):
    recent_clients = list(user.clients.order_by("-created_at", "-id")[:3])
    recent_campaigns = list(user.campaigns.select_related("client").order_by("-date", "-id")[:3])
    recent_notes = list(user.notes.select_related("client").order_by("-date", "-id")[:3])
    recent_tasks = list(user.tasks.select_related("client").order_by("-due_date", "-id")[:3])

    dated_items = []
    for client in recent_clients:
        dated_items.append(("client", client.created_at.date(), client.created_at))
    for campaign in recent_campaigns:
        dated_items.append(("campaign", campaign.date, campaign.date))
    for note in recent_notes:
        dated_items.append(("note", note.date, note.date))
    for task in recent_tasks:
        dated_items.append(("task", task.due_date, task.due_date))

    last_activity = max(dated_items, key=lambda item: item[1]) if dated_items else None

    return {
        "recent_clients": recent_clients,
        "recent_campaigns": recent_campaigns,
        "recent_notes": recent_notes,
        "recent_tasks": recent_tasks,
        "last_activity": last_activity[2] if last_activity else None,
    }


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created. Welcome!")
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "agency/register.html", {"form": form})


class AgencyLoginView(LoginView):
    template_name = "agency/login.html"
    redirect_authenticated_user = True
    authentication_form = AgencyAuthenticationForm


@login_required
def dashboard(request):
    clients = (
        Client.objects.filter(user=request.user)
        .annotate(
            campaign_count=Count("campaigns", distinct=True),
            pending_tasks=Count("tasks", filter=Q(tasks__is_completed=False), distinct=True),
        )
        .order_by("name")
    )
    today = timezone.localdate()
    month_spend = (
        Campaign.objects.filter(
            user=request.user,
            date__year=today.year,
            date__month=today.month,
        ).aggregate(total=Sum("spend"))["total"]
        or 0
    )
    total_clients = clients.count()
    context = {
        "clients": clients,
        "total_clients": total_clients,
        "month_spend": month_spend,
    }
    return render(request, "agency/dashboard.html", context)


def _get_client_for_user(user, pk):
    return get_object_or_404(Client, pk=pk, user=user)


@login_required
def client_create(request):
    if request.method == "POST":
        form = ClientForm(request.POST)
        if form.is_valid():
            client = form.save(commit=False)
            client.user = request.user
            client.save()
            messages.success(request, "Client created.")
            return redirect("client_detail", pk=client.pk)
    else:
        form = ClientForm()
    return render(request, "agency/client_form.html", {"form": form, "title": "Add New Client"})


@login_required
def client_detail(request, pk):
    client = _get_client_for_user(request.user, pk)
    campaigns = client.campaigns.filter(user=request.user).order_by("-date", "-id")
    notes = client.notes.filter(user=request.user)
    tasks = client.tasks.filter(user=request.user)

    campaign_form = CampaignForm()
    note_form = NoteForm()
    task_form = TaskForm()

    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add_campaign":
            campaign_form = CampaignForm(request.POST)
            if campaign_form.is_valid():
                c = campaign_form.save(commit=False)
                c.client = client
                c.user = request.user
                c.save()
                messages.success(request, "Campaign added.")
                return redirect("client_detail", pk=pk)
        elif action == "add_note":
            note_form = NoteForm(request.POST)
            if note_form.is_valid():
                n = note_form.save(commit=False)
                n.client = client
                n.user = request.user
                n.save()
                messages.success(request, "Note added.")
                return redirect("client_detail", pk=pk)
        elif action == "add_task":
            task_form = TaskForm(request.POST)
            if task_form.is_valid():
                t = task_form.save(commit=False)
                t.client = client
                t.user = request.user
                t.save()
                messages.success(request, "Task added.")
                return redirect("client_detail", pk=pk)

    context = {
        "client": client,
        "campaigns": campaigns,
        "notes": notes,
        "tasks": tasks,
        "campaign_form": campaign_form,
        "note_form": note_form,
        "task_form": task_form,
    }
    return render(request, "agency/client_detail.html", context)


@login_required
def client_edit(request, pk):
    client = _get_client_for_user(request.user, pk)
    if request.method == "POST":
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, "Client updated.")
            return redirect("client_detail", pk=pk)
    else:
        form = ClientForm(instance=client)
    return render(
        request,
        "agency/client_form.html",
        {"form": form, "title": f"Edit {client.name}", "client": client},
    )


@login_required
@require_POST
def client_delete(request, pk):
    client = _get_client_for_user(request.user, pk)
    client.delete()
    messages.success(request, "Client deleted.")
    return redirect("dashboard")


@login_required
def campaign_edit(request, pk, campaign_id):
    client = _get_client_for_user(request.user, pk)
    campaign = get_object_or_404(Campaign, pk=campaign_id, client=client, user=request.user)
    if request.method == "POST":
        form = CampaignForm(request.POST, instance=campaign)
        if form.is_valid():
            form.save()
            messages.success(request, "Campaign updated.")
            return redirect("client_detail", pk=pk)
    else:
        form = CampaignForm(instance=campaign)
    return render(
        request,
        "agency/campaign_form.html",
        {"form": form, "client": client, "campaign": campaign},
    )


@login_required
@require_POST
def campaign_delete(request, pk, campaign_id):
    client = _get_client_for_user(request.user, pk)
    campaign = get_object_or_404(Campaign, pk=campaign_id, client=client, user=request.user)
    campaign.delete()
    messages.success(request, "Campaign deleted.")
    return redirect("client_detail", pk=pk)


@login_required
@require_POST
def note_delete(request, pk, note_id):
    client = _get_client_for_user(request.user, pk)
    note = get_object_or_404(Note, pk=note_id, client=client, user=request.user)
    note.delete()
    messages.success(request, "Note deleted.")
    return redirect("client_detail", pk=pk)


@login_required
@require_POST
def task_delete(request, pk, task_id):
    client = _get_client_for_user(request.user, pk)
    task = get_object_or_404(Task, pk=task_id, client=client, user=request.user)
    task.delete()
    messages.success(request, "Task deleted.")
    return redirect("client_detail", pk=pk)


@login_required
@require_http_methods(["POST"])
def task_toggle(request, pk, task_id):
    client = _get_client_for_user(request.user, pk)
    task = get_object_or_404(Task, pk=task_id, client=client, user=request.user)

    if request.content_type == "application/json":
        try:
            body = json.loads(request.body.decode())
            completed = bool(body.get("is_completed"))
        except (json.JSONDecodeError, TypeError):
            completed = not task.is_completed
        task.is_completed = completed
        task.save(update_fields=["is_completed"])
        return JsonResponse({"ok": True, "is_completed": task.is_completed})

    task.is_completed = not task.is_completed
    task.save(update_fields=["is_completed"])
    return redirect("client_detail", pk=pk)


@login_required
@user_passes_test(_is_admin_user)
def user_management(request):
    create_form = AdminUserCreateForm()

    if request.method == "POST":
        action = request.POST.get("action")
        user_id = request.POST.get("user_id")

        if action == "create_user":
            create_form = AdminUserCreateForm(request.POST)
            if create_form.is_valid():
                user = create_form.save()
                messages.success(request, f"User '{user.username}' created successfully.")
                return redirect("user_management")
        elif action in {"toggle_staff", "toggle_active"} and user_id:
            target_user = get_object_or_404(User, pk=user_id)
            if target_user == request.user and action == "toggle_staff":
                messages.error(request, "You cannot remove your own admin access.")
                return redirect("user_management")
            if target_user == request.user and action == "toggle_active":
                messages.error(request, "You cannot deactivate your own account.")
                return redirect("user_management")
            if action == "toggle_staff":
                target_user.is_staff = not target_user.is_staff
                target_user.save(update_fields=["is_staff"])
                state = "granted" if target_user.is_staff else "removed"
                messages.success(
                    request,
                    f"Admin access {state} for '{target_user.username}'.",
                )
            else:
                target_user.is_active = not target_user.is_active
                target_user.save(update_fields=["is_active"])
                state = "activated" if target_user.is_active else "deactivated"
                messages.success(request, f"User '{target_user.username}' {state}.")
            return redirect("user_management")

    users = (
        User.objects.annotate(
            client_count=Count("clients", distinct=True),
            campaign_count=Count("campaigns", distinct=True),
            note_count=Count("notes", distinct=True),
            task_count=Count("tasks", distinct=True),
            pending_task_count=Count("tasks", filter=Q(tasks__is_completed=False), distinct=True),
        )
        .order_by("username")
    )

    user_activity = []
    for managed_user in users:
        activity = _recent_user_activity(managed_user)
        user_activity.append(
            {
                "user": managed_user,
                **activity,
            }
        )

    return render(
        request,
        "agency/user_management.html",
        {"users": user_activity, "create_form": create_form},
    )
