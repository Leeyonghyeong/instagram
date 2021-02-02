from django.http import JsonResponse
from django.views import View

# 베이스 뷰 생성


class BaseView(View):
    @staticmethod
    def response(data={}, message='', status=200):
        resutl = {
            'data': data,
            'message': message,
        }
        return JsonResponse(resutl, status)
