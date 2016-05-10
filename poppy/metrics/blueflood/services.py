# Copyright (c) 2016 Rackspace, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from oslo_context import context as context_utils
from oslo_log import log

from poppy.metrics import base
from poppy.metrics.blueflood.utils import client
from poppy.metrics.blueflood.utils import errors
from poppy.metrics.blueflood.utils import helper

LOG = log.getLogger(__name__)


class ServicesController(base.ServicesController):

    def __init__(self, driver):
        super(ServicesController, self).__init__(driver)

        self.driver = driver

    def _result_formatter(self, response):

        resp_dict = []

        if not response.ok:
            LOG.warning("BlueFlood Metrics Response status Code:{0} "
                        "Response Text: {1} "
                        "Request URL: {2}".format(response.status_code,
                                                  response.text,
                                                  response.url))
            return resp_dict
        else:

            serialized_response = response.json()
            try:
                values = serialized_response['values']
                for val in values:
                    m = {}
                    m['timestamp'] = helper.datetime_from_epoch(
                        int(val['timestamp']))
                    m['count'] = val['sum']
                    resp_dict.append(m)
            except KeyError:
                msg = 'content from {0} not conforming ' \
                      'to API contracts'.format(response.url)
                LOG.warning(msg)
                raise errors.BlueFloodApiSchemaError(msg)

            # sort the resp_dict by timestamp ascending
            resp_dict = sorted(resp_dict, key=lambda x: x['timestamp'])

            return resp_dict

    def read(self, metric_names, from_timestamp, to_timestamp, resolution):
        """read metrics from metrics driver.

        """
        curr_resolution = \
            helper.resolution_converter_seconds_to_enum(resolution)
        context_dict = context_utils.get_current().to_dict()

        project_id = context_dict['tenant']
        auth_token = None
        if self.driver.metrics_conf.use_keystone_auth:
            auth_token = context_dict['auth_token']

        tenanted_blueflood_url = \
            self.driver.metrics_conf.blueflood_url.format(
                project_id=project_id
            )
        from_timestamp = int(helper.datetime_to_epoch(from_timestamp))
        to_timestamp = int(helper.datetime_to_epoch(to_timestamp))
        urls = []
        params = {
            'to': to_timestamp,
            'from': from_timestamp,
            'resolution': curr_resolution
        }
        for metric_name in metric_names:
            tenanted_blueflood_url_with_metric = helper.join_url(
                tenanted_blueflood_url, metric_name.strip().replace(" ", ""))
            LOG.info("Querying BlueFlood Metric: {0}".format(
                tenanted_blueflood_url_with_metric))
            urls.append(helper.set_qs_on_url(
                        tenanted_blueflood_url_with_metric,
                        **params))
        executors = self.driver.metrics_conf.no_of_executors
        blueflood_client = client.BlueFloodMetricsClient(token=auth_token,
                                                         project_id=project_id,
                                                         executors=executors)
        results = blueflood_client.async_requests(urls)
        reordered_metric_names = []
        for result in results:
            metric_name = helper.retrieve_last_relative_url(result.url)
            reordered_metric_names.append(metric_name)

        formatted_results = []
        for metric_name, result in zip(reordered_metric_names, results):
            formatted_result = self._result_formatter(result)
            # NOTE(TheSriram): Tuple to pass the associated metric name, along
            # with the formatted result
            formatted_results.append((metric_name, formatted_result))

        return formatted_results
