from django.conf import settings
from django.db import models


class Client(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="clients",
    )

    def __str__(self):
        return self.name


class Campaign(models.Model):
    name = models.CharField(max_length=255)
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="campaigns",
    )
    clicks = models.IntegerField(default=0)
    spend = models.DecimalField(max_digits=10, decimal_places=2)
    conversions = models.IntegerField(default=0)
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="campaigns",
    )

    def __str__(self):
        return self.name


class Note(models.Model):
    content = models.TextField()
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="notes",
    )
    date = models.DateField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notes",
    )

    class Meta:
        ordering = ["-date", "-id"]


class Task(models.Model):
    description = models.CharField(max_length=200)
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    is_completed = models.BooleanField(default=False)
    due_date = models.DateField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
    )

    class Meta:
        ordering = ["due_date", "id"]
