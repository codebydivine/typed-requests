"""
Validation utilities for requests.

This module provides a bridge to the external divine-type-enforcer package
for type validation and enforcement.
"""

from type_enforcer import ValidationError, enforce

# Alias for backward compatibility
validate = enforce

__all__ = ["ValidationError", "validate", "enforce"]