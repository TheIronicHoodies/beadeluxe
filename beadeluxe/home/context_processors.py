from django.utils import timezone

def greeting(request):
    now = timezone.localtime()
    hour = now.hour

    if 5 <= hour < 12:
        greeting = "☀️ Good morning"
    elif 12 <= hour < 18:
        greeting = "🌤️ Good afternoon"
    else:
        greeting = "🌙 Good evening"

    return {"greeting": greeting}