from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from board.views import SessionViewSet, remove_session, verify_session

router = DefaultRouter()
router.register("sessions", SessionViewSet, basename="session")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("verify/<uuid:token>/", verify_session, name="verify"),
    path("remove/<uuid:token>/", remove_session, name="remove"),
]
