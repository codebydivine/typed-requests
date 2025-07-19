"""Requests Package - A type-safe HTTP client library."""

from .core import NetworkingManager, TypedResponse, networking_manager

__all__ = ["NetworkingManager", "TypedResponse", "networking_manager"]
