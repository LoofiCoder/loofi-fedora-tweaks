"""Package-related daemon handlers."""

from __future__ import annotations

from core.executor.action_result import ActionResult

from services.package.service import get_package_service
from daemon.validators import validate_package_list, validate_package_name, validate_search_limit, validate_search_query


class PackageHandler:
    """Serve package operations for IPC callers."""

    @staticmethod
    def install(packages: list[str]) -> dict:
        service = get_package_service()
        clean = validate_package_list(packages)
        if hasattr(service, "install_local"):
            result = service.install_local(clean)
        else:
            result = service.install(clean)
        return PackageHandler._serialize_result(result)

    @staticmethod
    def remove(packages: list[str]) -> dict:
        service = get_package_service()
        clean = validate_package_list(packages)
        if hasattr(service, "remove_local"):
            result = service.remove_local(clean)
        else:
            result = service.remove(clean)
        return PackageHandler._serialize_result(result)

    @staticmethod
    def update(packages: list[str] | None = None) -> dict:
        service = get_package_service()
        cleaned = validate_package_list(packages) if packages is not None else []
        if hasattr(service, "update_local"):
            result = service.update_local(cleaned or None)
        else:
            result = service.update(cleaned or None)
        return PackageHandler._serialize_result(result)

    @staticmethod
    def search(query: str, limit: int = 50) -> dict:
        service = get_package_service()
        clean_query = validate_search_query(query)
        valid_limit = validate_search_limit(limit)
        if hasattr(service, "search_local"):
            result = service.search_local(clean_query, limit=valid_limit)
        else:
            result = service.search(clean_query, limit=valid_limit)
        return PackageHandler._serialize_result(result)

    @staticmethod
    def info(package: str) -> dict:
        service = get_package_service()
        clean_package = validate_package_name(package)
        if hasattr(service, "info_local"):
            result = service.info_local(clean_package)
        else:
            result = service.info(clean_package)
        return PackageHandler._serialize_result(result)

    @staticmethod
    def list_installed() -> dict:
        service = get_package_service()
        if hasattr(service, "list_installed_local"):
            result = service.list_installed_local()
        else:
            result = service.list_installed()
        return PackageHandler._serialize_result(result)

    @staticmethod
    def is_installed(package: str) -> bool:
        service = get_package_service()
        clean_package = validate_package_name(package)
        if hasattr(service, "is_installed_local"):
            return bool(service.is_installed_local(clean_package))
        return bool(service.is_installed(clean_package))

    @staticmethod
    def _serialize_result(result: ActionResult) -> dict:
        if isinstance(result, ActionResult):
            return result.to_dict()
        return ActionResult.fail("Package action returned no result").to_dict()
