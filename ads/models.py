from django.db import models
from django.contrib.auth.models import User

class Ad(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image_url = models.URLField(null=True, blank=True)
    category = models.CharField(max_length=100, blank=False)
    condition_choices = [
        ('new', 'Новый'),
        ('used', 'Б/у'),
    ]
    condition = models.CharField(max_length=10, choices=condition_choices)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ads')


class ExchangeProposal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает'),
        ('accepted', 'Принята'),
        ('rejected', 'Отклонена'),
    ]
    ad_sender = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='sent_proposals')
    ad_receiver = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='received_proposals')
    comment = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

