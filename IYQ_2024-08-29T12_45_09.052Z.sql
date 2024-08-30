CREATE TYPE "courttype" AS ENUM (
	''ymq'',
	''lq'',
	''wq'',
	''zq'',
	''ppq'',
	''bswq'',
	''pkq''
);
CREATE TABLE "player" (
	"id" INTEGER NOT NULL UNIQUE,
	-- 玩家id,长度8位,自动生成,以1000 0001开始
	"playerid" INTEGER NOT NULL,
	-- 用户名称
	"name" VARCHAR,
	-- 昵称
	"nickname" VARCHAR,
	-- 用户的母语
	"language" SMALLINT,
	-- 用户性别
	"gender" CHAR,
	-- 国家
	"country" INTEGER,
	"province" INTEGER,
	-- 城市
	"city" INTEGER,
	-- 区/县
	"county" INTEGER,
	-- 创建时间
	"create_time" TIMESTAMP,
	-- 修改时间
	"modify_time" TIMESTAMP,
	-- 头像URL
	"avatarurl" VARCHAR,
	-- 当前是否是会员0否1付费会员2中级会员3高级会员
	"membership" CHAR,
	-- 离用户最近的标志性地点
	"nearby" POINT,
	-- 移动电话号码
	"mobilephone" INTEGER,
	PRIMARY KEY("id")
);

COMMENT ON TABLE "player" IS '玩家信息表';
COMMENT ON COLUMN player.playerid IS '玩家id,长度8位,自动生成,以1000 0001开始';
COMMENT ON COLUMN player.name IS '用户名称';
COMMENT ON COLUMN player.nickname IS '昵称';
COMMENT ON COLUMN player.language IS '用户的母语';
COMMENT ON COLUMN player.gender IS '用户性别';
COMMENT ON COLUMN player.country IS '国家';
COMMENT ON COLUMN player.city IS '城市';
COMMENT ON COLUMN player.county IS '区/县';
COMMENT ON COLUMN player.create_time IS '创建时间';
COMMENT ON COLUMN player.modify_time IS '修改时间';
COMMENT ON COLUMN player.avatarurl IS '头像URL';
COMMENT ON COLUMN player.membership IS '当前是否是会员0否1付费会员2中级会员3高级会员';
COMMENT ON COLUMN player.nearby IS '离用户最近的标志性地点';
COMMENT ON COLUMN player.mobilephone IS '移动电话号码';


CREATE TABLE "game" (
	"id" INTEGER NOT NULL UNIQUE,
	-- set by github.com/ai/nanoid
	"gameid" INTEGER NOT NULL UNIQUE,
	-- 标题
	"title" VARCHAR,
	-- 描述
	"description" VARCHAR,
	-- 开始日期
	"startdate" DATE,
	-- 结束日期
	"enddate" DATE,
	"starttime" CHAR,
	"endtime" CHAR,
	-- 举办地点
	"place" INTEGER,
	-- 场地编号
	"courtnum" SMALLINT,
	-- 活动那个规则
	"rule" VARCHAR,
	-- 活动发起人
	"initiator" INTEGER,
	-- 活动状态 {0:未开始,1:成约 2:待定 3:未成约 4:发起人取消}
	"staus" CHAR,
	PRIMARY KEY("id", "gameid")
);

COMMENT ON TABLE "game" IS '约球表';
COMMENT ON COLUMN game.gameid IS 'set by github.com/ai/nanoid';
COMMENT ON COLUMN game.title IS '标题';
COMMENT ON COLUMN game.description IS '描述';
COMMENT ON COLUMN game.startdate IS '开始日期';
COMMENT ON COLUMN game.enddate IS '结束日期';
COMMENT ON COLUMN game.place IS '举办地点';
COMMENT ON COLUMN game.courtnum IS '场地编号';
COMMENT ON COLUMN game.rule IS '活动那个规则';
COMMENT ON COLUMN game.initiator IS '活动发起人';
COMMENT ON COLUMN game.staus IS '活动状态 {0:未开始,1:成约 2:待定 3:未成约 4:发起人取消}';


CREATE TABLE "place" (
	"id" INTEGER NOT NULL UNIQUE,
	-- 场地id
	"placeid" INTEGER,
	-- 地址名称
	"name" VARCHAR,
	-- 地址
	"address" VARCHAR,
	-- 场地描述
	"descripiton" VARCHAR,
	-- 租户id
	"tenantid" INTEGER,
	PRIMARY KEY("id")
);
COMMENT ON COLUMN place.placeid IS '场地id';
COMMENT ON COLUMN place.name IS '地址名称';
COMMENT ON COLUMN place.address IS '地址';
COMMENT ON COLUMN place.descripiton IS '场地描述';
COMMENT ON COLUMN place.tenantid IS '租户id';


CREATE TABLE "court" (
	"id" INTEGER NOT NULL UNIQUE,
	"placeid" INTEGER,
	"name" COURTTYPE,
	-- {'ymq','lq','wq','zq','ppq','bswq','pkq'}
	"type" COURTTYPE,
	-- 场地编号：比如1号场，2号场
	"num" SMALLINT,
	"description" COURTTYPE,
	-- 租户id
	"tenantid" INTEGER,
	PRIMARY KEY("id")
);
COMMENT ON COLUMN court.type IS '{'ymq','lq','wq','zq','ppq','bswq','pkq'}';
COMMENT ON COLUMN court.num IS '场地编号：比如1号场，2号场';
COMMENT ON COLUMN court.tenantid IS '租户id';


CREATE TABLE "matchinfo" (
	"id" INTEGER NOT NULL UNIQUE,
	PRIMARY KEY("id")
);


CREATE TABLE "gameattendee" (
	"id" INTEGER NOT NULL UNIQUE,
	-- 约球活动id
	"gameid" INTEGER,
	-- 参与者
	"attendee" INTEGER,
	-- 参与状态0:用户取消 1:正常  2:发起者取消 3:管理员取消 
	"status" CHAR,
	-- 角色 如：种子选手
	"role" CHAR,
	PRIMARY KEY("id")
);
COMMENT ON COLUMN gameattendee.gameid IS '约球活动id';
COMMENT ON COLUMN gameattendee.attendee IS '参与者';
COMMENT ON COLUMN gameattendee.status IS '参与状态0:用户取消 1:正常  2:发起者取消 3:管理员取消 ';
COMMENT ON COLUMN gameattendee.role IS '角色 如：种子选手';


CREATE TABLE "UserFollowGame" (
	"id" INTEGER NOT NULL UNIQUE,
	"playerid" INTEGER,
	"gameid" INTEGER,
	PRIMARY KEY("id")
);


CREATE TABLE "GameTrace" (
	"id" INTEGER NOT NULL UNIQUE,
	PRIMARY KEY("id")
);


CREATE TABLE "tenant" (
	"id" INTEGER NOT NULL UNIQUE,
	"tenantid" INTEGER,
	"tenantname" VARCHAR,
	"description" VARCHAR,
	PRIMARY KEY("id")
);


CREATE TABLE "gametemplate" (
	"id" INTEGER NOT NULL UNIQUE,
	"templateid" INTEGER,
	"shortname" VARCHAR,
	"title" VARCHAR,
	"description" VARCHAR,
	"startdate" DATE,
	"enddate" DATE,
	"starttime" CHAR,
	"endtime" CHAR,
	"place" INTEGER,
	"court" INTEGER,
	"rule" VARCHAR,
	"owner" INTEGER,
	PRIMARY KEY("id")
);

COMMENT ON TABLE "gametemplate" IS '约球活动模板';


CREATE TABLE "setting" (
	"id" INTEGER NOT NULL UNIQUE,
	"name" VARCHAR,
	"value" VARCHAR,
	PRIMARY KEY("id")
);

COMMENT ON TABLE "setting" IS '抽成！计算方式根据城市，球类计算.';


CREATE TABLE "UserFollowPlace" (
	"id" INTEGER NOT NULL UNIQUE,
	"playerid" INTEGER,
	"placeid" INTEGER,
	PRIMARY KEY("id")
);


CREATE TABLE "payrecord" (
	"id" INTEGER NOT NULL UNIQUE,
	PRIMARY KEY("id")
);

COMMENT ON TABLE "payrecord" IS '支付记录';


CREATE TABLE "grade" (
	"id" INTEGER NOT NULL UNIQUE,
	-- 评价人
	"estimator" INTEGER,
	-- 被评价人
	"playerid" INTEGER,
	-- 水平等级
	"grade" NUMERIC,
	-- {'ymq','lq','wq','zq','ppq','bswq','pkq'}
	"balltype" COURTTYPE,
	PRIMARY KEY("id")
);

COMMENT ON TABLE "grade" IS 'Grade evaluation';
COMMENT ON COLUMN grade.estimator IS '评价人';
COMMENT ON COLUMN grade.playerid IS '被评价人';
COMMENT ON COLUMN grade.grade IS '水平等级';
COMMENT ON COLUMN grade.balltype IS '{'ymq','lq','wq','zq','ppq','bswq','pkq'}';


CREATE TABLE "lable" (
	"id" INTEGER NOT NULL UNIQUE,
	"target" INTEGER,
	"lablecontent" VARCHAR,
	PRIMARY KEY("id")
);


CREATE TABLE "workorder" (
	"id" INTEGER NOT NULL UNIQUE,
	"initiator" INTEGER,
	"title" VARCHAR,
	"description" VARCHAR,
	"createtime" TIME,
	"lastedittime" TIME,
	"Comment" VARCHAR,
	PRIMARY KEY("id")
);