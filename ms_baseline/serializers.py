"""REST serializers for ms_baseline."""
import codecs
import decimal
import json
import typing

import rest_framework.exceptions
import rest_framework.parsers
from rest_framework import serializers

from ms_baseline import models
from ms_baseline.utils import get_visited_store_id


class SimpleUserSerializer(serializers.ModelSerializer):
    """A simple user serializer."""

    full_name = serializers.SerializerMethodField()

    def get_full_name(self, instance):
        """Get the user’s full name."""
        return instance.get_full_name()

    class Meta:
        model = models.MsUser
        fields = ["id", "email", "first_name", "last_name", "full_name"]


def get_serializer_context(
    *, context: typing.Optional[typing.Mapping[str, typing.Any]] = None, request=None
) -> typing.Mapping[str, typing.Any]:
    """Get the DRF serializer context."""
    if context is None and request is None:
        raise ValueError("get_serializer_context requires either context or request.")
    if context is None:
        context = {"request": request}
    context["store_id"] = get_visited_store_id(context["request"])
    return context


class SerializerContextMixin:
    """A mixin with the serializer context."""

    def get_serializer_context(self):
        """Get the serializer context."""
        # noinspection PyUnresolvedReferences
        context = super().get_serializer_context()
        return get_serializer_context(context=context)


class JSONDecimalParser(rest_framework.parsers.JSONParser):
    """A JSON parser that reads all floats as decimal.Decimal."""

    def parse(self, stream, media_type=None, parser_context=None):
        """Parse the incoming bytestream as JSON and return the resulting data."""
        parser_context = parser_context or {}
        encoding = parser_context.get("encoding", "utf-8")

        try:
            decoded_stream = codecs.getreader(encoding)(stream)
            return json.load(decoded_stream, parse_float=decimal.Decimal)
        except ValueError as exc:
            raise rest_framework.exceptions.ParseError("JSON parse error - %s" % str(exc))
