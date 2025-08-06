from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from .models import LostItem, FoundItem, Keyword, Notification

def create_notifications(instance, model_cls):
    # name + description을 소문자로 이어붙여 검색용 텍스트 생성
    text = (instance.name + " " + (instance.description or "")).lower()
    content_type = ContentType.objects.get_for_model(model_cls)

    for kw in Keyword.objects.all():
        # 키워드가 텍스트에 포함되어 있을 경우
        if kw.word.lower() in text:
            # 이미 동일 키워드/아이템 조합 알림이 존재하면 생성하지 않음
            if not Notification.objects.filter(
                user=kw.user,
                keyword=kw.word,
                content_type=content_type,
                object_id=instance.id
            ).exists():
                Notification.objects.create(
                    user=kw.user,
                    keyword=kw.word,
                    content_type=content_type,
                    object_id=instance.id
                )

@receiver(post_save, sender=LostItem)
def notify_on_lostitem_save(sender, instance, created, **kwargs):
    if created:
        create_notifications(instance, LostItem)

@receiver(post_save, sender=FoundItem)
def notify_on_founditem_save(sender, instance, created, **kwargs):
    if created:
        create_notifications(instance, FoundItem)
