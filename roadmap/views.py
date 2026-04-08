from django.shortcuts import render
from .models import Domain
import requests
from django.conf import settings

def home(request):
    domains = Domain.objects.all()
    return render(request, 'roadmap/home.html', {'domains': domains})

from .models import Domain, RoadmapStage, Topic, UserProgress
from django.contrib.auth.models import User
import requests
from django.conf import settings


def roadmap_view(request, domain_id):
    domain = Domain.objects.get(id=domain_id)
    stages = RoadmapStage.objects.filter(domain=domain)

    user = User.objects.first()  # temporary user

    roadmap_data = []

    for stage in stages:
        topics = Topic.objects.filter(stage=stage)

        topic_data = []

        for topic in topics:
            # 🔹 YouTube API
            query = topic.name + " tutorial"

            url = "https://www.googleapis.com/youtube/v3/search"
            params = {
                "part": "snippet",
                "q": query,
                "key": settings.YOUTUBE_API_KEY,
                "maxResults": 2,
                "type": "video",
                "order": "viewCount"   # ⭐ improvement
            }

            response = requests.get(url, params=params)
            data = response.json()

            videos = []

            for item in data.get("items", []):
                video = {
                    "title": item["snippet"]["title"],
                    "video_id": item["id"]["videoId"]
                }
                videos.append(video)

            # 🔹 Progress Logic (NEW)
            progress = UserProgress.objects.filter(user=user, topic=topic).first()
            is_completed = progress.completed if progress else False

            topic_data.append({
                "topic": topic,
                "videos": videos,
                "completed": is_completed   # ⭐ important
            })

        roadmap_data.append({
            "stage": stage,
            "topics": topic_data
        })
        # 🔹 Calculate Progress
        total_topics = 0
        completed_topics = 0
        next_topic = None

        for item in roadmap_data:
            for t in item["topics"]:
                total_topics += 1
                if t["completed"]:
                    completed_topics += 1
                elif not next_topic:
                    next_topic = t["topic"]

        progress_percent = 0
        if total_topics > 0:
            progress_percent = int((completed_topics / total_topics) * 100)

    return render(request, 'roadmap/roadmap.html', {
    'domain': domain,
    'roadmap_data': roadmap_data,
    'progress_percent': progress_percent,
    'next_topic': next_topic
})

from django.shortcuts import redirect
from django.contrib.auth.models import User
from .models import UserProgress

def toggle_progress(request, topic_id):
    user = User.objects.first()  # temporary user (we’ll improve later)

    progress, created = UserProgress.objects.get_or_create(
        user=user,
        topic_id=topic_id
    )

    progress.completed = not progress.completed
    progress.save()

    return redirect(request.META.get('HTTP_REFERER'))

def dashboard(request):
    user = User.objects.first()

    domains = Domain.objects.all()
    dashboard_data = []

    for domain in domains:
        stages = RoadmapStage.objects.filter(domain=domain)

        total_topics = 0
        completed_topics = 0

        for stage in stages:
            topics = Topic.objects.filter(stage=stage)

            for topic in topics:
                total_topics += 1

                progress = UserProgress.objects.filter(user=user, topic=topic).first()
                if progress and progress.completed:
                    completed_topics += 1

        progress_percent = 0
        if total_topics > 0:
            progress_percent = int((completed_topics / total_topics) * 100)

        dashboard_data.append({
            "domain": domain,
            "progress": progress_percent
        })

    return render(request, 'roadmap/dashboard.html', {
        'dashboard_data': dashboard_data
    })