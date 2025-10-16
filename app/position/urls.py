from django.urls import path

from position.views import PositionListView

urlpatterns = [
    path('', PositionListView.as_view(), name='position-list'),
]