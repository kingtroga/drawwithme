from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver 
from django.db.models.signals import post_save
from django.utils import timezone

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatar/', default='avatar/default.png')
    friends = models.ManyToManyField('self', blank=True)
    created_at = models.DateField(auto_now_add=True)
    modified_at = models.TimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} Profile'
    
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        try:
            instance.profile
        except Profile.DoesNotExist:
            Profile.objects.create(user=instance)
        else:
            instance.profile.save()