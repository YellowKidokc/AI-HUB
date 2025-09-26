from __future__ import annotations

import importlib
import pkgutil
from typing import Iterable, List

from .base import HubModule, ModuleAPI


def discover_modules(api: ModuleAPI) -> List[HubModule]:
    modules: List[HubModule] = []
    package = __name__
    for finder, name, ispkg in pkgutil.iter_modules(__path__, f"{package}."):
        if ispkg:
            continue
        module = importlib.import_module(name)
        register = getattr(module, "register", None)
        if register is None:
            continue
        spec = register(api)
        if isinstance(spec, Iterable):
            modules.extend(spec)
        else:
            modules.append(spec)
    return sorted(modules, key=lambda module: module.order)
