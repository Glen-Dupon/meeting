# encoding: utf-8
from __future__ import absolute_import, unicode_literals

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path

from cool.views.websocket import CoolBFFAPIConsumer
# from django.core.asgi import get_asgi_application

# import os,django

# django.setup()

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "meeting.settings")


# from django.core.management import call_command

# 配置 WebSocket 路由

class MeetingConsumer(CoolBFFAPIConsumer):

    def accept(self, subprotocol=None):
        return super().accept('apiview')


def get_app():
    print("======================get app=======================")
    if hasattr(MeetingConsumer, 'as_asgi'):
        return MeetingConsumer.as_asgi()
    else:
        return MeetingConsumer

# 检查Django版本和Channels版本兼容性 ?

application = ProtocolTypeRouter({


    # "http": get_asgi_application(),

    # "websocket": URLRouter(
    #     MeetingConsumer.routing.websocket_urlpatterns
    # ),

    #http路由走这里
    #"http":get_asgi_application()# 也可以不需要此项，普通的HTTP请求不需要我们手动在这里添加，框架会自动加载
    #chat应用下rountings模块下的路由变量socket_urlpatterns
    # "websocket":URLRouter(routings.socket_urlpatterns)

    # https://blog.csdn.net/weixin_44367279/article/details/120222948

    'websocket': AuthMiddlewareStack(
        # 多个url合并一起使用，多个子路由列表相加:a+b ：
        URLRouter(
            [
                # 添加 WebSocket 路由
                path('/wsapi', get_app())
            ],
        ),
    ),
})

# https://blog.csdn.net/weixin_46371752/article/details/130517026
# https://blog.csdn.net/qq_42902997/article/details/131558930
# https://www.jianshu.com/p/ecee6ed92ddd
# https://blog.csdn.net/qq_52385631/article/details/122851430