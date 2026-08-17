# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: AGPL-3.0-only
"""Local shop-floor FastAPI application."""

from .app import create_app

__all__ = ["create_app"]
