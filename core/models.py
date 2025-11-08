from django.db import models
from django.conf import settings

class FoodDonation(models.Model):
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='food_donations')
    food_type = models.CharField(max_length=100)
    quantity = models.CharField(max_length=50)
    description = models.TextField()
    expiry_date = models.DateTimeField()
    location = models.CharField(max_length=255)
    image = models.ImageField(upload_to='food_donations/', null=True, blank=True)
    posted_at = models.DateTimeField(auto_now_add=True)
    is_accepted = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.food_type} by {self.donor.username}"

    class Meta:
        # Ensure fresh data is always fetched
        ordering = ['-posted_at']

class FoodRequest(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('FULFILLED', 'Fulfilled'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    requester = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='requests_made')
    food_type = models.CharField(max_length=100)
    quantity_required = models.CharField(max_length=50)
    location = models.CharField(max_length=255)
    required_timing = models.DateTimeField()
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    is_fulfilled = models.BooleanField(default=False)
    requested_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Request for {self.food_type} by {self.requester.username}"

class Collaboration(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    donor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='donor_collaborations', on_delete=models.CASCADE)
    ngo = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='ngo_collaborations', on_delete=models.CASCADE)
    food_donation = models.ForeignKey(FoodDonation, on_delete=models.CASCADE, null=True, blank=True)
    food_request = models.ForeignKey(FoodRequest, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    collaboration_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    people_served = models.PositiveIntegerField(null=True, blank=True, help_text="Number of people served when donation is completed")
    completion_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Collaboration between {self.donor.username} and {self.ngo.username}"

class LoginHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    login_timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()

    def __str__(self):
        return f"{self.user.username} logged in at {self.login_timestamp}"

class Analysis(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    food_donated_count = models.PositiveIntegerField(default=0)
    ngos_helped_count = models.PositiveIntegerField(default=0)
    collaborations_count = models.PositiveIntegerField(default=0)
    requests_fulfilled_count = models.PositiveIntegerField(default=0)
    total_people_served = models.PositiveIntegerField(default=0, help_text="Total number of people served across all completed donations")
    monthly_people_served = models.PositiveIntegerField(default=0, help_text="Number of people served in current month")
    monthly_donations_made = models.PositiveIntegerField(default=0, help_text="Number of donations made in current month")
    badge_level = models.CharField(max_length=20, blank=True, null=True, help_text="Current badge level based on monthly performance")

    def __str__(self):
        return f"Analysis for {self.user.username}"
    
    def recalculate_total_people_served(self):
        """Recalculate total people served from completed collaborations"""
        from django.db.models import Sum
        total = Collaboration.objects.filter(
            ngo=self.user,
            status='COMPLETED',
            people_served__isnull=False
        ).aggregate(total=Sum('people_served'))['total'] or 0
        self.total_people_served = total
        self.save()
        return total
    
    def recalculate_monthly_people_served(self):
        """Recalculate people served in current month from completed collaborations"""
        from django.db.models import Sum
        from datetime import datetime, date
        from django.utils import timezone
        
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_total = Collaboration.objects.filter(
            ngo=self.user,
            status='COMPLETED',
            people_served__isnull=False,
            completion_date__gte=start_of_month
        ).aggregate(total=Sum('people_served'))['total'] or 0
        
        self.monthly_people_served = monthly_total
        self.save()
        return monthly_total
    
    def recalculate_monthly_donations_made(self):
        """Recalculate donations made in current month"""
        from django.utils import timezone
        
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        monthly_count = FoodDonation.objects.filter(
            donor=self.user,
            posted_at__gte=start_of_month
        ).count()
        
        self.monthly_donations_made = monthly_count
        self.save()
        return monthly_count
    
    def get_badge_level(self):
        """Get badge level based on monthly performance"""
        # For NGOs: based on people served
        if hasattr(self.user, 'role') and self.user.role == self.user.Role.NGO:
            if self.monthly_people_served >= 1700:
                return 'DIAMOND'
            elif self.monthly_people_served >= 1500:
                return 'GOLD'
            elif self.monthly_people_served >= 1000:
                return 'SILVER'
            elif self.monthly_people_served >= 500:
                return 'BRONZE'
        # For Restaurants and Event Planners: based on donations made
        else:
            if self.monthly_donations_made >= 20:
                return 'DIAMOND'
            elif self.monthly_donations_made >= 15:
                return 'GOLD'
            elif self.monthly_donations_made >= 10:
                return 'SILVER'
            elif self.monthly_donations_made >= 5:
                return 'BRONZE'
        return None

# Separate profile models for each user type
class RestaurantProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='restaurant_profile')
    restaurant_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    profile_picture = models.ImageField(upload_to='restaurant_profile_pics/', null=True, blank=True)
    cuisine_type = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    operating_hours = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Restaurant Profile for {self.user.username}"

class NGOProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ngo_profile')
    organization_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    profile_picture = models.ImageField(upload_to='ngo_profile_pics/', null=True, blank=True)
    mission_statement = models.TextField(blank=True)
    description = models.TextField(blank=True)
    target_beneficiaries = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"NGO Profile for {self.user.username}"

class EventPlannerProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='eventplanner_profile')
    company_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    profile_picture = models.ImageField(upload_to='eventplanner_profile_pics/', null=True, blank=True)
    specialization = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Event Planner Profile for {self.user.username}"

# Keep the old UserProfile for backward compatibility (can be removed later)
class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='userprofile')
    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    organization_name = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.user.username
