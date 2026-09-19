import time

from google import genai
from google.genai import types
from django.conf import settings
from django.core.exceptions import PermissionDenied

from apps.inventory.services import create_draft_purchase_orders, get_low_stock_products

MODEL = "gemini-3.8-flash"
MAX_TOOL_ROUNDS = 5

# عدد محاولات إعادة الاتصال لو الموديل مشغول (503) قبل ما نستسلم
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 3

SYSTEM_INSTRUCTION = (
    
    "أنت مساعد ذكي داخل نظام إدارة مخزون ومبيعات. مهمتك مساعدة المستخدم في "
    "متابعة المخزون وإعداد مسودات طلبات شراء للمنتجات التي أوشكت على النفاد. "
    "استخدم الأدوات المتاحة لك دائماً بدلاً من افتراض أي بيانات، ولا تنشئ "
    "مسودة طلب شراء إلا بعد موافقة صريحة من المستخدم. اجعل ردودك مختصرة وواضحة."
)

_GET_LOW_STOCK = types.FunctionDeclaration(
    name="get_low_stock_products",
    description="Returns every product whose stock is at or below its minimum stock level.",
    parameters_json_schema={"type": "object", "properties": {}},
)

_CREATE_DRAFT_POS = types.FunctionDeclaration(
    name="create_draft_purchase_orders",
    description=(
        "Creates draft purchase orders (one per supplier) for low-stock products. "
        "Only call after the user confirms. Fails with a permission error if the "
        "user isn't allowed to create purchase orders."
    ),
    parameters_json_schema={
        "type": "object",
        "properties": {
            "product_ids": {
                "type": "array",
                "items": {"type": "integer"},
                "description": "Optional product IDs to include. Omit for all low-stock products.",
            }
        },
    },
)

TOOLS = [types.Tool(function_declarations=[_GET_LOW_STOCK, _CREATE_DRAFT_POS])]


class AgentUnavailableError(Exception):
    """بترفع لما الموديل يفضل مشغول بعد كل المحاولات."""
    pass


def _execute_tool(name, args, user):
    if name == "get_low_stock_products":
        products = get_low_stock_products()
        return {
            "products": [
                {
                    "id": p.id,
                    "name": p.name,
                    "sku": p.sku,
                    "stock_quantity": p.stock_quantity,
                    "min_stock_level": p.min_stock_level,
                    "supplier": p.supplier.name if p.supplier else None,
                }
                for p in products
            ]
        }

    if name == "create_draft_purchase_orders":
        try:
            orders = create_draft_purchase_orders(user=user, product_ids=args.get("product_ids"))
        except PermissionDenied as exc:
            return {"success": False, "error": str(exc)}

        if not orders:
            return {"success": False, "message": "No low-stock products to order right now."}

        return {
            "success": True,
            "purchase_orders": [
                {
                    "id": po.id,
                    "supplier": po.supplier.name if po.supplier else "Unknown",
                    "status": po.status,
                    "total_cost": str(po.total_cost),
                    "items": [
                        {"product": i.product.name, "quantity": i.quantity} for i in po.item.all()
                    ],
                }
                for po in orders
            ],
        }

    return {"error": f"Unknown tool: {name}"}


def _serialize_history(contents):
    return [c.model_dump(mode="json", exclude_none=True) for c in contents]


def _deserialize_history(raw_history):
    return [types.Content.model_validate(item) for item in (raw_history or [])]


def _generate_with_retry(client, contents, config):
    """
    بينادي Gemini، ولو رجع خطأ إن الموديل مشغول (503/UNAVAILABLE)
    بيعيد المحاولة كذا مرة مع انتظار بسيط بينهم قبل ما يستسلم.
    """
    last_error = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            return client.models.generate_content(model=MODEL, contents=contents, config=config)
        except Exception as exc:
            last_error = exc
            error_text = str(exc)
            is_busy = "503" in error_text or "UNAVAILABLE" in error_text or "overloaded" in error_text.lower()

            if is_busy and attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS)
                continue

            if is_busy:
                raise AgentUnavailableError(
                    "الخدمة مزدحمة حالياً (الموديل بيستقبل طلبات كتير). "
                    "جرب تبعت الرسالة تاني بعد شوية."
                ) from exc

            # أي خطأ تاني غير الازدحام بنرفعه زي ما هو
            raise

    raise AgentUnavailableError("تعذر الوصول للخدمة، حاول لاحقاً.") from last_error


def run_agent(user, message, history=None):
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    contents = _deserialize_history(history)
    contents.append(types.Content(role="user", parts=[types.Part.from_text(text=message)]))

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        tools=TOOLS,
        automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
    )

    actions = []
    reply_text = ""

    for _ in range(MAX_TOOL_ROUNDS):
        response = _generate_with_retry(client, contents, config)
        model_content = response.candidates[0].content
        contents.append(model_content)

        function_calls = [p.function_call for p in model_content.parts if p.function_call]
        reply_text += "".join(p.text for p in model_content.parts if p.text)

        if not function_calls:
            break

        response_parts = []
        for call in function_calls:
            args = dict(call.args or {})
            result = _execute_tool(call.name, args, user)
            actions.append({"tool": call.name, "input": args, "result": result})
            response_parts.append(types.Part.from_function_response(name=call.name, response=result))
        contents.append(types.Content(role="user", parts=response_parts))
    else:
        reply_text = reply_text or "تعذر إكمال الطلب — عدد كبير جداً من خطوات الأدوات المتتالية."

    return {"reply": reply_text, "actions": actions, "history": _serialize_history(contents)}