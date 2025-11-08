from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        RESTAURANT = "RESTAURANT", "Restaurant"
        NGO = "NGO", "Ngo"
        EVENTPLANNER = "EVENTPLANNER", "Event Planner"

    role = models.CharField(max_length=50, choices=Role.choices, default=Role.RESTAURANT)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.role or Role.RESTAURANT
        return super().save(*args, **kwargs)
