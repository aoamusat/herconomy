from apimonitor.views import IndexView
from django.urls import path

urlpatterns = [
    path("", IndexView.as_view(), name="api.index"),
    # path("transaction/", InboundSMSView.as_view()),
]
