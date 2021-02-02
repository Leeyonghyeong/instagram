from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch

from .models import Content, FollowRelations

# Create your views here.


@method_decorator(login_required, name='dispatch')
class HomeView(TemplateView):
    # @method_decorator(login_required)
    # def dispatch(self, request, *args, **kwargs):
    #     return super(HomeView, self).dispatch(request, *args, **kwargs)

    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super(HomeView, self).get_context_data(**kwargs)

        user = self.request.user
        followees = FollowRelations.objects.filter(
            follower=user).values_list('followee__id', flat=True)
        lookup_user_ids = [user.id] + list(followees)
        context['contents'] = Content.objects.select_related(
            'user').prefetch_related('image_set').filter(user__id__in=lookup_user_ids)

        return context


@method_decorator(login_required, name='dispatch')
class RelationView(TemplateView):

    template_name = 'relation.html'

    def get_context_data(self, **kwargs):
        context = super(RelationView, self).get_context_data(**kwargs)

        user = self.request.user

        # 내가 팔로우 하는 사람들
        try:
            followers = FollowRelations.objects.get(
                follower=user).followee.all()
            context['followees'] = followers
            context['followees_ids'] = list(
                followers.values_list('id', flat=True))
        except FollowRelations.DoesNotExist:
            context['followees_ids'] = [0, 0]

        context['followers'] = FollowRelations.objects.select_related(
            'follower').filter(followee__in=[user])
        return context
