import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .services.agent import run_agent, AgentUnavailableError


@login_required
@require_POST
def chat_view(request):
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    message = (data.get("message") or "").strip()
    if not message:
        return JsonResponse({"error": "'message' is required."}, status=400)

    try:
        result = run_agent(user=request.user, message=message, history=data.get("history"))
    except AgentUnavailableError as exc:
        # الموديل مشغول بعد كل محاولات إعادة الاتصال - رسالة عربي واضحة بدل الخطأ الخام
        return JsonResponse({"error": str(exc)}, status=503)
    except Exception as exc:
        return JsonResponse({"error": f"حصل خطأ أثناء تنفيذ الطلب: {exc}"}, status=500)

    return JsonResponse(result)