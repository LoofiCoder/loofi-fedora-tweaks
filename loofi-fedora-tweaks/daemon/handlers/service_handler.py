"""System and service-related daemon handlers."""

from __future__ import annotations

from core.executor.action_result import ActionResult
from services.system.service import SystemService
from services.system.services import ServiceManager, UnitScope
from daemon.validators import (
    validate_delay_seconds,
    validate_description,
    validate_hostname,
    validate_unit_filter,
    validate_unit_name,
    validate_unit_scope,
)


class ServiceHandler:
    """Serve system and service operations for IPC callers."""

    @staticmethod
    def reboot(description: str = "", delay_seconds: int = 0) -> dict:
        service = SystemService()
        valid_description = validate_description(description)
        valid_delay_seconds = validate_delay_seconds(delay_seconds)
        result = service.reboot_local(description=valid_description, delay_seconds=valid_delay_seconds)
        return ServiceHandler._serialize_action_result(result)

    @staticmethod
    def shutdown(description: str = "", delay_seconds: int = 0) -> dict:
        service = SystemService()
        valid_description = validate_description(description)
        valid_delay_seconds = validate_delay_seconds(delay_seconds)
        result = service.shutdown_local(description=valid_description, delay_seconds=valid_delay_seconds)
        return ServiceHandler._serialize_action_result(result)

    @staticmethod
    def suspend(description: str = "") -> dict:
        service = SystemService()
        valid_description = validate_description(description)
        result = service.suspend_local(description=valid_description)
        return ServiceHandler._serialize_action_result(result)

    @staticmethod
    def update_grub(description: str = "") -> dict:
        service = SystemService()
        valid_description = validate_description(description)
        result = service.update_grub_local(description=valid_description)
        return ServiceHandler._serialize_action_result(result)

    @staticmethod
    def set_hostname(hostname: str, description: str = "") -> dict:
        service = SystemService()
        valid_hostname = validate_hostname(hostname)
        valid_description = validate_description(description)
        result = service.set_hostname_local(valid_hostname, description=valid_description)
        return ServiceHandler._serialize_action_result(result)

    @staticmethod
    def has_pending_reboot() -> bool:
        return bool(SystemService.has_pending_reboot())

    @staticmethod
    def get_package_manager() -> str:
        return str(SystemService.get_package_manager())

    @staticmethod
    def get_variant_name() -> str:
        return str(SystemService.get_variant_name())

    @staticmethod
    def list_units(scope: str = "user", filter_type: str = "all") -> list[dict[str, str | bool]]:
        valid_scope = validate_unit_scope(scope)
        valid_filter_type = validate_unit_filter(filter_type)
        parsed_scope = UnitScope.SYSTEM if valid_scope == "system" else UnitScope.USER
        units = ServiceManager.list_units(parsed_scope, valid_filter_type)
        return [
            {
                "name": unit.name,
                "state": unit.state.value,
                "scope": unit.scope.value,
                "description": unit.description,
                "is_gaming": unit.is_gaming,
            }
            for unit in units
        ]

    @staticmethod
    def start_unit(name: str, scope: str = "user") -> dict[str, str | bool]:
        valid_name = validate_unit_name(name)
        valid_scope = validate_unit_scope(scope)
        parsed_scope = UnitScope.SYSTEM if valid_scope == "system" else UnitScope.USER
        result = ServiceManager.start_unit(valid_name, parsed_scope)
        return {"success": result.success, "message": result.message}

    @staticmethod
    def stop_unit(name: str, scope: str = "user") -> dict[str, str | bool]:
        valid_name = validate_unit_name(name)
        valid_scope = validate_unit_scope(scope)
        parsed_scope = UnitScope.SYSTEM if valid_scope == "system" else UnitScope.USER
        result = ServiceManager.stop_unit(valid_name, parsed_scope)
        return {"success": result.success, "message": result.message}

    @staticmethod
    def restart_unit(name: str, scope: str = "user") -> dict[str, str | bool]:
        valid_name = validate_unit_name(name)
        valid_scope = validate_unit_scope(scope)
        parsed_scope = UnitScope.SYSTEM if valid_scope == "system" else UnitScope.USER
        result = ServiceManager.restart_unit(valid_name, parsed_scope)
        return {"success": result.success, "message": result.message}

    @staticmethod
    def _serialize_action_result(result: ActionResult) -> dict:
        if isinstance(result, ActionResult):
            return result.to_dict()
        return ActionResult.fail("Service action returned no result").to_dict()
