# encoding: utf-8
from __future__ import absolute_import, unicode_literals
from django.db import models
from django.contrib import admin
from apps.wechat.models import User
from core import utils
from core.constants import DeleteCode
from core.utils import admin_register
from . import constants

### Enum类型映射
COURT_TYPE_CHOICES = [
    ('ymq', '羽毛球'),
    ('wq', '网球'),
    ('lq', '篮球'),
    ('zq', '足球'),
    ('ppq', '乒乓球'),
    ('bswq', '壁球'),
    ('pkq', '皮克球'),
]

LANGUAGE_TYPE_CHOICES = [
    ('zh_CN', '简体中文'),
    ('zh_TW', '繁体中文'),
    ('en_US', '英语'),
    ('ko_KR', '韩语'),
    ('th_TH', '泰语'),
    ('ja_JP', '日语'),
]

ROLE_TYPE = [
    ('normal', '普通选手'),
    ('seed', '种子选手'),
    ('coach', '教练'),
]

# 不用外键的方案

### 1. 用户信息
from wechat.models import User

@admin_register(addable=False, changeable=False, list_display=['name','city','create_time','membership','mobilephone',], list_filter=['mobilephone', ])
class Player(User):

    county = models.IntegerField(verbose_name='区/县',blank=True, null=True)
    nearby = models.CharField(verbose_name='住哪里',max_length=255, blank=True, null=True)
    membership = models.CharField(verbose_name='是否是会员',max_length=1, blank=True, null=True)
    create_time = models.DateTimeField(verbose_name='创建时间',blank=True, null=True)
    modify_time = models.DateTimeField(verbose_name='修改时间',blank=True, null=True)
    
    def __str__(self):
        return self.name or self.nickname or str(self.id)

    class Meta:
        verbose_name = verbose_name_plural = "用户"


### 2. 地点
@admin.register(addable=True, changeable=True, list_display=['placeid','name','province','city','county','address','descripiton',], list_filter=['province','city','county', ])
class Place(utils.BaseModel):
    placeid = models.IntegerField(verbose_name='',blank=True, null=True)
    name = models.CharField(verbose_name='名称',max_length=255, blank=True, null=True)
    province = models.IntegerField(verbose_name='省份',blank=True, null=True)
    city = models.IntegerField(verbose_name='城市',blank=True, null=True)
    county = models.IntegerField(verbose_name='区/县',blank=True, null=True)
    address = models.CharField(verbose_name='地址',max_length=255, blank=True, null=True)
    descripiton = models.CharField(verbose_name='更多信息',max_length=255, blank=True, null=True)
    tenantid = models.IntegerField(verbose_name='租户',blank=True, null=True)#是否具有独占权限？又要考虑其他租户能使用
    create_time = models.DateTimeField(verbose_name='创建时间',blank=True, null=True)

    def __str__(self):
        return self.name or str(self.id)
    
    class Meta:
        verbose_name = verbose_name_plural = "地点"


### 3. 场地
@admin.register
class Court(utils.BaseModel):
    # id = models.AutoField(primary_key=True)
    placeid = models.IntegerField(blank=True, null=True)
    name = models.CharField(verbose_name='场地名称',max_length=50)
    type = models.CharField(verbose_name='场地类型',max_length=50, choices=COURT_TYPE_CHOICES)
    num = models.SmallIntegerField(verbose_name='场地编号',blank=False, null=False)
    description = models.CharField(verbose_name='场地更多信息',max_length=10, blank=True, null=True)
    tenantid = models.IntegerField(verbose_name='租户',blank=True, null=True)

    def __str__(self):
        return self.name or str(self.name)

    class Meta:
        verbose_name = verbose_name_plural = "场地信息"

### 4. 约球活动模板

@admin.register
class GameTemplate(utils.BaseModel):
    id = models.AutoField(primary_key=True)
    templateid = models.IntegerField(blank=True, null=True)
    shortname = models.CharField(verbose_name='模板助记名',max_length=255, blank=True, null=True)
    title = models.CharField(verbose_name='模板标题',max_length=255, blank=True, null=True)
    description = models.CharField(verbose_name='更多信息',max_length=255, blank=True, null=True)
    # startdate = models.DateField(verbose_name='开始日期',default=today,blank=True, null=True)
    # enddate = models.DateField(verbose_name='角色',blank=True, null=True)
    # starttime = models.CharField(verbose_name='开始时间',max_length=255, blank=True, null=True)
    # endtime = models.CharField(verbose_name='结束时间',max_length=255, blank=True, null=True)
    place = models.IntegerField(verbose_name='地点',blank=True, null=True)
    court = models.IntegerField(verbose_name='场地',blank=True, null=True)
    rule = models.CharField(verbose_name='规则',max_length=255, blank=True, null=True)
    owner = models.IntegerField(verbose_name='模板创建人',blank=True, null=True)

    def __str__(self):
        return self.title or str(self.id)

    class Meta:
        verbose_name = verbose_name_plural = "活动模板"


### 5. 约球活动
@admin_register(addable=True, changeable=True, list_display=['gameid', 'title','description','startdate','enddate'], list_filter=['startdate', ])
class Game(utils.BaseModel):
    id = models.AutoField(primary_key=True)
    gameid = models.IntegerField(verbose_name='活动id',unique=True)
    title = models.CharField(verbose_name='活动短标题',max_length=25, blank=True, null=True)
    description = models.CharField(verbose_name='活动描述',max_length=255, blank=True, null=True)
    startdate = models.DateField(verbose_name='开始日期',blank=False, null=True)
    enddate = models.DateField(verbose_name='结束日期',blank=True, null=True)
    starttime = models.CharField(verbose_name='开始时间',max_length=255, blank=True, null=True)
    endtime = models.CharField(verbose_name='结束时间',max_length=255, blank=True, null=True)
    place = models.IntegerField(verbose_name='地点',blank=True, null=True)
    court = models.SmallIntegerField(verbose_name='场地编号',blank=True, null=True)
    rule = models.CharField(verbose_name='规则描述',max_length=500, blank=True, null=True)
    initiator = models.IntegerField(verbose_name='活动发起人',blank=False, null=False) 
    staus = models.CharField(verbose_name='活动状态',max_length=1, blank=True, null=True)

    @property
    def attendees(self):
        return User.objects.filter(
            ballcallattendee__ballcall_id=self.pk, ballcallattendee__delete_status=DeleteCode.NORMAL.code
        )
    
    def __str__(self):
        return self.title #or str(self.id)

    class Meta:
        verbose_name = verbose_name_plural = "约球活动"


### 6. 约球活动参与人
@admin.register
class GameAttendee(utils.BaseModel):
    game = models.IntegerField(blank=True, null=True)
    attendee = models.IntegerField(verbose_name='参与人',blank=True, null=True)
    status = models.CharField(verbose_name='状态',max_length=1, blank=True, null=True)
    role = models.CharField(verbose_name='角色',max_length=1, blank=True, null=True)

    def __str__(self):
        return str(self.id)
    
    class Meta:
        unique_together = ('attendee', 'game')
        verbose_name = verbose_name_plural = "活动参加人员"


### 7. 用户关注的活动
class UserFollowGame(utils.BaseModel):
    # id = models.AutoField(primary_key=True)
    player = models.IntegerField(blank=True, null=True)
    game = models.IntegerField(blank=True, null=True)

    # 不用外键
    # user = utils.ForeignKey(Player, verbose_name='关注人', editable=False)
    # game = utils.ForeignKey(Game, verbose_name='活动', related_name='followGames', editable=False)

    # def __str__(self):
    #     return str(self.id)
    
    class Meta:
        unique_together = ('player', 'game')
        verbose_name = verbose_name_plural = "用户关注活动"
    

### 8. 用户关注用户
class UserFollowUser(utils.BaseModel):
    follower = models.IntegerField(blank=True, null=True) # 关注者
    followee = models.IntegerField(blank=True, null=True) # 被关注者
    class Meta:
        unique_together = ('follower', 'followee')
        verbose_name = verbose_name_plural = "用户关注用户"


### 9. 用户关注地点
@admin.register
class UserFollowPlace(utils.BaseModel):
    player = models.IntegerField(verbose_name='玩家',blank=True, null=True)
    place = models.IntegerField(verbose_name='地点',blank=True, null=True)
    class Meta:
        verbose_name = verbose_name_plural = "用户关注地点"


### 10. 用户活动跟踪
@admin_register(addable=False, changeable=False, list_display=['meeting', 'user'], list_filter=['owner', 'type'])
class GameTrace(utils.BaseModel):
    game = models.IntegerField(verbose_name='活动',blank=True, null=True)
    player = utils.ForeignKey(User, verbose_name='操作人')
    owner = models.BooleanField(verbose_name='是否发起人自己操作')
    type = models.IntegerField(verbose_name='操作类型', choices=constants.meetingTraceTypeCode.get_choices_list())
    data = models.CharField(verbose_name='详细信息', max_length=4096, default='')
    
    class Meta:
        verbose_name = verbose_name_plural = "活动跟踪"


### 11. 租户模型 用于将用户升级为租户(或者租户的下属员工)；租户客户创建地点，场地

@admin.register
class Tenant(utils.BaseModel):
    id = models.AutoField(primary_key=True)
    tenantid = models.IntegerField(blank=True, null=True)
    tenantname = models.CharField(verbose_name='商家名称',max_length=255, blank=True, null=True)
    description = models.CharField(verbose_name='更多信息',max_length=255, blank=True, null=True)

    def __str__(self):
        return self.tenantname or str(self.id)

    class Meta:
        verbose_name = verbose_name_plural = "商家"


### 12. 系统设置

@admin.register
class Setting(utils.BaseModel):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    value = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name or str(self.id)

    class Meta:
        verbose_name = verbose_name_plural = "设置"


### 13. 支付模型

@admin.register
class PayRecord(utils.BaseModel):
    id = models.AutoField(primary_key=True)

    def __str__(self):
        return str(self.id)
    
    class Meta:
        verbose_name = verbose_name_plural = "支付记录"


### 14. 分级模型

@admin.register
class Grade(utils.BaseModel):
    id = models.AutoField(primary_key=True)
    estimator = models.IntegerField(verbose_name='评价人',blank=True, null=True)
    player = models.IntegerField(verbose_name='被评价人',blank=True, null=True)
    grade = models.DecimalField(verbose_name='等级',max_digits=5, decimal_places=2, blank=True, null=True)
    balltype = models.CharField(verbose_name='球类',max_length=10, choices=COURT_TYPE_CHOICES)

    def __str__(self):
        return str(self.id)


### 15. 标签模型

@admin.register
class Lable(utils.BaseModel):
    id = models.AutoField(primary_key=True)
    target = models.IntegerField(verbose_name='标签目的',blank=True, null=True)
    lablecontent = models.CharField(verbose_name='标签内容',max_length=255, blank=True, null=True)

    def __str__(self):
        return str(self.id)
    
    class Meta:
        verbose_name = verbose_name_plural = "标签"


### 16. 工单模型
@admin.register
class WorkOrder(utils.BaseModel):
    id = models.AutoField(primary_key=True)
    initiator = models.IntegerField(verbose_name='反馈发起人',blank=True, null=True)
    title = models.CharField(verbose_name='标题',max_length=255, blank=True, null=True)
    description = models.CharField(verbose_name='反馈详情',max_length=255, blank=True, null=True)
    createtime = models.TimeField(verbose_name='创建时间',blank=True, null=True)
    lastedittime = models.TimeField(verbose_name='修改时间',blank=True, null=True)
    comment = models.CharField(verbose_name='评价',max_length=255, blank=True, null=True)

    def __str__(self):
        return self.title or str(self.id)
    
    class Meta:
        verbose_name = verbose_name_plural = "我有话说"


### 17. 比赛信息
@admin.register
class MatchInfo(utils.BaseModel):
    id = models.AutoField(primary_key=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = verbose_name_plural = "比赛信息"