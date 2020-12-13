"""General models used for the API."""
import datetime
import typing

import attr


def date_to_string_converter(dt: typing.Union[datetime.datetime, str]) -> str:
    """Convert a date to string (if it isn’t already a string)."""
    if isinstance(dt, datetime.datetime):
        return dt.isoformat()


def enum_get_value(e):
    """Get value from an enum."""
    return e.value


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class UserRegisterRequest:
    """A user registration request."""

    email: str
    password: str
    repeat_password: str
    first_name: str
    last_name: str
    default_store_id: typing.Optional[int]


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class UserProfileEditRequest:
    """A user profile edit request."""

    old_password: str
    new_password: str
    repeat_password: str
    first_name: str
    last_name: str
    default_store_id: typing.Optional[int]


@attr.s(auto_attribs=True, slots=True, kw_only=True)
class GenericResponse:
    """Generic response to an action."""

    success: bool
    message: str = ""
