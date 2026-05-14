"""Core module for database, logging, and utilities."""

from .database import Database
from .logger import setup_logger, log
from .embeds import create_embed, create_error_embed, create_success_embed
from .helpers import format_number, get_rarity_color, generate_card_id

__all__ = [
    "Database",
    "setup_logger",
    "log",
    "create_embed",
    "create_error_embed",
    "create_success_embed",
    "format_number",
    "get_rarity_color",
    "generate_card_id",
]
