"""Contextual declaration, binding and production input errors."""


class DeclarationError(ValueError):
    """A production declaration is malformed."""


class BindingError(ValueError):
    """A supplied instance or reference is incompatible with its profile."""


class ProductionConflictError(RuntimeError):
    """Several declarations claim the same physical obligation."""


class ProductionInputChangedError(RuntimeError):
    """A shared binding generation changed; construct a fresh binding."""


class ProductionExportError(RuntimeError):
    """A requested instruction or export input cannot be consumed."""
