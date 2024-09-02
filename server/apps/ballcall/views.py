from __future__ import absolute_import, unicode_literals
import datetime
import json
from cool.views import ViewSite, CoolAPIException, ErrorCode, mixins
from cool.views.fields import SplitCharField
from rest_framework import fields
from constance import config
from django.db import transaction
from django.db.models import Q
from apps.wechat import biz
from apps.wechat.views import UserBaseView
from core import utils, constants as core_constants
from . import models, serializer, constants

site = ViewSite(name='meetings', app_name='meetings')


class BaseView(UserBaseView):

    @staticmethod
    def get_room_follow(room_id, user_id):
        follow, _ = models.UserFollowRoom.default_manager.get_or_create(
            room_id=room_id, user_id=user_id
        )
        return follow

    @classmethod
    def response_info_date_time_settings(cls):
        return {
            'start_time': '开始时间',
            'end_time': '结束时间',
            'start_date': '开始日期',
            'end_date': '结束日期',
            'history_start_date': '历史开始日期',
            'history_end_date': '历史结束日期'
        }

    @staticmethod
    def get_date_time_settings():
        today = datetime.date.today()
        return {
            'start_time': config.RESERVE_START_TIME,
            'end_time': config.RESERVE_END_TIME,
            'start_date': today,
            'end_date': today + datetime.timedelta(days=config.SELECT_DATE_DAYS),
            'history_start_date': today - datetime.timedelta(days=config.MAX_HISTORY_DAYS),
            'history_end_date': today
        }

    def get_context(self, request, *args, **kwargs):
        raise NotImplementedError

    class Meta:
        path = '/'

@site
class Config(BaseView):
    name = "配置信息"

    def get_context(self, request, *args, **kwargs):
        return {
            'reserve_start_time': config.RESERVE_START_TIME,
            'reserve_end_time': config.RESERVE_END_TIME,
            'select_date_days': config.SELECT_DATE_DAYS
        }

'''
part of place
CRUD
'''
class PlaceBase(BaseView):
    check_manager = False

# R U D
## create place
@site
class CreatePlace(mixins.AddMixin, BaseView):
    model = models.Place
    response_info_serializer_class = serializer.PlaceSerializer
    add_fields = ['name', 'description', 'create_user_manager']

    # def init_fields(self, request, obj):
    #     obj.create_user_id = request.user.pk
    #     # obj.create_user_id = request.user.pk if request.user.pk else "sysadmin"
    #     super().init_fields(request, obj)

    # def save_obj(self, request, obj):
    #     super().save_obj(request, obj)
    #     try:
    #         obj.qr_code = biz.get_wxa_code_unlimited_file(
    #             "room_%d.jpg" % obj.pk, scene="room_id=%d" % obj.pk, page="pages/room/detail"
    #         )
    #         obj.save(update_fields=['qr_code', ], force_update=True)
    #     except Exception:
    #         utils.exception_logging.exception("get_wxa_code_unlimited_file", extra={'request': request})
    #     self.get_room_follow(obj.pk, request.user.pk)

## retrive place
@site
class PlaceInfo(PlaceBase):
    model = models.Place
    response_info_serializer_class = serializer.PlaceSerializer
    add_fields = ['name', 'type','num','description', 'create_user_manager']

## update place
@site    
class editPlace(PlaceBase):
    model = models.Place
    response_info_serializer_class = serializer.PlaceSerializer
    add_fields = ['name', 'type','num','description', 'create_user_manager']

## delete place
@site
class deletePlace(PlaceBase):
    model = models.Place
    response_info_serializer_class = serializer.PlaceSerializer
    add_fields = ['name', 'type','num','description']

#user follow place
@site
class UserFollowPlace(BaseView):
    model = models.Place
    response_info_serializer_class = serializer.PlaceSerializer
    add_fields = ['name', 'type','num','description']

#user unfollow place
@site
class UserunFollowPlace(BaseView):
    model = models.Place
    response_info_serializer_class = serializer.PlaceSerializer
    add_fields = ['name', 'type','num','description']

'''
part of court
CRUD
'''

class CourtBase(BaseView):
    check_manager = False

# R U D
## create court
@site
class CreateCourt(mixins.AddMixin, CourtBase):
    model = models.Court
    response_info_serializer_class = serializer.CourtSerializer
    add_fields = ['name', 'type','num','description']

## retrive court
@site
class CourtInfo(CourtBase):
    model = models.Court
    response_info_serializer_class = serializer.CourtSerializer
    add_fields = ['name', 'type','num','description']

## update court
@site    
class editCourt(CourtBase):
    model = models.Court
    response_info_serializer_class = serializer.CourtSerializer
    add_fields = ['name', 'type','num','description']

@site
class deleteCourt(CourtBase):
    model = models.Court
    response_info_serializer_class = serializer.CourtSerializer
    add_fields = ['name', 'type','num','description']

#user follow court 实际业务中用户是否需要关注场地？
@site
class UserFollowCourt(CourtBase):
    model = models.Court
    response_info_serializer_class = serializer.CourtSerializer
    add_fields = ['name', 'type','num','description']

@site
class UserunFollowCourt(CourtBase):
    model = models.Court
    response_info_serializer_class = serializer.CourtSerializer
    add_fields = ['name', 'type','num','description']


'''
part of game template
CRUD
'''

#create Game template
@site
class CreateGameTemplate(mixins.AddMixin, BaseView):
    model = models.GameTemplate
    response_info_serializer_class = serializer.GameTemplateSerializer
    add_fields = ['name', 'type','num','description']

class GameBase(BaseView):
    check_manager = False

# R U D
@site
class GameTemplateInfo(GameBase):
    model = models.GameTemplate
    response_info_serializer_class = serializer.GameTemplateSerializer
    add_fields = ['name', 'type','num','description']


@site    
class editGameTemplate(GameBase):
    model = models.GameTemplate
    response_info_serializer_class = serializer.GameTemplateSerializer
    add_fields = ['name', 'type','num','description']

@site    
class deleteGameTemplate(GameBase):
    model = models.GameTemplate
    response_info_serializer_class = serializer.GameTemplateSerializer
    add_fields = ['name', 'type','num','description']

'''
part of game
CRUD
'''

#create Game template
@site
class CreateGame(mixins.AddMixin, BaseView):
    model = models.Game
    response_info_serializer_class = serializer.GameTemplateSerializer
    add_fields = ['name', 'type','num','description']

class GameBase(BaseView):
    check_manager = False


# R U D
@site
class GameInfo(GameBase):
    model = models.Game
    response_info_serializer_class = serializer.GameSerializer
    add_fields = ['name', 'type','num','description']


@site    
class editGame(GameBase):
    model = models.Game
    response_info_serializer_class = serializer.GameSerializer
    add_fields = ['name', 'type','num','description']


#发起人取消活动
@site
class CancelGame(GameBase):
    name = "取消会议" 
    model = models.Game
    response_info_serializer_class = serializer.GameSerializer

    def get_context(self, request, *args, **kwargs):
        pass


#user follow game
@site
class UserFollowGame(GameBase):
    model = models.Court
    response_info_serializer_class = serializer.GameSerializer
    add_fields = ['name', 'type','num','description']

@site
class UserunFollowGame(GameBase):
    model = models.Court
    response_info_serializer_class = serializer.GameSerializer
    add_fields = ['name', 'type','num','description']

#用户参加活动
@site
class UserJoinGame(GameBase):
    name = "参加活动"
    def get_context(self, request, *args, **kwargs):
        pass

#用户退出活动
@site
class Leave(GameBase):
    name = "退出活动"

    def get_context(self, request, *args, **kwargs):
        pass

#展示其他已经成行的活动给用户，提高氛围感
#用户结束打球后评价其他用户

urlpatterns = site.urlpatterns
app_name = site.app_name