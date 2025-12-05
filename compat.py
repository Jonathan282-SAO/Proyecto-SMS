"""
Compat shim to provide `pkgutil.get_loader` when missing (Python 3.14+)
This file should be imported before Flask so Flask's internal code that
calls `pkgutil.get_loader` continues to work.
"""
import pkgutil
import importlib.util

if not hasattr(pkgutil, 'get_loader'):
    def _compat_get_loader(name):
        # Avoid calling find_spec on '__main__' (can raise ValueError)
        if name == '__main__':
            return None
        try:
            spec = importlib.util.find_spec(name)
        except (ImportError, ValueError):
            return None
        if spec is None:
            return None
        return spec.loader

    pkgutil.get_loader = _compat_get_loader
