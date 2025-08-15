from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.contrib.postgres.fields import ArrayField


class LostItem(models.Model):
    CATEGORY_CHOICES = [
        ('가방', '가방'),
        ('귀금속', '귀금속'),
        ('의류', '의류'),
        ('전자기기', '전자기기'),
        ('지갑', '지갑'),
        ('컴퓨터', '컴퓨터'),
        ('카드', '카드'),
        ('현금', '현금'),
        ('휴대폰', '휴대폰'),
        ('문서/서류', '문서/서류'),
        ('악기', '악기'),
        ('스포츠용품', '스포츠용품'), 
        ('신분증', '신분증'),
        ('책/노트', '책/노트'),
        ('기타', '기타'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='기타')

    subcategory = models.CharField(max_length=50, blank=True, null=True, verbose_name='세부옵션')

     # ✅ 다중 위치용 새 필드
    lost_locations = ArrayField(
        base_field=models.CharField(max_length=200),  
        default=list,
        blank=True,
    )

    lost_date_start = models.DateField(null=False, blank=True)
    lost_date_end = models.DateField(null=False, blank=True)

    is_claimed = models.BooleanField(default=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='lost_items',
        null=True, blank=True,
    )
    
    image = models.ImageField(upload_to='lost_items/', blank=True, null=True)

    def __str__(self):
        return f"[분실물] {self.name}"


class FoundItem(models.Model):
    CATEGORY_CHOICES = [
        ('가방', '가방'),
        ('귀금속', '귀금속'),
        ('의류', '의류'),
        ('전자기기', '전자기기'),
        ('지갑', '지갑'),
        ('컴퓨터', '컴퓨터'),
        ('카드', '카드'),
        ('현금', '현금'),
        ('휴대폰', '휴대폰'),
        ('문서/서류', '문서/서류'),
        ('악기', '악기'),
        ('스포츠용품', '스포츠용품'), 
        ('신분증', '신분증'),
        ('책/노트', '책/노트'),
        ('기타', '기타'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='기타')

    subcategory = models.CharField(max_length=50, blank=True, null=True, verbose_name='세부옵션')  # 새 필드 추가

    found_location = models.CharField(max_length=200)
    found_date = models.DateField(null=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='found_items',
        null=True, blank=True
    )

    is_returned = models.BooleanField(default=False)
    image = models.ImageField(upload_to='found_items/', blank=True, null=True)

    lat = models.FloatField(blank=True, null=True)
    lng = models.FloatField(blank=True, null=True)

    STATUS_CHOICES = [
        ('보관 중', '보관 중'),
        ('소유자 반환', '소유자 반환'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='보관 중')
    is_deleted = models.BooleanField(default=False, db_index=True)
    def __str__(self):
        return f"[습득물] {self.name}"
    
    
class Keyword(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    word = models.CharField(max_length=50)

    class Meta:
        unique_together = ('user', 'word')  # 사용자별 중복 방지

    def __str__(self):
        return f"{self.user.username} - {self.word}"


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    # Generic relation to LostItem or FoundItem
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveBigIntegerField()
    item = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"🔔 {self.user.username} - '{self.keyword}' 매칭 알림"
    

class Notice(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True
    )
    
    def __str__(self):
        return self.title


class Inquiry(models.Model):
    STATUS_CHOICES = [
        ('pending', '대기 중'),
        ('answered', '답변 완료'),
        ('closed', '종료'),
    ]

    CATEGORY_CHOICES = [
        ('login', '로그인 문제'),
        ('lost', '분실물 등록/조회'),
        ('account', '계정 관련'),
        ('other', '기타'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='other'
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    response = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} - {self.subject}"
