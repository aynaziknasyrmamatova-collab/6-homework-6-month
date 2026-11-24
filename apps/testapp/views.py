from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import RegisterSerializer
from .tasks import send_welcome_email_task


class RegisterView(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        send_welcome_email_task.delay(user.pk)
        return Response(
            {"id": user.pk, "username": user.username, "email": user.email},
            status=status.HTTP_201_CREATED,
        )
