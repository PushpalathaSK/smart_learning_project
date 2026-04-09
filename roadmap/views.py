from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.utils.timezone import now
from datetime import timedelta

import requests

from .models import Domain, RoadmapStage, Topic, UserProgress


# 🔹 HOME PAGE
def home(request):
    domains = Domain.objects.all()
    return render(request, 'roadmap/home.html', {'domains': domains})


# 🔹 ROADMAP VIEW
@login_required
def roadmap_view(request, domain_id):
    domain = Domain.objects.get(id=domain_id)
    stages = RoadmapStage.objects.filter(domain=domain)

    user = request.user
    roadmap_data = []

    for stage in stages:
        topics = Topic.objects.filter(stage=stage)

        topic_data = []

        for topic in topics:
            # 🔥 Better YouTube Query
            query = topic.name + " full course beginner tutorial"

            url = "https://www.googleapis.com/youtube/v3/search"

            params = {
                "part": "snippet",
                "q": query,
                "key": settings.YOUTUBE_API_KEY,
                "maxResults": 3,
                "type": "video",
                "order": "viewCount"
            }

            response = requests.get(url, params=params)
            data = response.json()

            videos = []

            for item in data.get("items", []):
                video_id = item.get("id", {}).get("videoId")

                if not video_id:
                    continue

                videos.append({
                    "title": item["snippet"]["title"],
                    "video_id": video_id
                })

            # 🔹 Progress Check
            progress = UserProgress.objects.filter(user=user, topic=topic).first()
            is_completed = progress.completed if progress else False

            topic_data.append({
                "topic": topic,
                "videos": videos,
                "completed": is_completed
            })

        roadmap_data.append({
            "stage": stage,
            "topics": topic_data
        })

    # 🔹 Progress Calculation
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

    progress_percent = int((completed_topics / total_topics) * 100) if total_topics > 0 else 0

    return render(request, 'roadmap/roadmap.html', {
        'domain': domain,
        'roadmap_data': roadmap_data,
        'progress_percent': progress_percent,
        'next_topic': next_topic
    })


# 🔹 TOGGLE PROGRESS
@login_required
def toggle_progress(request, topic_id):
    user = request.user

    progress, created = UserProgress.objects.get_or_create(
        user=user,
        topic_id=topic_id
    )

    progress.completed = not progress.completed

    if progress.completed:
        progress.completed_date = now().date()
    else:
        progress.completed_date = None

    progress.save()

    return redirect(request.META.get('HTTP_REFERER'))


# 🔹 DASHBOARD WITH STREAK
@login_required
def dashboard(request):
    user = request.user

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

        progress_percent = int((completed_topics / total_topics) * 100) if total_topics > 0 else 0

        dashboard_data.append({
            "domain": domain,
            "progress": progress_percent
        })

    # 🔥 STREAK LOGIC
    today = now().date()

    completed_dates = UserProgress.objects.filter(
        user=user,
        completed=True
    ).values_list('completed_date', flat=True).distinct()

    completed_dates = sorted([d for d in completed_dates if d], reverse=True)

    streak = 0
    current_day = today

    for date in completed_dates:
        if date == current_day:
            streak += 1
            current_day -= timedelta(days=1)
        else:
            break

    return render(request, 'roadmap/dashboard.html', {
        'dashboard_data': dashboard_data,
        'streak': streak
    })

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserCreationForm()

    return render(request, 'roadmap/signup.html', {'form': form})