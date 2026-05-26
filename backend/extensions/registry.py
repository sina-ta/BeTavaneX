from importlib import import_module
import os

from fastapi import FastAPI


OPTIONAL_EXTENSIONS = (
    "workforce",
)


def is_extension_enabled(name: str) -> bool:
    value = os.getenv(
        f"BETAVANX_ENABLE_{name.upper()}_EXTENSION",
        "false",
    )
    return value.strip().lower() in {"1", "true", "yes", "on"}


def register_enabled_extension_models() -> None:
    for extension in OPTIONAL_EXTENSIONS:
        if not is_extension_enabled(extension):
            continue

        module = import_module(
            f"backend.extensions.{extension}.models"
        )
        module.register_models()


def include_enabled_extension_routers(app: FastAPI) -> None:
    for extension in OPTIONAL_EXTENSIONS:
        if not is_extension_enabled(extension):
            continue

        module = import_module(
            f"backend.extensions.{extension}.router"
        )
        module.include_router(app)
