from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import redirect, render
from django.utils.translation import get_language
from django.utils.translation import gettext as _
from django.views.decorators.http import require_http_methods

from apps.core import selectors as core_selectors

from .services import RateLimitExceeded, submit_contact_inquiry


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
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


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
        context['form_errors'] = {
            field: (errs[0] if isinstance(errs, list) else errs)
            for field, errs in exc.message_dict.items()
        }
        if is_htmx:
            if is_modal_form:
                context.update({
                    'form_prefix': 'modal',
                    'form_root_id': 'contact-modal-form-root',
                })
            else:
                context.update({
                    'form_compact': True,
                })
            return render(request, 'partials/contact_form.html', context, status=400)
        return render(request, 'pages/contacts.html', context, status=400)
    except RateLimitExceeded:
        context['form_errors'] = {
            'non_field': _('Слишком много заявок. Попробуйте позже.'),
        }
        if is_htmx:
            if is_modal_form:
                context.update({
                    'form_prefix': 'modal',
                    'form_root_id': 'contact-modal-form-root',
                })
            else:
                context.update({
                    'form_compact': True,
                })
            return render(request, 'partials/contact_form.html', context, status=429)
        return render(request, 'pages/contacts.html', context, status=429)

    if is_htmx:
        return render(request, 'partials/contact_success.html')

    messages.success(request, _('Заявка отправлена. Мы свяжемся с вами.'))
    return redirect('contacts')
