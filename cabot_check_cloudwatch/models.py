import ast
from datetime import datetime, timedelta
from os import environ as env

from cabot.cabotapp.models import StatusCheck, StatusCheckResult
from django.contrib import admin
from django.db import models

from .helpers import get_boto_client


class CloudwatchStatusCheck(StatusCheck):
    check_name = 'cloudwatch'
    edit_url_name = 'update-cloudwatch-check'
    duplicate_url_name = 'duplicate-cloudwatch-check'
    icon_class = 'glyphicon-cloud'

    cloudwatch_config = models.ForeignKey('CloudwatchConfig')
    cloudwatch_metric = models.TextField(
        help_text='Full metric name (<Namespace>:<Metric>) for any cloudwatch metric.',
    )
    dimensions = models.CharField(max_length=2000, blank=False)
    statistic = models.CharField(max_length=2000, blank=False, choices=(
        ('SampleCount', 'SampleCount'),
        ('Average', 'Average'),
        ('Sum', 'Sum'),
        ('Minimum', 'Minimum'),
        ('Maximum', 'Maximum'),
    ))

    def parsed_dimensions(self):
        results = []
        try:
            for name, value in [dim.split('=') for dim in ast.literal_eval(self.dimensions)]:
                results.append({
                    "Name": name,
                    "Value": value,
                })
        except SyntaxError:
            pass

        return results

    def _run(self):
        result = StatusCheckResult(status_check=self)

        try:
            client = get_boto_client(self.cloudwatch_config)
        except Exception as e:
            result.succeeded = False
            result.error = u"Couldn't create cloudwatch client: {}".format(e)
            return result
        else:
            namespace, metric_name = self.cloudwatch_metric.split(":")
            start_time = datetime.now() - timedelta(minutes=self.frequency)
            end_time = datetime.now()
            resp = client.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                Dimensions=self.parsed_dimensions(),
                StartTime=start_time,
                EndTime=end_time,
                Period=60,
                Statistics=['SampleCount','Average','Sum','Minimum','Maximum',],
            )

            if len(resp['Datapoints']) == 0:
                result.succeeded = False
                result.error = u"No datapoints"
                return result

            failures = []
            stats = [dp[self.statistic] for dp in resp['Datapoints']]
            for stat in stats:
                failure_value = None
                if self.check_type == '<':
                    if stat < float(self.value):
                        failure_value = stat
                elif self.check_type == '<=':
                    if stat <= float(self.value):
                        failure_value = stat
                elif self.check_type == '>':
                    if stat > float(self.value):
                        failure_value = stat
                elif self.check_type == '>=':
                    if stat >= float(self.value):
                        failure_value = stat
                elif self.check_type == '==':
                    if float(self.value) == stat:
                        failure_value = float(self.value)
                else:
                    raise Exception(u'Check type %s not supported' %
                                    self.check_type)

                if not failure_value is None:
                    failures.append(failure_value)

            if len(failures) > 0:
                result.succeeded = False
                result.error = u"{} {} {}".format(failures, self.check_type, self.value)
                return result

        result.succeeded = True
        return result


class CloudwatchConfig(models.Model):
    name = models.CharField(max_length=30, blank=False)
    aws_access_key_id = models.CharField(max_length=2000, blank=False)
    aws_secret_access_key = models.CharField(max_length=2000, blank=False)
    aws_session_token = models.CharField(max_length=2000, blank=True)
    aws_region = models.CharField(max_length=100, blank=False)

    def __str__(self):
        return self.name


admin.site.register(CloudwatchConfig)
