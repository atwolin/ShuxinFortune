from django.http import JsonResponse
from django.shortcuts import render
from .models import Fortune


def index(request):
    """Render the main fortune drawing page."""
    return render(request, "lottery/index.html")


def draw_fortune(request):
    """View to draw a random fortune and return it as JSON."""

    fortune = (
        Fortune.objects.filter(is_active=True, category__is_active=True)
        .order_by("?")
        .first()
    )

    if not fortune:
        return JsonResponse({"error": "No fortunes available."}, status=404)

    return JsonResponse(
        {
            "message": fortune.message,
            "category": fortune.category.name,
        }
    )
