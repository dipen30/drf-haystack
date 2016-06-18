# -*- coding: utf-8 -*-

from __future__ import absolute_import, unicode_literals

from rest_framework.decorators import detail_route, list_route
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ViewSetMixin

from .generics import HaystackGenericAPIView


class HaystackViewSet(RetrieveModelMixin, ListModelMixin, ViewSetMixin, HaystackGenericAPIView):
    """
    The HaystackViewSet class provides the default ``list()`` and
    ``retrieve()`` actions with a haystack index as it's data source.
    """

    @detail_route(methods=["get"], url_path="more-like-this")
    def more_like_this(self, request, pk=None):
        """
        Sets up a detail route for ``more-like-this`` results.
        Note that you'll need backend support in order to take advantage of this.

        This will add ie. ^search/{pk}/more-like-this/$ to your existing ^search pattern.
        """
        obj = self.get_object().object
        queryset = self.filter_queryset(self.get_queryset()).more_like_this(obj)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @list_route(methods=["get"], url_path="facets")
    def facets(self, request):
        """
        Sets up a list route for ``faceted`` results.

        This will add ie ^search/facets/$ to your existing ^search pattern.
        """
        queryset = self.filter_facet_queryset(self.get_queryset())

        for facet in request.query_params.getlist("selected_facets"):

            if ":" not in facet:
                continue

            field, value = facet.split(":", 1)
            if value:
                queryset = queryset.narrow('%s:"%s"' % (field, queryset.query.clean(value)))

        serializer = self.get_facet_serializer(queryset.facet_counts(), objects=queryset, many=False)
        return Response(serializer.data)
