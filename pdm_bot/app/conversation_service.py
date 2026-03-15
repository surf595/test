"""Backward-compatible import path for conversation service."""

from .services.conversation_service import build_assistant_reply

__all__ = ["build_assistant_reply"]
