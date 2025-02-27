# (C) Datadog, Inc. 2024-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)

import pytest

from datadog_checks.dev.utils import get_metadata_metrics
from datadog_checks.mongo import MongoDb

from . import common
from .common import METRIC_VAL_CHECKS

pytestmark = [pytest.mark.usefixtures('dd_environment'), pytest.mark.integration, common.shard]


def test_mongo_arbiter(aggregator, check, instance_arbiter, dd_run_check):
    check = check(instance_arbiter)
    dd_run_check(check)

    tags = [f'host:{common.HOST}', f'port:{common.PORT_ARBITER}', 'db:admin']
    aggregator.assert_service_check('mongodb.can_connect', status=MongoDb.OK, tags=tags)

    metric_names = aggregator.metric_names
    assert metric_names

    for metric_name in metric_names:
        if metric_name in METRIC_VAL_CHECKS:
            metric = aggregator.metrics(metric_name)[0]
            assert METRIC_VAL_CHECKS[metric_name](metric.value)
    aggregator.assert_metrics_using_metadata(get_metadata_metrics(), check_submission_type=True)

    expected_metrics = {
        'mongodb.replset.health': 1.0,
        'mongodb.replset.votefraction': None,
        'mongodb.replset.votes': 1,
        'mongodb.replset.state': 7,
    }
    expected_tags = [
        'server:mongodb://localhost:27020/',
        'replset_name:shard01',
        'replset_state:arbiter',
        'replset_me:shard01c:27020',
        'sharding_cluster_role:shardsvr',
        'hosting_type:self-hosted',
    ] + check.internal_resource_tags
    for metric, value in expected_metrics.items():
        aggregator.assert_metric(metric, value, expected_tags, count=1)


@pytest.mark.flaky
def test_mongo_replset(instance_shard, aggregator, check, dd_run_check):
    mongo_check = check(instance_shard)
    dd_run_check(mongo_check)

    replset_metrics = [
        'mongodb.replset.health',
        'mongodb.replset.replicationlag',
        'mongodb.replset.state',
        'mongodb.replset.votefraction',
        'mongodb.replset.votes',
    ]
    replset_common_tags = [
        "replset_name:shard01",
        "server:mongodb://localhost:27018/",
        "sharding_cluster_role:shardsvr",
        'hosting_type:self-hosted',
    ] + mongo_check.internal_resource_tags
    for metric in replset_metrics:
        aggregator.assert_metric(
            metric, tags=replset_common_tags + ['replset_state:primary', 'replset_me:shard01a:27018']
        )
    aggregator.assert_metric(
        'mongodb.replset.optime_lag',
        tags=replset_common_tags + ['replset_state:primary', 'member:shard01a:27018', 'replset_me:shard01a:27018'],
    )
    aggregator.assert_metric(
        'mongodb.replset.optime_lag',
        tags=replset_common_tags + ['replset_state:secondary', 'member:shard01b:27019', 'replset_me:shard01a:27018'],
    )
    aggregator.assert_metrics_using_metadata(get_metadata_metrics(), check_submission_type=True)
