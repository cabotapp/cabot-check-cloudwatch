import ast
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
from django.utils import six

from .helpers import get_boto_client
from .models import CloudwatchConfig, CloudwatchStatusCheck


# Custom widget classes to add current value to options
# Without these the form is wiped when you try to edit
class ListSelect2(autocomplete.ListSelect2):
    def optgroups(self, name, value, *args, **kwargs):
        if len(self.choices) == 0:
            for v in value:
                self.choices.insert(0, (v, v))
        ret = super(ListSelect2, self).optgroups(name, value, *args,**kwargs)
        return ret


class Select2Multiple(autocomplete.Select2Multiple):
    def optgroups(self, name, value, *args, **kwargs):
        value = [ast.literal_eval(v) for v in value][0]
        if len(self.choices) == 0:
            for v in value:
                self.choices.insert(0, (v, v))
        return super(Select2Multiple, self).optgroups(name, value, *args,**kwargs)


class CloudwatchStatusCheckForm(StatusCheckForm):
    symmetrical_fields = ('service_set', 'instance_set')

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
            'cloudwatch_metric': ListSelect2(
                url='cloudwatch-metric-autocomplete',
                forward=['cloudwatch_config'],
                attrs={
                    'style': 'width: 100%',
                }
            ),
            'dimensions': Select2Multiple(
                url='cloudwatch-dimension-autocomplete',
                forward=['cloudwatch_config', 'cloudwatch_metric'],
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
