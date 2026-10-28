import json

from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from . import ingest, service
from .models import Document


def index(request):
    """Single page: upload form, question form, answer + citations."""
    ctx = {"documents": Document.objects.all(), "messages": []}
    if request.method == "POST":
        if request.FILES:
            for f in request.FILES.getlist("files"):
                try:
                    ingest.ingest(f.name, f)
                    ctx["messages"].append(("ok", f"Indexed {f.name}"))
                except Exception as exc:
                    ctx["messages"].append(("error", f"{f.name}: {exc}"))
            ctx["documents"] = Document.objects.all()
        question = request.POST.get("question", "").strip()
        if question:
            ctx["result"] = service.ask(question)
    return render(request, "rag/index.html", ctx)


@require_POST
def delete_document(request, pk):
    Document.objects.filter(pk=pk).delete()
    return redirect("index")


@csrf_exempt  # JSON API for scripts/curl; the demo has no auth or sessions
@require_POST
def api_ask(request):
    try:
        question = str(json.loads(request.body or b"{}").get("question", "")).strip()
    except (ValueError, AttributeError):
        return JsonResponse({"error": "Body must be JSON like {\"question\": \"...\"}"}, status=400)
    if not question:
        return JsonResponse({"error": "'question' is required"}, status=400)
    return JsonResponse(service.ask(question), json_dumps_params={"ensure_ascii": False})
