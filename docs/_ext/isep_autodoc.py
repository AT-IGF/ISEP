import types
import typing
from dataclasses import MISSING, fields, is_dataclass
from sphinx.ext.autodoc import ClassDocumenter
from sphinx.pycode import ModuleAnalyzer


class AliasAsClassDocumenter(ClassDocumenter):
    """Document class aliases (e.g. ``ModelBuilderConfig as SupervisedTrainingConfig``)
    under the alias name instead of "alias of"."""

    def import_object(self, raiseerror=False):
        result = super().import_object(raiseerror)
        self.doc_as_attr = False
        return result


def default_repr(f):
    """Readable default value of a dataclass field, or None when the field is required."""
    if f.default is not MISSING:
        return repr(f.default)
    if f.default_factory is MISSING:
        return None
    factory = f.default_factory
    if isinstance(factory, type):
        return f"{factory.__name__}()"
    return repr(factory())


def default_of(f):
    default = default_repr(f)
    return "required" if default is None else f"optional (default={default})"


def type_name(tp):
    args = typing.get_args(tp)
    if isinstance(tp, types.UnionType) or typing.get_origin(tp) is typing.Union:
        return " | ".join(type_name(arg) for arg in args)
    if args:
        origin = typing.get_origin(tp)
        return f"{origin.__name__}[{', '.join(type_name(arg) for arg in args)}]"
    if tp is type(None):
        return "None"
    return getattr(tp, "__name__", str(tp))


def summary_of(tp):
    tp = next((arg for arg in typing.get_args(tp) if is_dataclass(arg)), tp)
    doc = tp.__doc__ if is_dataclass(tp) else None
    if not doc or doc.startswith(f"{tp.__name__}("):
        return ""
    return " ".join(doc.strip().split("\n\n")[0].split())


def add_parameters(app, what, name, obj, options, lines):
    """Build a "Parameters" section from dataclass field docstrings."""
    if not is_dataclass(obj):
        return

    field_docs = ModuleAnalyzer.for_module(obj.__module__).find_attr_docs()
    lines += ["", ".. rubric:: Parameters", "   :class: isep-params-title", ""]

    for f in fields(obj):
        doc = " ".join(field_docs.get((obj.__qualname__, f.name), [])) or summary_of(
            f.type
        )
        lines += [
            ".. container:: isep-param-name",
            "",
            f"   **{f.name}** : {type_name(f.type)}, {default_of(f)}",
            "",
        ]
        if doc:
            lines += [".. container:: isep-param-doc", "", f"   {doc}", ""]


def clean_signature(app, what, name, obj, options, signature, return_annotation):
    """Build dataclass signatures from fields: names and readable defaults, without type annotations."""
    if what != "class" or not is_dataclass(obj):
        return signature, return_annotation

    parts = []
    for f in fields(obj):
        if not f.init:
            continue
        default = default_repr(f)
        parts.append(f.name if default is None else f"{f.name}={default}")
    return f"({', '.join(parts)})", None


def setup(app):
    app.add_autodocumenter(AliasAsClassDocumenter, override=True)
    app.connect("autodoc-process-docstring", add_parameters, priority=400)
    app.connect("autodoc-process-signature", clean_signature)
