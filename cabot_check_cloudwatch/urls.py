from os import environ as env

from django.conf.urls import url

from .views import (CloudwatchCheckCreateView, CloudwatchCheckUpdateView,
                    duplicate_check, MetricAutocomplete, DimensionAutocomplete)

urlpatterns = [
    url(r'^cloudwatchcheck/create/', view=CloudwatchCheckCreateView.as_view(),
       name='create-cloudwatch-check'),
    url(r'^cloudwatchcheck/update/(?P<pk>\d+)/',
       view=CloudwatchCheckUpdateView.as_view(), name='update-cloudwatch-check'),
    url(r'^cloudwatchcheck/duplicate/(?P<pk>\d+)/',
       view=duplicate_check, name='duplicate-cloudwatch-check'),

    url(
        r'^cloudwatchcheck/metric-autocomplete/$',
        MetricAutocomplete.as_view(),
        name='cloudwatch-metric-autocomplete',
    ),
    url(
        r'^cloudwatchcheck/dimension-autocomplete/$',
        DimensionAutocomplete.as_view(),
        name='cloudwatch-dimension-autocomplete',
    ),

]
