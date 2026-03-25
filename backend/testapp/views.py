from django.http import JsonResponse
from .models import TestMessage
from django.views.decorators.csrf import csrf_exempt
import json


@csrf_exempt
def test_api(request):

        if request.method == "GET":
            messages = list(TestMessage.objects.all().values())
            return JsonResponse(messages, safe=False)
        
        if request.method == "POST":
            data = json.loads(request.body)
            message_text = data.get("message")

            new_message = TestMessage.objects.create(
                message=message_text
            )

            return JsonResponse({
                "id": new_message.id,
                "message": new_message.message
            })
