# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from rest_framework import serializers

from apps.wechat.models import User
from apps.wechat.serializer import UserSerializer
from core import utils
from . import models

from .models import Player, Game, Place, Court, MatchInfo, GameAttendee, UserFollowGame, GameTrace
from .models import Tenant, GameTemplate, Setting, UserFollowPlace, PayRecord, Grade, Lable, WorkOrder

class PlayerSerializer(utils.BaseSerializer):
    class Meta:
        model = Player
        fields = '__all__'

class PlaceSerializer(utils.BaseSerializer):
    class Meta:
        model = Place
        fields = '__all__'

class CourtSerializer(utils.BaseSerializer):
    class Meta:
        model = Court
        fields = '__all__'

class GameSerializer(utils.BaseSerializer):
    
    initiator = UserSerializer(many=False, read_only=True) # 发起人就是微信用户
    place = PlaceSerializer(many=False, read_only=True)
    court = CourtSerializer(many=False, read_only=True)
    attendees = UserSerializer(many=True, read_only=True)
    # is_manager = serializers.SerializerMethodField("func_is_manager")

    # def func_is_manager(self, obj):
    #     if self.request is None or not isinstance(self.request.user, User):
    #         return False
    #     return self.request.user.pk == obj.user_id or (
    #             obj.room.create_user_manager and self.request.user.pk == obj.room.create_user_id
    #     )

    class Meta:
        model = Game
        fields = '__all__'

class GameAttendeeSerializer(utils.BaseSerializer):
    class Meta:
        model = GameAttendee
        fields = '__all__'

class UserFollowGameSerializer(utils.BaseSerializer):
    class Meta:
        model = UserFollowGame
        fields = '__all__'

class GameTraceSerializer(utils.BaseSerializer):
    class Meta:
        model = GameTrace
        fields = '__all__'

class TenantSerializer(utils.BaseSerializer):
    class Meta:
        model = Tenant
        fields = '__all__'

class GameTemplateSerializer(utils.BaseSerializer):
    class Meta:
        model = GameTemplate
        fields = '__all__'

class SettingSerializer(utils.BaseSerializer):
    class Meta:
        model = Setting
        fields = '__all__'

class UserFollowPlaceSerializer(utils.BaseSerializer):
    class Meta:
        model = UserFollowPlace
        fields = '__all__'

class PayRecordSerializer(utils.BaseSerializer):
    class Meta:
        model = PayRecord
        fields = '__all__'

class GradeSerializer(utils.BaseSerializer):
    class Meta:
        model = Grade
        fields = '__all__'

class LableSerializer(utils.BaseSerializer):
    class Meta:
        model = Lable
        fields = '__all__'

class MatchInfoSerializer(utils.BaseSerializer):
    class Meta:
        model = MatchInfo
        fields = '__all__'
        
class WorkOrderSerializer(utils.BaseSerializer):
    class Meta:
        model = WorkOrder
        fields = '__all__'