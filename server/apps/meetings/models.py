# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from django.db import models
from django.contrib import admin

from apps.wechat.models import User
from core import utils
from core.constants import DeleteCode
from core.utils import admin_register

from . import constants

@admin_register(addable=True, changeable=False, list_display=['create_user', ])
class Room(utils.BaseModel):
    name = models.CharField(verbose_name='名称', default='', max_length=64)
    description = models.CharField(verbose_name='描述', default='', max_length=255, blank=True)
    create_user = utils.ForeignKey(User, verbose_name='创建人', related_name='create_rooms', editable=False, default='1001')
    qr_code = models.ImageField('二维码', upload_to="%Y/%m/%d/", max_length=512, null=False, default='', editable=False)
    create_user_manager = models.BooleanField(verbose_name='创建人管理权限', default=False,
                                              help_text='会议室创建人可以管理该会议室内所有会议')

    class Meta:
        verbose_name = verbose_name_plural = "会议室"


@admin_register(addable=False, changeable=False, list_display=['room', 'user'], list_filter=['room', ])
class UserFollowRoom(utils.BaseModel):
    user = utils.ForeignKey(User, verbose_name='关注人', editable=False)
    room = utils.ForeignKey(Room, verbose_name='会议室', related_name='follows', editable=False)

    class Meta:
        unique_together = ('user', 'room')
        verbose_name = verbose_name_plural = "用户关注会议室"


@admin_register(addable=False, changeable=False, list_display=['room', 'user'], list_filter=['date', 'room'])
class meeting(utils.BaseModel):
    name = models.CharField(verbose_name='名称', default='', max_length=64)
    description = models.CharField(verbose_name='描述', default='', max_length=255, blank=True)
    user = utils.ForeignKey(User, verbose_name='发起人', related_name='reserve_meetings', editable=False)
    room = utils.ForeignKey(Room, verbose_name='会议室', editable=False)
    date = models.DateField(verbose_name='会议日期', db_index=True, editable=False)
    start_time = models.TimeField(verbose_name='开始时间', editable=False)
    end_time = models.TimeField(verbose_name='结束时间', editable=False)

    @property
    def attendees(self):
        return User.objects.filter(
            meetingattendee__meeting_id=self.pk, meetingattendee__delete_status=DeleteCode.NORMAL.code
        )

    class Meta:
        verbose_name = verbose_name_plural = "会议"


@admin_register(addable=False, changeable=False, list_display=['meeting', 'user'])
class meetingAttendee(utils.BaseModel):
    meeting = utils.ForeignKey(meeting, verbose_name='会议', editable=False)
    user = utils.ForeignKey(User, verbose_name='参与人', editable=False)

    class Meta:
        unique_together = ('user', 'meeting')
        verbose_name = verbose_name_plural = "参会人"


@admin_register(addable=False, changeable=False, list_display=['meeting', 'user'], list_filter=['owner', 'type'])
class meetingTrace(utils.BaseModel):
    meeting = utils.ForeignKey(meeting, verbose_name='会议')
    user = utils.ForeignKey(User, verbose_name='操作人')
    owner = models.BooleanField(verbose_name='是否发起人自己操作')
    type = models.IntegerField(verbose_name='操作类型', choices=constants.meetingTraceTypeCode.get_choices_list())
    data = models.CharField(verbose_name='详细信息', max_length=4096, default='')

    class Meta:
        verbose_name = verbose_name_plural = "会议操作历史"
