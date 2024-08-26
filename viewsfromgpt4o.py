from cool.views import  CoolAPIException
from rest_framework import serializers, views, status, generics, mixins, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.db.models import Q
from constance import config
from core import core_constants
import datetime
import json

from . import models, serializers as app_serializers, constants

'''
以下是使用 Django REST Framework 重写的代码，保持了原始功能，但使用了 DRF 的类视图、序列化器和权限机制。
请注意，某些部分如异常处理、权限检查等逻辑需要调整以适应 DRF 的方法。
'''

# Base View
class BaseView(views.APIView):
    permission_classes = [IsAuthenticated]

    def get_room_follow(self, room_id, user_id):
        follow, _ = models.UserFollowRoom.objects.get_or_create(room_id=room_id, user_id=user_id)
        return follow

    def get_date_time_settings(self):
        today = datetime.date.today()
        return {
            'start_time': config.RESERVE_START_TIME,
            'end_time': config.RESERVE_END_TIME,
            'start_date': today,
            'end_date': today + datetime.timedelta(days=config.SELECT_DATE_DAYS),
            'history_start_date': today - datetime.timedelta(days=config.MAX_HISTORY_DAYS),
            'history_end_date': today
        }

class my_BaseView(views.APIView):
    permission_classer = [IsAuthenticated]
    def  get_room_follow(self, room_id, user_id):
        follow , _ = models.UserFollowRoom.objects.get_or_create(room_id = room_id, user_id = user_id)
        return follow
    
    def get_date_time_settings(self):
        today = datetime.date.today()
        return {
            'start_time':config.RESERVE_START_TIME,
            'edn_time':config.RESERVE_END_TIME,
            'start_date':today,
            'end_date':today + datetime.timedelta(days=config.SELECT_DATE_DAYS),
            'history_start_date':today - datetime.timedelta(days=config.MAX_HISTORY_DAYS),
            'history_end_data':today
        }

# Config View
class ConfigView(BaseView):
    def get(self, request):
        return Response({
            'reserve_start_time': config.RESERVE_START_TIME,
            'reserve_end_time': config.RESERVE_END_TIME,
            'select_date_days': config.SELECT_DATE_DAYS
        })
    
class myConfigView(BaseView): 
    def get(selft,request):
        return Response(
            {
                'reserve_start_time':config.RESERVE_START_TIME,
                'reserve_end_time':config.RESERVE_END_TIME,
                'select_date_days':config.SELECT_DATE_DAYS
            }
        )

# Room Create View
class RoomCreateView(generics.CreateAPIView):
    queryset = models.Room.objects.all()
    serializer_class = app_serializers.RoomSerializer

    def perform_create(self, serializer):
        serializer.save(create_user_id=self.request.user.pk)
        obj = serializer.instance
        try:
            obj.qr_code = biz.get_wxa_code_unlimited_file(
                "room_%d.jpg" % obj.pk, scene="room_id=%d" % obj.pk, page="pages/room/detail"
            )
            obj.save(update_fields=['qr_code'])
        except Exception:
            utils.exception_logging.exception("get_wxa_code_unlimited_file", extra={'request': self.request})
        self.get_room_follow(obj.pk, self.request.user.pk)


class myRoomCreateview(generics.CreateAPIView):
    queryset =  models.Room.objects.all()
    serializers_class = app_serializers.RoomSerializer
    def perform_create(self,serializer):
        serializer.save(create_user_id=self.request.user.pk)
        obj = serializer.instance
        try:
            obj.qr_code = biz.get_wxa_code_unlimited_file(
                "room_%d.jpg" % obj.pk, scene="room_id=%d" % obj.pk, page="pages/room/detail"
            )
            obj.save(update_fields=['qi_code'])
        except Exception:
            utils.exception_logging.exception("get_wxa_code_unlimited_file",extra={request:self.request})
        self.get_room_follow(obj.pk,self.request.user.pk)


# Room Base View for Room-related actions
class RoomBaseView(BaseView):
    check_manager = False

    def get_object(self):
        room = models.Room.objects.filter(pk=self.kwargs['room_id']).first()
        if not room:
            raise CoolAPIException(ErrorCode.ERR_MEETING_ROOM_NOT_FOUND)
        if self.check_manager and room.create_user_id != self.request.user.pk:
            raise CoolAPIException(ErrorCode.ERROR_PERMISSION)
        return room

class myRoomBaseView(BaseView):
    check_manager = False
    def get_object(self):
        room = models.Room.objects.filter(pk=self.kwargs['roo_id']).first()
        if not room:
            raise CoolAPIException(ErrorCode.ERR_MEETING_ROOM_NOT_FOUND)
        if self.check_manager and room.create_user_id != self.request.user.pk:
            raise CoolAPIException(ErrorCode.ERROR_PERMISSION)
        return room


# Room Edit View
class RoomEditView(RoomBaseView):
    check_manager = True
    serializer_class = app_serializers.RoomSerializer

    def put(self, request, *args, **kwargs):
        room = self.get_object()
        serializer = self.serializer_class(room, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class myRoomEditView(RoomBaseView):
    check_manager=True
    serilizer_class=app_serializers.RoomSerializer

    #Put会保存用户没有改动的字段吗？
    #区分类 对象 实例
    #区分前端 实例 数据结构 数据库
    def put(self, request, *args, **kwargs):
        # room = models.Room.objects.filter(pk=self.kwargs['room_id']).first()
        room = self.get_object() #在本地获取了用户要编辑的Room的一个对象
        serializer = self.serilizer_class(room,data=request.data,partial=True)#它会把从客户端发送的数据（`request.data`）应用到已经获取到的 `room` 对象上，从而创建了一个特定的序列化器实例。
        serializer.is_valid(raise_exception=True)#验证数据
        serializer.save()#更新对象并持久化到数据库
        return Response(serializer.data)#给前端返回序列化器取出的刚刚保存的数据
    

# Room Delete View
class RoomDeleteView(RoomBaseView):
    check_manager = True

    def delete(self, request, *args, **kwargs):
        room = self.get_object()
        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

# Room Info View
class RoomInfoView(RoomBaseView):
    serializer_class = app_serializers.RoomDetailSerializer

    def get(self, request, *args, **kwargs):
        room = self.get_object()
        serializer = self.serializer_class(room)
        return Response(serializer.data)
    
class myRoomInfoView(RoomBaseView):
    serializer_class = app_serializers.RoomDetailSerializer
    def get(self, request, *args, **kwargs):
        room = self.get_object() #程序内的对象，非返回的数据，因为只是模型计划获取对象，真正获取数据库中的数据还得靠序列化器
        serializer = self.serializer_class(room)
        return Response(serializer.data)

# Room Follow/Unfollow Views
class RoomFollowView(BaseView):
    def post(self, request):
        room_ids = request.data.get('room_id', [])
        if len(room_ids) > 50:
            raise CoolAPIException(ErrorCode.ERROR_BAD_PARAMETER)
        for room_id in room_ids:
            self.get_room_follow(room_id, request.user.pk).un_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class myRoomFloowView(BaseView):   

    def post(self,request):
        room_ids = request.data.get('room_id',[])#默认值防止不存在的id导致异常而设计返回空列表
        if len(room_ids) > 50:
            raise CoolAPIException(ErrorCode.ERROR_BAD_PARAMETER)
        for room_id in room_ids:
            self.get_room_follow(room_id,request.user.pk).un_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class RoomUnFollowView(BaseView):
    def post(self, request):
        room_id = request.data.get('room_id')
        follow = models.UserFollowRoom.objects.filter(room_id=room_id, user_id=request.user.pk).first()
        if not follow:
            raise CoolAPIException(ErrorCode.ERROR_BAD_PARAMETER)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class myRoomUnFollowView(BaseView):
    def post(self,request):
        room_id = request.data.get(room_id)
        follow = models.UserFollowRoom.objects.fileter(room_id=room_id,user_id=request.user.pk).first()
        if not follow:
            raise CoolAPIException(ErrorCode.ERROR_BAD_PRAMETER)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Followed Rooms List View
# generics视图提供了response的封装
class FollowRoomsView(generics.ListAPIView):
    serializer_class = app_serializers.RoomSerializer

    def get_queryset(self):
        return models.Room.objects.filter(
            follows__user_id=self.request.user.pk,
            follows__delete_status=core_constants.DeleteCode.NORMAL.code
        )

class myFollowRoomsView(generics.ListViewAPI):
    serializers_class = app_serializers.RoomSerializer

    def get_queryset(self):
        return models.Room.objects.filter(
            follows__user_id=self.request.user.pk,
            follows__delete_status=core_constants.DeleteCode.NORMAL.code
        )
    

# Created Rooms List View
class CreateRoomsView(generics.ListAPIView):
    serializer_class = app_serializers.RoomSerializer

    def get_queryset(self):
        return models.Room.objects.filter(create_user_id=self.request.user.pk)


class myCreatRoomsView(generics.ListAPIView):
    serializer_class = app_serializers.RoomSerializer
    def get_queryset(self):
        return models.Room.objects.fileter(create_user_id = self.request.user.pk)

# Room Meetings View
# where what when
class RoomMeetingsView(BaseView):
    def get(self, request):
        room_ids = request.query_params.getlist('room_ids', [])
        if len(room_ids) > 10:
            raise CoolAPIException(ErrorCode.ERROR_BAD_PARAMETER)
        date = request.query_params.get('date', datetime.date.today())

        rooms = models.Room.objects.filter(id__in=room_ids).order_by('id')
        meetings = models.Meeting.objects.filter(room_id__in=room_ids, date=date).order_by('start_time')

        ret = self.get_date_time_settings()
        ret.update({
            'rooms': app_serializers.RoomSerializer(rooms, many=True).data,
            'meetings': app_serializers.MeetingSerializer(meetings, many=True).data
        })
        return Response(ret)


class myRoomMeetingsView(BaseView):
    def get(self,request):
        room_ids = request.query_params.getlist('room_ids',[])
        if len(room_ids) > 10:
            raise CoolAPIException(ErrorCode.ErrOR_BAD_PARAMETER)
        date = request.query_params.get('date',datetime.date.today())
        rooms = models.Room.objects.filter(id__in=room_ids).order_by('id')
        meetings = models.Meeting.objects.filter(rood_ids__in=room_ids,date=date).order_by('start_time')
        ret = self.get_date_time_settings()
        ret.update(
            {
                # 'rooms': models.Room.objects.fileter(),
                # 'meetings':models.Meeting.objects.fileter()
                'rooms': app_serializers.RoomSerializer(rooms,many=True).data,
                'meetings':app_serializers.MeetingSerializer(meetings,many=True).data
            }
        )
        return Response(ret)

    
# History Meetings View
class HistoryMeetingsView(RoomBaseView):
    check_manager = True

    def get(self, request, *args, **kwargs):
        room = self.get_object()
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')

        meetings = models.Meeting.objects.filter(
            room_id=room.pk,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date', 'start_time')

        ret = self.get_date_time_settings()
        ret.update({
            'meetings': app_serializers.MeetingSerializer(meetings, many=True).data
        })
        return Response(ret)


# My Meetings View
class MyMeetingsView(BaseView):
    def get(self, request):
        date = request.query_params.get('date', datetime.date.today())

        meeting_ids = models.MeetingAttendee.objects.filter(
            user_id=request.user.pk, meeting__date=date
        ).values_list('meeting', flat=True)

        meetings = models.Meeting.objects.filter(id__in=meeting_ids)
        rooms = models.Room.objects.filter(id__in=set(map(lambda x: x.room_id, meetings)))

        ret = self.get_date_time_settings()
        ret.update({
            'rooms': app_serializers.RoomSerializer(rooms, many=True).data,
            'meetings': app_serializers.MeetingSerializer(meetings, many=True).data
        })
        return Response(ret)

# Meeting Reserve View
class ReserveMeetingView(BaseView):
    serializer_class = app_serializers.MeetingDetailSerializer

    def post(self, request):
        data = request.data
        if data['start_time'] >= data['end_time']:
            raise CoolAPIException(ErrorCode.ERROR_BAD_PARAMETER)
        if not self.time_ok(data['start_time']) or not self.time_ok(data['end_time']):
            raise CoolAPIException(ErrorCode.ERROR_BAD_PARAMETER)
        now = datetime.datetime.now()
        if data['date'] == now.date() and data['start_time'] < now.time():
            raise CoolAPIException(ErrorCode.ERR_MEETING_ROOM_TIMEOVER)

        with transaction.atomic():
            if models.Meeting.objects.filter(room_id=data['room_id'], date=data['date']).filter(
                    Q(start_time__lte=data['start_time']) & Q(end_time__gt=data['start_time']) |
                    Q(start_time__lt=data['end_time']) & Q(end_time__gte=data['end_time']) |
                    Q(start_time__lte=data['start_time']) & Q(start_time__gt=data['end_time']) |
                    Q(end_time__lt=data['start_time']) & Q(end_time__gte=data['end_time'])
            ).select_for_update().exists():
                raise CoolAPIException(ErrorCode.ERR_MEETING_ROOM_INUSE)
            meeting = models.Meeting.objects.create(
                user_id=request.user.pk,
                room_id=data['room_id'],
                name=data['name'],
                description=data['description'],
                date=data['date'],
                start_time=data['start_time'],
                end_time=data['end_time'],
            )
            models.MeetingAttendee.objects.create(user_id=request.user.pk, meeting_id=meeting.pk)
        self.get_room_follow(data['room_id'], request.user.pk)
        return Response(self.serializer_class(meeting).data)


class myReserveMeetingView(BaseView):
    serializer = app_serializers.MeetingDetailSerializer

    
    def post(self,request):
        data =  request.data
        if data['start_time'] >= data['end_time']:
            raise CoolAPIException(ErrorCode.ERROR_BAD_PARAMETER)
        if not self.time_ok(data['start_time']) or self.time_ok(data['end_time']):
            raise CoolAPIException(ErrorCode.ERROR_BAD_PARAMETER)
        now = datetime.time.now()
        # nowdate = datetime.date.today()

        if data['date'] >= now.date() and data['start_time'] < now.time():
            raise CoolAPIException(ErrorCode.ERR_MEETING_ROOM_TIMEOVER)
        
        with transaction.atomic():
            # if models.Meeting.objects.filter(room_id=data['room_id'], date=data['date']).filter(
            #         Q(start_time__lte=data['start_time']) & Q(end_time__gt=data['start_time']) |
            #         Q(start_time__lt=data['end_time']) & Q(end_time__gte=data['end_time']) |
            #         Q(start_time__lte=data['start_time']) & Q(start_time__gt=data['end_time']) |
            #         Q(end_time__lt=data['start_time']) & Q(end_time__gte=data['end_time'])
            # ).select_for_update().exists():
            #     raise CoolAPIException(ErrorCode.ERR_MEETING_ROOM_INUSE)
            
            if models.Meeting.objects.filter(
                Q(start_time__lte=data['start_time']) & Q(end_time__gt=data['start_time']) |
                Q(start_time__lt=data['end_time']) & Q(end_time__gte=data['end_time']) |
                Q(start_time__lte=data['start_time']) & Q(start_time__gt=data['end_time']) |
                Q(end_time__lt=data['start_time']) & Q(end_time__gte=data['end_time'])
            ).exists().select_for_update().exists():
                raise CoolAPIException(ErrorCode.ERR_MEETING_ROOM_INUSE)

            meeting = models.Meeting.objects.create(
                name = request.user.pk,
                description = request.data['description'],
                user = request.user.pk,
                room = request.data['room_id'],
                date = request.data['date'],
                start_time = request.data['start_time'],
                end_time = request.data['end_time']
            )
            models.MeetingAttendee.objects.create(user_id=request.user.pk,meeting_id=meeting.pk)

        return Response(self.serializer_class(meeting).data)

# Meeting Base View
class MeetingBaseView(BaseView):
    check_manager = False
    check_meeting_time = True

    def get_object(self):
        meeting = models.Meeting.objects.filter(pk=self.kwargs['meeting_id']).first()
        if not meeting:
            raise CoolAPIException(ErrorCode.ERR_MEETING_NOT_FOUND)
        if self.check_manager and meeting.user_id != self.request.user.pk:
            raise CoolAPIException(ErrorCode.ERROR_PERMISSION)
        if self.check_meeting_time and datetime.datetime.combine(meeting.date, meeting.end_time) < datetime.datetime.now():
            raise CoolAPIException(ErrorCode.ERR_MEETING_ROOM_TIMEOVER)
        return meeting


class myMettingBaseView(BaseView):
    check_manager = False
    check_meeting_time = True

    def get_object(self):
        meeting = models.Meeting.objects.filter(pk=self.kwargs['meeting_id']).first()
        if not meeting:
            raise CoolAPIException(ErrorCode.ERR_MEETING_NOT_FOUND)
        if self.check_manager and meeting.user_id != self.request.user.pk:
            raise CoolAPIException(ErrorCode.ERROR_PERMISSION)
        if self.check_meeting_time and datetime.datetime.combine(meeting.data,meeting.end_time) < datetime.datetime.now():
            raise CoolAPIException(ErrorCode.ERR_MEETING_ROOM_TIMEOVER)
        return meeting
                                                               

# Edit Meeting View
class EditMeetingView(MeetingBaseView):
    serializer_class = app_serializers.MeetingDetailSerializer

    def put(self, request, *args, **kwargs):
        meeting = self.get_object()
        serializer = self.serializer_class(meeting, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class myEidtMeetingView(MeetingBaseView):
    serializer_class = app_serializers.MeetingDetailSerializer

    def put(self,request,*args,**kwargs):
        meeting = self.get_object()
        serializer = self.serializer_class(meeting,data=request.data,partital=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# Delete Meeting View
class DeleteMeetingView(MeetingBaseView):
    def delete(self, request, *args, **kwargs):
        meeting = self.get_object()
        meeting.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class myDeleteMeetingView(MeetingBaseView):
    def delete(self,request,*args,**kwargs):
        meeting = self.get_object()
        meeting.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# Meeting Info View
class MeetingInfoView(MeetingBaseView):
    serializer_class = app_serializers.MeetingDetailSerializer

    def get(self, request, *args, **kwargs):
        meeting = self.get_object()
        serializer = self.serializer_class(meeting)
        return Response(serializer.data)


class myMeetingInfoView(MeetingBaseView):
    serializer_class = app_serializers.MeetingDetailSerializer

    def get(self,request,*args,**kwargs):
        meeting = self.get_object()
        serializer = self.serializer_class(meeting)
        return Response(serializer.data)
    

# Meeting Attendees View
class MeetingAttendeesView(MeetingBaseView):
    serializer_class = app_serializers.MeetingAttendeeSerializer

    def get(self, request, *args, **kwargs):
        meeting = self.get_object()
        attendees = models.MeetingAttendee.objects.filter(meeting_id=meeting.pk)
        serializer = self.serializer_class(attendees, many=True)
        return Response(serializer.data)


class myMeetingAttendeesView(MeetingBaseView):
    serializer_class = app_serializers.MeetingAttendeeSerializer
    def get(self,request,*args,**kwargs):
        meeting = self.get_object()
        attendees = models.MeetingAttendee.object.filter(meeting_id=meeting.id)
        serializer = self.serializer_class(attendees,many=True)
        return Response(serializer)


# Add/Remove Attendees View
class EditMeetingAttendeesView(MeetingBaseView):
    serializer_class = app_serializers.MeetingAttendeeSerializer

    def post(self, request, *args, **kwargs):
        meeting = self.get_object()
        user_ids = request.data.get('user_ids', [])
        if not user_ids or len(user_ids) > 50:
            raise CoolAPIException(ErrorCode.ERROR_BAD_PARAMETER)
        attendees = []
        for user_id in user_ids:
            if models.MeetingAttendee.objects.filter(meeting_id=meeting.pk, user_id=user_id).exists():
                continue
            attendees.append(models.MeetingAttendee(meeting_id=meeting.pk, user_id=user_id))
        models.MeetingAttendee.objects.bulk_create(attendees)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, *args, **kwargs):
        meeting = self.get_object()
        user_id = request.data.get('user_id')
        attendee = models.MeetingAttendee.objects.filter(meeting_id=meeting.pk, user_id=user_id).first()
        if not attendee:
            raise CoolAPIException(ErrorCode.ERROR_BAD_PARAMETER)
        attendee.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class myEditMeetingAttendeesView(MeetingBaseView):
    serializer_class = app_serializers.MeetingAttendeeSerializer

    def post(self,request, *rags, **kwargs):
        meeting = self.get_object()
        user_ids = request.data.get(user_ids,[])
        if not user_ids or len(user_ids) > 50:
            raise CoolAPIException(ErrorCode.ERROR_BAD_PARAMETER)
        attendees = []
        for user_id in user_ids:
            if models.MeetingAttendee.objects.filter(meeting_id = meeting.pk,user_id = user_id).exist():#对象层 是否可以用缓存来提高性能？
                continue
            attendees.append(models.MeetingAttendee(meeting_id=meeting.pk,user_id = user_id)) #模型层 Meeting.pk 来自get_Object()方法  user_id 来自request.data，所以并没有去访问数据库！
        models.MeetingAttendee.objects.bulk_create(attendees) #对象层
        return Response(status=status.HTTP_204_NO_CONTENT)


    def delete(self,request, *rags, **kwargs):
        meeting = self.get_object()
        user_id = request.data.get('user_ids')
        attendee = models.MeetingAttendee.objects.filter(meeting_id=meeting.pk,user_id=user_id)
        if not attendee:
            raise CoolAPIException(ErrorCode.ERROR_BAD_PARAMETER)
        attendee.delete()
        return Response(status = status.HTTP_204_NO_CONTENT)

'''
主要调整：
APIView 用作基础视图。
generics.CreateAPIView, ListAPIView 用于创建和列表视图。
Serializer 用于序列化数据。
事务 在视图中处理，并且数据库操作是在事务上下文中进行的。
权限 通过 permission_classes 属性来处理。
该代码保持了原有的功能，并对 Django REST Framework 进行了优化，使其更加清晰、模块化和遵循 DRF 的最佳实践。
如果你需要更多的帮助或有任何问题，请告诉我。
'''