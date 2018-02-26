from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# We add the connection between the django user and the user_id of log files


class LodegUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    lodeg_user_id = models.CharField(max_length=100, unique=True)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        LodegUser.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.lodeguser.save()

# This class is necessary only if you are using the SQLite implementation of the cache
# Mind to comment this out if MongoDb implementation is chosen.


class Cache(models.Model):
    user = models.ForeignKey(LodegUser, on_delete=models.CASCADE)
    data = models.BinaryField()
