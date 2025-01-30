from django.shortcuts import render

# Create your views here.
from django.http import JsonResponse
from django.views import View
from django.conf import settings
from api.services import calculate_optimal_route


class RouteAPIView(View):
    def get(self, request):
        start = request.GET.get('start')
        end = request.GET.get('end')
        if not start or not end:
            return JsonResponse({'error': 'Missing start or end parameters'}, status=400)
        
        result = calculate_optimal_route(start, end)
        if 'error' in result:
            return JsonResponse(result, status=400)
        return JsonResponse(result)