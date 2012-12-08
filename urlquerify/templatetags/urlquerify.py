import re
from copy import deepcopy
from django import template
from django.template.base import token_kwargs, resolve_variable
from ..models import QueryState


register = template.Library()


class UrlquerifyNode(template.Node):
    """
    Simple filter that takes request.GET and updates/deletes/adds params into it
    Requirements: django.core.context_processors.request should be switched on!
    """
    def __init__(self, update_items=None, remove_items=None, only_items=None):
        self.update_items = update_items or {}
        self.remove_items = remove_items or []
        self.only_items = only_items or []

    def __repr__(self):
        return '<UrlquerifyNode>'

    def render(self, context):
        state = QueryState(resolve_variable('request', context))

        update_items = deepcopy(self.update_items)
        for key, val in update_items.items():
            new_value = val.resolve(context)
            if new_value:
                update_items[key] = new_value
            else:
                del update_items[key]

        state.update(**update_items)

        if self.only_items:
            state.only(*self.only_items)

        state.remove(*self.remove_items)

        query = state.serialize() or '.'
        return query


kwarg_re = re.compile(r"\w+=.+")

def token_named_args(bits, arg_names):
    if not bits or not arg_names:
        return {}

    assert isinstance(bits, list)
    assert isinstance(arg_names, list)

    args = {}

    for name in arg_names:
        try:
            index = bits.index(name)
            next_index = index + 1

            has_correct_value = True

            #  If argument name is in end of list and has no value next of it
            if len(bits) == next_index:
                has_correct_value = False

            #  If next argument is another reserved argument name
            elif bits[next_index] in arg_names:
                has_correct_value = False

            # If next argument is keyword block
            elif kwarg_re.match(bits[next_index]):
                has_correct_value = False

            if not has_correct_value:
                raise template.TemplateSyntaxError("%r named argument expected a value after it" % bits[index])

            else:
                args[name] = bits[index + 1]
                bits.pop(index) # Remove key
                bits.pop(index) # Remove value

        except ValueError:
            pass

    return args


@register.tag
def urlquerify(parser, token):
    bits = token.split_contents()
    remaining_bits = bits[1:]

    update_items = token_kwargs(remaining_bits, parser, support_legacy=True)

    named_args = token_named_args(remaining_bits, ['remove', 'only'])
    remove_items = named_args.get('remove', '').split(',')
    only_items = named_args.get('only', '').split(',')

    return UrlquerifyNode(update_items, remove_items, only_items)
