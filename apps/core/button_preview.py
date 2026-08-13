"""Staff-only unsaved button-style preview (session + query, never persisted)."""

from __future__ import annotations

from django.http import HttpRequest

from .theme_fields import (
    BUTTON_STYLE_DEFAULTS,
    FILL_GRADIENT,
    FILL_SOLID,
    fill_css_background,
    normalize_hex,
    validate_fill_payload,
)

SESSION_KEY = 'button_style_preview'
_ALLOWED_ROLES = frozenset(BUTTON_STYLE_DEFAULTS)
_ALLOWED_FILLS = frozenset({FILL_SOLID, FILL_GRADIENT})


class ButtonStylePreview:
    def __init__(self, payload: dict):
        self.role = payload['role']
        self.fill_type = payload['fill_type']
        self.solid_color = payload.get('solid_color') or ''
        self.gradient_start = payload.get('gradient_start') or ''
        self.gradient_end = payload.get('gradient_end') or ''
        self.gradient_angle = payload.get('gradient_angle')

    def as_css_background(self, fallback: str = '') -> str:
        return fill_css_background(
            fill_type=self.fill_type,
            solid_color=self.solid_color,
            gradient_start=self.gradient_start,
            gradient_end=self.gradient_end,
            gradient_angle=self.gradient_angle,
            fallback=fallback,
        )

    def has_custom_fill(self) -> bool:
        if self.fill_type == FILL_SOLID:
            return bool(self.solid_color)
        return bool(self.gradient_start and self.gradient_end)


def parse_preview_draft(data, *, role: str) -> dict | None:
    role = (role or data.get('role') or '').strip()
    if role not in _ALLOWED_ROLES:
        return None
    fill_type = (data.get('fill_type') or '').strip()
    if fill_type not in _ALLOWED_FILLS:
        return None
    angle_raw = data.get('gradient_angle')
    if angle_raw in (None, ''):
        angle = None
    else:
        try:
            angle = int(angle_raw)
        except (TypeError, ValueError):
            return None
    solid = normalize_hex(data.get('solid_color') or '')
    start = normalize_hex(data.get('gradient_start') or '')
    end = normalize_hex(data.get('gradient_end') or '')
    errors = validate_fill_payload(
        fill_type=fill_type,
        solid_color=solid,
        gradient_start=start,
        gradient_end=end,
        gradient_angle=angle,
        require_complete=True,
    )
    if errors:
        return None
    return {
        'role': role,
        'fill_type': fill_type,
        'solid_color': solid,
        'gradient_start': start,
        'gradient_end': end,
        'gradient_angle': angle,
    }


def resolve_button_preview(request: HttpRequest) -> dict | None:
    user = getattr(request, 'user', None)
    if not user or not user.is_authenticated or not user.is_staff:
        return None
    if request.GET.get('clear_btn_preview') == '1':
        request.session.pop(SESSION_KEY, None)
        return None
    if request.GET.get('btn_preview') == '1':
        draft = parse_preview_draft(request.GET, role=request.GET.get('role', ''))
        if draft:
            request.session[SESSION_KEY] = draft
            return draft
    stored = request.session.get(SESSION_KEY)
    if isinstance(stored, dict) and stored.get('role') in _ALLOWED_ROLES:
        return stored
    return None


def overlay_button_styles(request: HttpRequest, button_styles: dict) -> tuple[dict, dict | None]:
    draft = resolve_button_preview(request)
    if not draft:
        return button_styles, None
    styles = dict(button_styles)
    styles[draft['role']] = ButtonStylePreview(draft)
    return styles, draft
