from django.contrib import admin

from .models import Campaign, Client, Note, Task


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "created_at")


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ("name", "client", "user", "spend", "date")


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("client", "user", "date")


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("description", "client", "due_date", "is_completed")
