from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from apps.core import selectors as core_selectors

from .services import RateLimitExceeded, submit_contact_inquiry


def _flatten_validation_errors(exc: ValidationError) -> dict:
    if getattr(exc, 'error_dict', None):
        return {
            field: (errs[0] if isinstance(errs, list) else errs)
            for field, errs in exc.message_dict.items()
        }
    error_messages = getattr(exc, 'messages', None) or [str(exc)]
    return {'non_field': error_messages[0]}


def _htmx_form_context(is_modal_form: bool) -> dict:
    if is_modal_form:
        return {
            'form_prefix': 'modal',
            'form_root_id': 'contact-modal-form-root',
            'form_compact': True,
        }
    return {'form_compact': True}


def _contact_error_response(request, context, *, is_htmx: bool, is_modal_form: bool, status: int):
    if is_htmx:
        context.update(_htmx_form_context(is_modal_form))
        return render(request, 'partials/contact_form.html', context, status=status)
    return render(request, 'pages/contacts.html', context, status=status)


def _prepare_partner_offers(offers):
    """Structure exact CMS copy for visual lists without rewriting it."""
    for offer in offers:
        intro = []
        label = ''
        points = []
        outro = []
        points_started = False
        for line in (offer.text or '').splitlines():
            line = line.strip()
            if not line:
                continue
            if line.startswith('•'):
                points_started = True
                points.append(line.removeprefix('•').strip())
            elif not points_started and line.endswith(':'):
                label = line
            elif points_started:
                outro.append(line)
            else:
                intro.append(line)
        offer.presentation_intro = intro
        offer.presentation_label = label
        offer.presentation_points = points
        offer.presentation_outro = outro
    return offers


def _client_ip(request) -> str | None:
    # Не довіряємо X-Forwarded-For від клієнта (spoof → bypass rate-limit).
    # Реальний IP має виставляти довірений reverse-proxy у REMOTE_ADDR.
    return request.META.get('REMOTE_ADDR') or None


@require_http_methods(['GET', 'POST'])
def contacts(request):
    blocks = core_selectors.get_blocks('contacts')
    offers = _prepare_partner_offers(list(core_selectors.get_partner_offers()))
    context = {
        'blocks': blocks,
        'offers': offers,
        'form_errors': {},
        'form_data': {},
    }

    if request.method == 'GET':
        return render(request, 'pages/contacts.html', context)

    form_data = {
        'purpose': request.POST.get('purpose', ''),
        'name': request.POST.get('name', ''),
        'phone': request.POST.get('phone', ''),
        'email': request.POST.get('email', ''),
    }
    context['form_data'] = form_data
    is_htmx = request.headers.get('HX-Request') == 'true'
    htmx_target = request.headers.get('HX-Target', '')
    is_modal_form = htmx_target == 'contact-modal-form-root'

    try:
        submit_contact_inquiry(
            purpose=form_data['purpose'],
            name=form_data['name'],
            phone=form_data['phone'],
            email=form_data['email'],
            honeypot=request.POST.get('website', ''),
            ip_address=_client_ip(request),
            language=get_language(),
        )
    except ValidationError as exc:
        context['form_errors'] = _flatten_validation_errors(exc)
        return _contact_error_response(
            request,
            context,
            is_htmx=is_htmx,
            is_modal_form=is_modal_form,
            status=400,
        )
    except RateLimitExceeded:
        context['form_errors'] = {
            'non_field': _('Слишком много заявок. Попробуйте позже.'),
        }
        return _contact_error_response(
            request,
            context,
            is_htmx=is_htmx,
            is_modal_form=is_modal_form,
            status=429,
        )

    if is_htmx:
        return render(request, 'partials/contact_success.html')

    messages.success(request, _('Заявка отправлена. Мы свяжемся с вами.'))
    return redirect('contacts')
