"""Acyro exceptions."""


class CycleError(Exception):
    """Raised when a task graph contains a cycle."""


class UnknownDependencyError(Exception):
    """Raised when a task depends on an unregistered task."""
