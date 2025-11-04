from rest_framework.views import APIView
from rest_framework.response import Response


class BaseAPIView(APIView):

    # Temporary fix for the Django django-remote-form-helpers library
   def get(self, request, *args, **kwargs):
        data = self.get_data(request.query_params)

        return Response(data)