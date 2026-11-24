from django.db import models
from django.conf import settings



class EmailConfirm(models.Model):
    user = models.ForeignKey( settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.code}"


class Task(models.Model):
    STATUS_CHOICES = [ ('pending', 'Pending'), ('in_progress', 'In Progress'), ('finished', 'Finished'), ('cancelled', 'Cancelled'),]
    PRIORITY_CHOICES = [('low', 'Low'),('medium', 'Medium'),('high', 'High'),]
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='tasks')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    priority = models.CharField( max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField( max_length=15, choices=STATUS_CHOICES, default='pending')
    deadline = models.DateField( null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
