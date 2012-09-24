from copy import deepcopy
from django import template
from django.template.base import token_kwargs, resolve_variable
register = template.Library()


class UrlquerifyNode(template.Node):
    def __init__(self, state_var_name, update_items=None, remove_items=None, only_items=None):
        self.state_var_name = state_var_name
        self.update_items = update_items or {}
        self.remove_items = remove_items or []
        self.only_items = only_items or []

    def __repr__(self):
        return '<UrlquerifyNode>'

    def render(self, context):
        state = deepcopy(resolve_variable(self.state_var_name, context))

        for key, val in self.update_items.iteritems():
            self.update_items[key] = val.resolve(context)

        state.update(**self.update_items)

        if self.only_items:
            state.only(*self.only_items)

        state.remove(*self.remove_items)

        return state.serialize()


def token_named_args(bits, arg_names):
    if not bits or not arg_names:
        return {}

    assert isinstance(bits, list)
    assert isinstance(arg_names, list)

    args = {}

    for name in arg_names:
        try:
            index = bits.index(name)

            # Two possible incorrect situations:
            #   1. if argument name is in end of list and has no value next of it
            #   2. If next argument is another reserved argument name
            if len(bits) == index + 1 or bits[index + 1] in arg_names:
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
    state_name = bits[1]
    remaining_bits = bits[2:]

    update_items = token_kwargs(remaining_bits, parser, support_legacy=True)

    named_args = token_named_args(remaining_bits, ['remove', 'only'])
    remove_items = named_args.get('remove', '').split(',')
    only_items = named_args.get('only', '').split(',')

    return UrlquerifyNode(state_name, update_items, remove_items, only_items)
