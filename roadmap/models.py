from django.db import models

# Domain Model
class Domain(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


# Roadmap Stage Model
class RoadmapStage(models.Model):
    domain = models.ForeignKey(Domain, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.domain.name} - {self.name}"


# Topic Model
class Topic(models.Model):
    stage = models.ForeignKey(RoadmapStage, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.name
    
from django.contrib.auth.models import User

class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.topic.name}"