import base64
import re
import types

from yaql.context import EvalArg

import engine.config as cfg
from engine.dsl import helpers


def _transform_json(json, mappings):
    if isinstance(json, types.ListType):
        return [_transform_json(t, mappings) for t in json]

    if isinstance(json, types.DictionaryType):
        result = {}
        for key, value in json.items():
            result[_transform_json(key, mappings)] = \
                _transform_json(value, mappings)
        return result

    elif isinstance(json, types.ListType):
        result = []
        for value in json:
            result.append(_transform_json(value, mappings))
        return result

    elif isinstance(json, types.StringTypes) and json.startswith('$'):
        value = _convert_macro_parameter(json[1:], mappings)
        if value is not None:
            return value

    return json


def _convert_macro_parameter(macro, mappings):
    replaced = [False]

    def replace(match):
        replaced[0] = True
        return unicode(mappings.get(match.group(1)))

    result = re.sub('{(\\w+?)}', replace, macro)
    if replaced[0]:
        return result
    else:
        return mappings[macro]


@EvalArg('format', types.StringTypes)
def _format(format, *args):
    return format.format(*[t() for t in args])


@EvalArg('src', types.StringTypes)
@EvalArg('substring', types.StringTypes)
@EvalArg('value', types.StringTypes)
def _replace_str(src, substring, value):
    return src.replace(substring, value)


@EvalArg('src', types.StringTypes)
@EvalArg('replacements', dict)
def _replace_dict(src, replacements):
    for key, value in replacements.iteritems():
        if isinstance(src, str):
            src = src.replace(key, str(value))
        else:
            src = src.replace(key, unicode(value))
    return src


def _len(value):
    return len(value())


def _coalesce(*args):
    for t in args:
        val = t()
        if val:
            return val
    return None


@EvalArg('value', types.StringTypes)
def _base64encode(value):
    return base64.b64encode(value)

@EvalArg('value', types.StringTypes)
def _base64decode(value):
    return base64.b64decode(value)


@EvalArg('group', types.StringTypes)
@EvalArg('setting', types.StringTypes)
def _config(group, setting):
    return cfg.CONF[group][setting]


@EvalArg('setting', types.StringTypes)
def _config_default(setting):
    return cfg.CONF[setting]


@EvalArg('value', types.StringTypes)
def _upper(value):
    return value.upper()


@EvalArg('value', types.StringTypes)
def _lower(value):
    return value.lower()


@EvalArg('separator', types.StringTypes)
def _join(separator, *args):
    return separator.join([t() for t in args])


@EvalArg('value', types.StringTypes)
@EvalArg('separator', types.StringTypes)
def _split(value, separator):
    return value.split(separator)


@EvalArg('value', types.StringTypes)
@EvalArg('prefix', types.StringTypes)
def _startswith(value, prefix):
    return value.startswith(prefix)


@EvalArg('value', types.StringTypes)
@EvalArg('suffix', types.StringTypes)
def _endswith(value, suffix):
    return value.endswith(suffix)


@EvalArg('value', types.StringTypes)
def _trim(value):
    return value.strip()


@EvalArg('value', types.StringTypes)
@EvalArg('pattern', types.StringTypes)
def _mathces(value, pattern):
    return re.match(pattern, value) is not None


@EvalArg('value', types.StringTypes)
@EvalArg('index', int)
@EvalArg('length', int)
def _substr(value, index=0, length=-1):
    if length < 0:
        return value[index:]
    else:
        return value[index:index+length]


def _str(value):
    value = value()
    if value is None:
        return None
    return unicode(value)


def _int(value):
    value = value()
    return int(value)


def _pselect(collection, composer):
    return helpers.parallel_select(collection(), composer)


def register(context):
    context.register_function(
        lambda json, mappings: _transform_json(json(), mappings()), 'bind')

    context.register_function(_format, 'format')
    context.register_function(_replace_str, 'replace')
    context.register_function(_replace_dict, 'replace')
    context.register_function(_len, 'len')
    context.register_function(_coalesce, 'coalesce')
    context.register_function(_base64decode, 'base64decode')
    context.register_function(_base64encode, 'base64encode')
    context.register_function(_config, 'config')
    context.register_function(_config_default, 'config')
    context.register_function(_lower, 'toLower')
    context.register_function(_upper, 'toUpper')
    context.register_function(_join, 'join')
    context.register_function(_split, 'split')
    context.register_function(_pselect, 'pselect')
    context.register_function(_startswith, 'startsWith')
    context.register_function(_endswith, 'endsWith')
    context.register_function(_trim, 'trim')
    context.register_function(_mathces, 'matches')
    context.register_function(_substr, 'substr')
    context.register_function(_str, 'str')
    context.register_function(_int, 'int')
