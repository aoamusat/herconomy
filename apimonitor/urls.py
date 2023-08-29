from apimonitor.views import IndexView, TransactionView
from django.urls import path

urlpatterns = [
    path("", IndexView.as_view(), name="api.index"),
    path("transaction/", TransactionView.as_view()),
]
