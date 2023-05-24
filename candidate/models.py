from django.db import models

# Create your models here.
class Candidate(models.Model):
    name = models.CharField(max_length=255)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=10)
    photo = models.ImageField(upload_to='candidates')
    landmarks = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Detection(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    frame = models.ImageField(upload_to='detection_frames/')

    def __str__(self):
        return f'Detection #{self.id}'