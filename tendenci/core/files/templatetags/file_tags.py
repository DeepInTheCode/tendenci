from django.template import Library, Node, TemplateSyntaxError, Variable, VariableDoesNotExist
from tendenci.core.files.models import File

register = Library()


@register.inclusion_tag("files/options.html", takes_context=True)
def file_options(context, user, file):
    context.update({
        "opt_object": file,
        "user": user
    })
    return context


@register.inclusion_tag("files/nav.html", takes_context=True)
def file_nav(context, user, file=None):
    context.update({
        "nav_object": file,
        "user": user
    })
    return context


@register.inclusion_tag("files/search-form.html", takes_context=True)
def file_search(context):
    return context


@register.inclusion_tag('files/reports/most-viewed-result.html', takes_context=True)
def most_viewed_result(context):
    event_log = context['event_log']
    context['file'] = File.objects.get(pk=event_log['object_id'])
    return context


class FilesForModelNode(Node):

    def __init__(self, context_var, *args, **kwargs):
        self.kwargs = kwargs
        self.context_var = context_var

    def render(self, context):
        instance = self.kwargs['instance']

        try:
            instance = Variable(instance).resolve(context)
        except VariableDoesNotExist:
            return ''

        files = File.objects.get_for_model(instance)

        context[self.context_var] = files
        return ''


@register.tag
def files_for_model(parser, token):
    """
    Pull a list of :model:`File` objects based on another model.

    Example::

        {% files_for_model speaker as speaker_files %}
        {% for file in speaker_files %}
            {{ file.file }}
        {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    context_var = bits[3]
    kwargs['instance'] = bits[1]

    if len(bits) < 3:
        message = "'%s' tag requires more than 3" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[2] != "as":
        message = "'%s' second argument must be 'as" % bits[0]
        raise TemplateSyntaxError(message)

    return FilesForModelNode(context_var, *args, **kwargs)


@register.filter
def size(file, size):
    """
    size examples:
        size = '100x200'
        size = '100'
        size = '100x'
        size = 'x100'
        size = '100x200/constrain'
    """
    from django.core.urlresolvers import reverse

    if not isinstance(file, File):
        return u''

    options = u''

    if '/' in size:
        size, options = size.split('/')

    kwargs = {
        'id': unicode(file.pk),
        'size': size,
    }

    if 'constrain' in options:
        kwargs['constrain'] = 'constrain'

    return reverse('file', kwargs=kwargs)
