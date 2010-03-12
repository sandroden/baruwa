#  Based on: http://www.djangosnippets.org/snippets/73/
#
#  Modified by Sean Reifschneider to be smarter about surrounding page
#  link context.  For usage documentation see:
#
#     http://www.tummy.com/Community/Articles/django-pagination/

from django import template

register = template.Library()

def paginator(context, adjacent_pages=2):
    """
    To be used in conjunction with the object_list generic view.

    Adds pagination context variables for use in displaying first, adjacent and
    last page links in addition to those created by the object_list generic
    view.

    """
    startPage = max(context['page'] - adjacent_pages, 1)
    if startPage <= 3: startPage = 1
    endPage = context['page'] + adjacent_pages + 1
    if endPage >= context['pages'] - 1: endPage = context['pages'] + 1
    page_numbers = [n for n in range(startPage, endPage) \
            if n > 0 and n <= context['pages']]
    page_obj = context['page_obj']
    paginator = context['paginator']
    if context.has_key('quarantine'):
        if int(context['quarantine']) == 1:
            quarantine = "quarantine"
        else:
            quarantine = "full"
    else:
        quarantine = ''

    if not context.has_key('direction'):
        context['direction'] = None

    if not context.has_key('order_by'):
        context['order_by'] = None
    if not context.has_key('search_for'):
        context['search_for'] = None

    if not context.has_key('query_type'):
        context['query_type'] = None

    return {
        'page_obj': page_obj,
        'paginator': paginator,
        'hits': context['hits'],
        'results_per_page': context['results_per_page'],
        'page': context['page'],
        'pages': context['pages'],
        'page_numbers': page_numbers,
        'next': context['next'],
        'previous': context['previous'],
        'has_next': context['has_next'],
        'has_previous': context['has_previous'],
        'show_first': 1 not in page_numbers,
        'show_last': context['pages'] not in page_numbers,
        'quarantine': quarantine,
        'order_by': context['order_by'],
        'direction': context['direction'],
        'app': context['app'],
        'search_for': context['search_for'],
        'query_type': context['query_type'],
        'list_all': context['list_all'],
    }

register.inclusion_tag('tags/paginator.html', takes_context=True)(paginator)