# -*- coding: utf-8 -*-
from lunr.builder import Builder
from lunr.stemmer import stemmer
from lunr.stop_word_filter import stop_word_filter
from lunr.trimmer import trimmer
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name

import base64
import pygments


def javascript_uri(html):
    """Because data-uri for text/html is not supported by IE"""
    if isinstance(html, str):
        html = html.encode('utf-8')
    return (
        'javascript:(function(){{'
        'var w=window.open();'
        'w.document.open();'
        'w.document.write(window.atob(\'{}\'));'
        'w.document.close();'
        '}})();'.format(base64.b64encode(html).decode('utf-8'))
    )


def data_uri(mimetype, data):
    return 'data:{};base64,{}'.format(
        mimetype,
        base64.b64encode(data).decode('utf-8'),
    )


def highlight(language, data):
    lexer = get_lexer_by_name(language)
    formatter = HtmlFormatter(noclasses=True, nowrap=True)
    return pygments.highlight(data, lexer, formatter)


def lunr_builder(ref, fields):
    """A convenience function to configure and construct a lunr.Builder.

    Returns:
        Index: The populated Index ready to search against.
    """
    builder = Builder()
    builder.pipeline.add(trimmer, stop_word_filter, stemmer)
    builder.search_pipeline.add(stemmer)
    builder.ref(ref)
    for field in fields:
        builder.field(field)
    return builder


def readable_keyword(s):
    """Return keyword with only the first letter in title case
    """
    if s and not s.startswith('*'):
        if s.count('.'):
            library, name = s.rsplit('.', 1)
            return library + '.' + name[0].title() + name[1:].lower()
        else:
            return s[0].title() + s[1:].lower()
    else:
        return s


def detect_robot_context(code, cursor_pos):
    """Return robot code context in cursor position"""
    code = code[:cursor_pos]
    line = code.rsplit('\n')[-1]
    context_parts = code.rsplit('***', 2)
    if len(context_parts) != 3 or line.lstrip() == line:
        return '__root__'
    else:
        context_name = context_parts[1].strip().lower()
        if context_name == 'settings':
            return '__settings__'
        elif context_name in ['tasks', 'test cases']:
            return '__tasks__'
        elif context_name == 'keywords':
            return '__keywords__'