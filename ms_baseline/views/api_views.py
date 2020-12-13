"""API responses for ms_baseline."""
import json
import logging

import cattr
from django.contrib.auth.decorators import login_required
from django.db import DatabaseError
from django.utils.crypto import constant_time_compare
from django.utils.translation import gettext as _
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ms_baseline.api_extra_models import GenericResponse, UserProfileEditRequest, UserRegisterRequest
from ms_baseline.api_utils import asdict_drf_response, asdict_json_response
from ms_baseline.models import MsUser, Store

logger = logging.getLogger("ms_baseline.views.api_views")


@api_view()
def list_stores(request):
    """Return a list of stores that are not hidden."""
    stores_data = Store.objects.filter(hidden=False).values("id", "name", "address", "city", "region_code")
    return Response(list(stores_data))


@api_view(["POST"])
@login_required
def set_default_store(request):
    """Set the user’s default store."""
    try:
        request.user.default_store_id = int(request.POST["store"])
        request.user.save()
        return asdict_drf_response(GenericResponse(success=True, message=_("Your store has been changed!")))
    except Exception as e:
        logger.exception(f"Failed to set store {request.POST['store']} for {request.user}", e)
        return asdict_drf_response(GenericResponse(success=False, message=_("Failed to set store!")))


@api_view()
def whoami(request):
    """Identify the logged-in user."""
    if request.user.is_authenticated:
        obj = {"logged_in": True}
        obj.update(request.user.get_profile())
    else:
        obj = {"logged_in": False}
    return Response(obj)


@api_view(["POST"])
def register(request):
    """Register a new user account."""
    data: dict = json.loads(request.body.decode("utf-8"))
    req: UserRegisterRequest = cattr.structure(data, UserRegisterRequest)
    if not constant_time_compare(req.password, req.repeat_password):
        return asdict_json_response(GenericResponse(success=False, message=_("Passwords do not match.")), 400)
    user = MsUser(
        email=req.email, first_name=req.first_name, last_name=req.last_name, default_store_id=req.default_store_id
    )
    user.set_password(req.password)
    try:
        user.save()
        return asdict_json_response(GenericResponse(success=True, message=_("Registration was successful!")))
    except DatabaseError:
        if MsUser.objects.filter(email=req.email):
            return asdict_json_response(
                GenericResponse(success=False, message=_("An account with this e-mail address already exists.")),
                400,
            )

        logger.exception("Failed to register a user account!")
        return asdict_drf_response(GenericResponse(success=False, message=_("Failed to create an account.")), 500)


@api_view(["GET", "POST"])
@login_required
def profile(request):
    """Get or edit the user’s profile."""
    if request.method == "GET":
        return Response(request.user.get_profile())
    data: dict = json.loads(request.body.decode("utf-8"))
    req: UserProfileEditRequest = cattr.structure(data, UserProfileEditRequest)
    request.user.first_name = req.first_name
    request.user.last_name = req.last_name
    request.user.default_store_id = req.default_store_id
    if req.old_password and req.new_password and req.repeat_password and request.user.check_password(req.old_password):
        if not constant_time_compare(req.new_password, req.repeat_password):
            return asdict_drf_response(GenericResponse(success=False, message=_("Passwords do not match.")), 400)
        else:
            request.user.set_password(req.new_password)

    request.user.save()
    return asdict_drf_response(GenericResponse(success=True, message=_("Your data has been changed!")))
