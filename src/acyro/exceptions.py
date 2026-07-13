"""Acyro exceptions."""


class CycleError(Exception):
    """Raised when a task graph contains a cycle."""


class UnknownDependencyError(Exception):
    """Raised when a task depends on an unregistered task."""


class InputNotFoundError(Exception):
    """Raised when a declared task input cannot be found."""


class OutputNotFoundError(Exception):
    """Raised when a task does not create a declared output."""
