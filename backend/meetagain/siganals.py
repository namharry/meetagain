from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import LostItem, FoundItem, Keyword, Notification

def create_notifications(instance, model_cls):
    text = (instance.name + " " + (instance.description or "")).lower()
    content_type = ContentType.objects.get_for_model(model_cls)

    for kw in Keyword.objects.all():
        if kw.word.lower() in text:
            Notification.objects.create(
                user=kw.user,
                keyword=kw.word,
                content_type=content_type,
                object_id=instance.id,
            )

@receiver(post_save, sender=LostItem)
def notify_on_lostitem_save(sender, instance, created, **kwargs):
    if created:
        create_notifications(instance, LostItem)

@receiver(post_save, sender=FoundItem)
def notify_on_founditem_save(sender, instance, created, **kwargs):
    if created:
        create_notifications(instance, FoundItem)

