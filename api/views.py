from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.core.validators import validate_email, ValidationError
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from contents.models import Content, Image, FollowRelations


# 베이스 뷰 생성
@method_decorator(csrf_exempt, name='dispatch')
class BaseView(View):

    @staticmethod
    def response(data={}, message='', status=200):
        result = {
            'data': data,
            'message': message,
        }

        return JsonResponse(result, status=status)


# 유저 생성 뷰
class UserCreateView(BaseView):

    def post(self, request):
        username = request.POST.get('username', '')
        if not username:
            return self.response(message='아이디를 입력해주세요.', status=400)

        password = request.POST.get('password', '')
        if not password:
            return self.response(message='비밀번호를 입력해주세요.', status=400)

        re_password = request.POST.get('re_password', '')
        if not re_password:
            return self.response(message='비밀번호 확인을 입력해주세요.', status=400)

        email = request.POST.get('email', '')
        try:
            validate_email(email)
        except ValidationError:
            return self.response(message='이메일을 입력해주세요.', status=400)

        if password != re_password:
            return self.response(message='비밀번호가 일치하지 않습니다.', status=400)

        try:
            user = User.objects.create_user(username, email, password)
        except IntegrityError:
            return self.response(message='이미 존재하는 아이디입니다.', status=400)

        return self.response({'user.id': user.id})


# 유저 로그인 뷰
class UserLoginView(BaseView):
    def post(self, request):
        username = request.POST.get('username')
        if not username:
            return self.response(message='아이디를 입력해 주세요', status=400)

        password = request.POST.get('password')
        if not password:
            return self.response(message='비밀번호를 입력해 주세요', status=400)

        user = authenticate(request, username=username, password=password)

        if user is None:
            return self.response(message='입력 정보를 다시 확인해 주시기 바랍니다.', status=400)

        login(request, user)

        return self.response()


# 유저 로그아웃 뷰
class UserLogoutView(BaseView):
    def get(self, request):
        logout(request)

        return self.response()


# 콘텐츠 생성 뷰
@method_decorator(login_required, name='dispatch')
class ContentCreateView(BaseView):
    def post(self, request):
        text = request.POST.get('text', '').strip()
        content = Content.objects.create(user=request.user, text=text)

        for idx, file in enumerate(request.FILES.values()):
            Image.objects.create(content=content, image=file, order=idx)

        return self.response()


# 팔로우 뷰
@method_decorator(login_required, name='dispatch')
class RelationCreateView(BaseView):

    def post(self, request):
        try:
            user_id = request.POST.get('id', '')
        except ValueError:
            return self.response(message='잘못된 요청입니다.', status=400)

        try:
            relation = FollowRelations.objects.get(follower=request.user)
        except FollowRelations.DoesNotExist:
            relation = FollowRelations.objects.create(follower=request.user)

        try:
            if user_id == request.user.id:
                # 자기 자신은 팔로우 안됨.
                raise IntegrityError
            relation.followee.add(user_id)
            relation.save()
        except IntegrityError:
            return self.response(message='잘못된 요청입니다.', status=400)

        return self.response()


# 언팔로우 뷰
@method_decorator(login_required, name='dispatch')
class RelationDeleteView(BaseView):

    def post(self, request):
        try:
            user_id = request.POST.get('id', '')
        except ValueError:
            return self.response(message='잘못된 요청입니다.', status=400)

        try:
            relation = FollowRelations.objects.get(follower=request.user)
        except FollowRelations.DoesNotExist:
            return self.response(message='잘못된 요청입니다.', status=400)

        try:
            if user_id == request.user.id:
                # 자기 자신은 언팔로우 안됨.
                raise IntegrityError
            relation.followee.remove(user_id)
            relation.save()
        except IntegrityError:
            return self.response(message='잘못된 요청입니다.', status=400)

        return self.response()


# 유저 검색 뷰
class UserGetView(BaseView):

    def get(self, request):
        username = request.GET.get('username', '').strip()

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return self.response(message='사용자를 찾을 수 없습니다.', status=404)

        return self.response({'username': username, 'email': user.email, 'id': user.id})
