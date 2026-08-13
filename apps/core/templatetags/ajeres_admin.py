"""Admin sidebar helpers (nested Unfold nav)."""

from __future__ import annotations

from django import template

register = template.Library()


def _branch_is_active(items) -> bool:
    if not isinstance(items, list):
        return False
    for item in items:
        if not isinstance(item, dict):
            continue
        if item.get('active'):
            return True
        children = item.get('items')
        if isinstance(children, list) and _branch_is_active(children):
            return True
    return False


@register.simple_tag
def nav_branch_active(items) -> bool:
    return _branch_is_active(items)


@register.filter
def nav_children(item) -> list:
    if not isinstance(item, dict):
        return []
    children = item.get('items')
    if isinstance(children, list):
        return children
    return []
