"""Utilities for APIs in MobiShopper."""
import collections

import attr
import django.http
import rest_framework.pagination
import rest_framework.response


def asdict_json_response(obj, status=200):
    """Create a JsonResponse, based on an attrs class."""
    return django.http.JsonResponse(attr.asdict(obj), status=status)


def asdict_drf_response(obj, status=200):
    """Create a DRF Response, based on an attrs class."""
    return rest_framework.response.Response(attr.asdict(obj), status=status)


class PageNumberIncludedPagination(rest_framework.pagination.PageNumberPagination):
    """A paginator which includes the page number in its response."""

    def get_paginated_response(self, data):
        """Get a paginated response."""
        return rest_framework.response.Response(
            collections.OrderedDict(
                [
                    ("page", self.page.number),
                    ("count", self.page.paginator.count),
                    ("next", self.get_next_link()),
                    ("previous", self.get_previous_link()),
                    ("results", data),
                ]
            )
        )
