# (C) Datadog, Inc. 2021-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)

# This file is autogenerated.
# To change this file you should edit assets/configuration/spec.yaml and then run the following commands:
#     ddev -x validate config -s <INTEGRATION_NAME>
#     ddev -x validate models -s <INTEGRATION_NAME>

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator, model_validator
from typing_extensions import Literal

from datadog_checks.base.utils.functions import identity
from datadog_checks.base.utils.models import validation

from . import defaults, validators


class MetricPatterns(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        frozen=True,
    )
    exclude: Optional[tuple[str, ...]] = None
    include: Optional[tuple[str, ...]] = None


class InstanceConfig(BaseModel):
    model_config = ConfigDict(
        validate_default=True,
        arbitrary_types_allowed=True,
        frozen=True,
    )
    allowed_versions: Optional[tuple[str, ...]] = None
    days_critical: Optional[float] = None
    days_warning: Optional[float] = None
    disable_generic_tags: Optional[bool] = None
    empty_default_hostname: Optional[bool] = None
    fetch_intermediate_certs: Optional[bool] = None
    intermediate_cert_refresh_interval: Optional[float] = None
    local_cert_path: Optional[str] = None
    metric_patterns: Optional[MetricPatterns] = None
    min_collection_interval: Optional[float] = None
    name: Optional[str] = None
    port: Optional[int] = None
    seconds_critical: Optional[int] = None
    seconds_warning: Optional[int] = None
    send_cert_duration: Optional[bool] = None
    server: str
    server_hostname: Optional[str] = None
    service: Optional[str] = None
    start_tls: Optional[Literal['postgres', 'mysql']] = None
    tags: Optional[tuple[str, ...]] = None
    timeout: Optional[int] = None
    tls_ca_cert: Optional[str] = None
    tls_cert: Optional[str] = None
    tls_private_key: Optional[str] = None
    tls_private_key_password: Optional[str] = None
    tls_validate_hostname: Optional[bool] = None
    tls_verify: Optional[bool] = None
    transport: Optional[str] = None

    @model_validator(mode='before')
    def _initial_validation(cls, values):
        return validation.core.initialize_config(getattr(validators, 'initialize_instance', identity)(values))

    @field_validator('*', mode='before')
    def _validate(cls, value, info):
        field = cls.model_fields[info.field_name]
        field_name = field.alias or info.field_name
        if field_name in info.context['configured_fields']:
            value = getattr(validators, f'instance_{info.field_name}', identity)(value, field=field)
        else:
            value = getattr(defaults, f'instance_{info.field_name}', lambda: value)()

        return validation.utils.make_immutable(value)

    @model_validator(mode='after')
    def _final_validation(cls, model):
        return validation.core.check_model(getattr(validators, 'check_instance', identity)(model))
