import json

from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .services.agent import run_agent


@login_required
@permission_required('inventory.can_create_draft_po', raise_exception=True)
@require_POST
def chat_view(request):
    """
    POST body: {"message": "...", "history": [...]}   (history optional —
    it's whatever this endpoint returned last time, the frontend just
    stores it and sends it back so the conversation continues).

    Response: {"reply": "...", "actions": [...], "history": [...]}

    استخدام الشات بوت كله محجوز لصاحب صلاحية can_create_draft_po (المالك
    حالياً)، مش بس عملية إنشاء المسودة. أي مستخدم تاني هياخد 403 قبل ما
    يوصل لـ Gemini أصلاً.
    """
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    message = (data.get("message") or "").strip()
    if not message:
        return JsonResponse({"error": "'message' is required."}, status=400)

    result = run_agent(user=request.user, message=message, history=data.get("history"))
    return JsonResponse(result)