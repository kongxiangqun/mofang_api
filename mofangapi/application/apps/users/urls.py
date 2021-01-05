from . import views
from application.utils import path


urlpatterns = [
    path("/avatar", views.avatar),
    path("/invite/code", views.invite_code),
    path("/invite/download", views.invite_download),
    path("/alipay/notify", views.notify_response, methods=["POST","GET"]),
]