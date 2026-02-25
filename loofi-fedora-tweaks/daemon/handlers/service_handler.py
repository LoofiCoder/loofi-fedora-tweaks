"""System and service-related daemon handlers."""

from __future__ import annotations

from core.executor.action_result import ActionResult
from services.system.service import SystemService
from services.system.services import ServiceManager, UnitScope


class ServiceHandler:
    """Serve system and service operations for IPC callers."""

    @staticmethod
    def reboot(description: str = "", delay_seconds: int = 0) -> dict:
        service = SystemService()
        result = service.reboot_local(description=str(description or ""), delay_seconds=int(delay_seconds))
        return ServiceHandler._serialize_action_result(result)

    @staticmethod
    def shutdown(description: str = "", delay_seconds: int = 0) -> dict:
        service = SystemService()
        result = service.shutdown_local(description=str(description or ""), delay_seconds=int(delay_seconds))
        return ServiceHandler._serialize_action_result(result)

    @staticmethod
    def suspend(description: str = "") -> dict:
        service = SystemService()
        result = service.suspend_local(description=str(description or ""))
        return ServiceHandler._serialize_action_result(result)

    @staticmethod
    def update_grub(description: str = "") -> dict:
        service = SystemService()
        result = service.update_grub_local(description=str(description or ""))
        return ServiceHandler._serialize_action_result(result)

    @staticmethod
    def set_hostname(hostname: str, description: str = "") -> dict:
        service = SystemService()
        clean_hostname = str(hostname or "").strip()
        result = service.set_hostname_local(clean_hostname, description=str(description or ""))
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
        parsed_scope = UnitScope.SYSTEM if str(scope or "").strip().lower() == "system" else UnitScope.USER
        units = ServiceManager.list_units(parsed_scope, str(filter_type or "all").strip().lower())
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
        clean_name = str(name or "").strip()
        parsed_scope = UnitScope.SYSTEM if str(scope or "").strip().lower() == "system" else UnitScope.USER
        result = ServiceManager.start_unit(clean_name, parsed_scope)
        return {"success": result.success, "message": result.message}

    @staticmethod
    def stop_unit(name: str, scope: str = "user") -> dict[str, str | bool]:
        clean_name = str(name or "").strip()
        parsed_scope = UnitScope.SYSTEM if str(scope or "").strip().lower() == "system" else UnitScope.USER
        result = ServiceManager.stop_unit(clean_name, parsed_scope)
        return {"success": result.success, "message": result.message}

    @staticmethod
    def restart_unit(name: str, scope: str = "user") -> dict[str, str | bool]:
        clean_name = str(name or "").strip()
        parsed_scope = UnitScope.SYSTEM if str(scope or "").strip().lower() == "system" else UnitScope.USER
        result = ServiceManager.restart_unit(clean_name, parsed_scope)
        return {"success": result.success, "message": result.message}

    @staticmethod
    def _serialize_action_result(result: ActionResult) -> dict:
        if isinstance(result, ActionResult):
            return result.to_dict()
        return ActionResult.fail("Service action returned no result").to_dict()
