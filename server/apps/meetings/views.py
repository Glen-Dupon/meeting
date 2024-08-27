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


class ConfigView(BaseView):
    def get(self, request):
        return Response({
            'reserve_start_time': config.RESERVE_START_TIME,
            'reserve_end_time': config.RESERVE_END_TIME,
            'select_date_days': config.SELECT_DATE_DAYS
        })


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


class RoomBaseView(BaseView):
    check_manager = False

    def get_object(self):
        room = models.Room.objects.filter(pk=self.kwargs['room_id']).first()
        if not room:
            raise CoolAPIException(ErrorCode.ERR_MEETING_ROOM_NOT_FOUND)
        if self.check_manager and room.create_user_id != self.request.user.pk:
            raise CoolAPIException(ErrorCode.ERROR_PERMISSION)
        return room


class RoomEditView(RoomBaseView):
    check_manager = True
    serializer_class = app_serializers.RoomSerializer

    def put(self, request, *args, **kwargs):
        room = self.get_object()
        serializer = self.serializer_class(room, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    

class RoomDeleteView(RoomBaseView):
    check_manager = True

    def delete(self, request, *args, **kwargs):
        room = self.get_object()
        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoomInfoView(RoomBaseView):
    serializer_class = app_serializers.RoomDetailSerializer

    def get(self, request, *args, **kwargs):
        room = self.get_object()
        serializer = self.serializer_class(room)
        return Response(serializer.data)
    

class RoomFollowView(BaseView):
    def post(self, request):
        room_ids = request.data.get('room_id', [])
        if len(room_ids) > 50:
            raise CoolAPIException(ErrorCode.ERROR_BAD_PARAMETER)
        for room_id in room_ids:
            self.get_room_follow(room_id, request.user.pk).un_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoomUnFollowView(BaseView):
    def post(self, request):
        room_id = request.data.get('room_id')
        follow = models.UserFollowRoom.objects.filter(room_id=room_id, user_id=request.user.pk).first()
        if not follow:
            raise CoolAPIException(ErrorCode.ERROR_BAD_PARAMETER)
        follow.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowRoomsView(generics.ListAPIView):
    serializer_class = app_serializers.RoomSerializer

    def get_queryset(self):
        return models.Room.objects.filter(
            follows__user_id=self.request.user.pk,
            follows__delete_status=core_constants.DeleteCode.NORMAL.code
        )


class CreateRoomsView(generics.ListAPIView):
    serializer_class = app_serializers.RoomSerializer

    def get_queryset(self):
        return models.Room.objects.filter(create_user_id=self.request.user.pk)


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
                                                               

class EditMeetingView(MeetingBaseView):
    serializer_class = app_serializers.MeetingDetailSerializer

    def put(self, request, *args, **kwargs):
        meeting = self.get_object()
        serializer = self.serializer_class(meeting, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class DeleteMeetingView(MeetingBaseView):
    def delete(self, request, *args, **kwargs):
        meeting = self.get_object()
        meeting.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MeetingInfoView(MeetingBaseView):
    serializer_class = app_serializers.MeetingDetailSerializer

    def get(self, request, *args, **kwargs):
        meeting = self.get_object()
        serializer = self.serializer_class(meeting)
        return Response(serializer.data)


class MeetingAttendeesView(MeetingBaseView):
    serializer_class = app_serializers.MeetingAttendeeSerializer

    def get(self, request, *args, **kwargs):
        meeting = self.get_object()
        attendees = models.MeetingAttendee.objects.filter(meeting_id=meeting.pk)
        serializer = self.serializer_class(attendees, many=True)
        return Response(serializer.data)


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