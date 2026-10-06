from django.conf import settings
from django.contrib import admin
from django.http import FileResponse, Http404
from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from board.views import SessionViewSet, remove_session, verify_session

router = DefaultRouter()
router.register("sessions", SessionViewSet, basename="session")



def spa(request, path=""):
    """Serve the built React app for any non-API route (production only)."""
    index = settings.FRONTEND_DIST / "index.html"
    if not index.exists():
        raise Http404("Frontend not built. In development use the Vite server.")
    return FileResponse(open(index, "rb"), content_type="text/html")


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("verify/<uuid:token>/", verify_session, name="verify"),
    path("remove/<uuid:token>/", remove_session, name="remove"),
    re_path(r"^(?!api/|admin/|static/|verify/|remove/).*$", spa, name="spa"),
]
