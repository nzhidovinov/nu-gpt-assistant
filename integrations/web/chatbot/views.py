from django.shortcuts import render


def start(request):
    return render(request, "start.html")


def chatbot(request):
    return render(request, "chatbot.html", context={'bot_name': 'AirportBot'})


def stats(request):
    return render(request, "stats.html")
