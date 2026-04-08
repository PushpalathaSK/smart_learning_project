from django.contrib import admin
from .models import Domain, RoadmapStage, Topic

admin.site.register(Domain)
admin.site.register(RoadmapStage)
admin.site.register(Topic)

from .models import UserProgress
admin.site.register(UserProgress)