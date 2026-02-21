"""Backward-compatibility shim. Use core.export.ansible_export instead."""
from core.export.ansible_export import *  # noqa: F401, F403
from core.export.ansible_export import AnsibleExporter, Result  # noqa: F401
