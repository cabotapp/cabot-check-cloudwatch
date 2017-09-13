from datetime import datetime
from os import environ as env

import boto3

from cabot.cabotapp.models import StatusCheck
from cabot.cabotapp.views import (CheckCreateView, CheckUpdateView,
                                  StatusCheckForm, base_widgets)
from dal import autocomplete
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from .helpers import get_boto_client
from .models import CloudwatchConfig, CloudwatchStatusCheck


class CloudwatchStatusCheckForm(StatusCheckForm):
    symmetrical_fields = ('service_set', 'instance_set')

    dimensions = forms.CharField(
        help_text='Dimensions',
        widget=autocomplete.Select2Multiple(
            url='cloudwatch-dimension-autocomplete',
            forward=['cloudwatch_config', 'cloudwatch_metric'],
        ),
    )

    class Meta:
        model = CloudwatchStatusCheck
        fields = (
            'name',
            'cloudwatch_config',
            'cloudwatch_metric',
            'dimensions',
            'statistic',
            'check_type',
            'value',
            'frequency',
            'active',
            'importance',
            'debounce',
        )

        widgets = dict(**base_widgets)
        widgets.update({
            'value': forms.TextInput(attrs={
                'style': 'width: 100px',
                'placeholder': 'threshold value',
            }),
            'cloudwatch_metric': autocomplete.ListSelect2(
                url='cloudwatch-metric-autocomplete',
                forward=['cloudwatch_config'],
                attrs={
                    'style': 'width: 100%',
                }
            ),
            'check_type': forms.Select(attrs={
                'data-rel': 'chosen',
            }),
            'check_type': forms.Select(attrs={
                'data-rel': 'chosen',
            })
        })


class CloudwatchCheckCreateView(CheckCreateView):
    model = CloudwatchStatusCheck
    form_class = CloudwatchStatusCheckForm


class CloudwatchCheckUpdateView(CheckUpdateView):
    model = CloudwatchStatusCheck
    form_class = CloudwatchStatusCheckForm

def duplicate_check(request, pk):
    pc = StatusCheck.objects.get(pk=pk)
    npk = pc.duplicate()
    return HttpResponseRedirect(reverse('update-cloudwatch-check', kwargs={'pk': npk}))


class MetricAutocomplete(LoginRequiredMixin, autocomplete.Select2ListView):
    def get_list(self):
        result = []
        client = get_boto_client(CloudwatchConfig.objects.get(pk=self.forwarded['cloudwatch_config']))
        metrics = client.list_metrics()['Metrics']

        for metric in metrics:
            metric_string = "{}:{}".format(metric['Namespace'], metric['MetricName'])
            if self.q.lower() in metric_string.lower():
                result.append(metric_string)

        return sorted(set(result))

class DimensionAutocomplete(LoginRequiredMixin, autocomplete.Select2ListView):
    def get_list(self):
        result = []
        client = get_boto_client(CloudwatchConfig.objects.get(pk=self.forwarded['cloudwatch_config']))
        namespace, metric_name = self.forwarded['cloudwatch_metric'].split(':')
        metrics = client.list_metrics(
            Namespace=namespace,
            MetricName=metric_name)['Metrics']

        for metric in metrics:
            dimensions = metric['Dimensions']
            for dimension in dimensions:
                dimension_string = "{}={}".format(dimension['Name'], dimension['Value'])
                if self.q.lower() in dimension_string.lower():
                    result.append(dimension_string)

        # resp = client.get_metric_statistics(Namespace=namespace,MetricName=metric_name,Dimensions=dimensions,StartTime=start_time,EndTime=end_time,Period=60,Statistics=['SampleCount','Average','Sum','Minimum','Maximum',],)

        return sorted(set(result))
