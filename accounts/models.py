from django.db import models
from django.contrib.auth.models import User
from accounts.choices import *
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class ModelMixin(models.Model):
    """
        This mixins provide the default field in the models project wise
    """
    created_on = models.DateTimeField(auto_now=True)
    updated_on = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_created",
                                   on_delete=models.CASCADE, null=True, blank=True)
    updated_by = models.ForeignKey(User, related_name="%(app_label)s_%(class)s_updated",
                                   on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.created_by.email

    class Meta:
        abstract = True

class Profile(ModelMixin):
    phone = models.CharField(max_length=15, null=True, blank=True)
    country = models.CharField(max_length=40, null=True, blank=True, choices=country_choice)
    business_name = models.CharField(max_length=150, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.id is not None:
            return super(Profile, self).save()
        query = Profile.objects.filter(created_by=self.created_by)
        if len(query) <= 1:
            return super(Profile, self).save()
        raise ValueError("User already have Profile.")

class InvitedUser(ModelMixin):
    email = models.EmailField(null=True, blank=True, unique=True)

    def __str__(self):
        return str(self.email)

class Supplier(ModelMixin):
    name = models.CharField(max_length=60)
    supplier_id = models.CharField(max_length=60)
    phone = models.CharField(max_length=10)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return str(self.name)

class Inventory(ModelMixin):
    category = models.CharField(max_length=30, choices=category_type)
    type = models.CharField(max_length=30, choices=inventory_type)
    ownership_type = models.CharField(max_length=30, default='Full ownership', choices=owner_type)
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return str(self.category)
