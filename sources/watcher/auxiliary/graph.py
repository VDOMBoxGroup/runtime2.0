

import sys
import types
import numbers
import gc
import inspect

from memory.generic import MemoryBase
from .auxiliary import quote


DEFAULT_GRAPH_DEPTH = 10
DEFAULT_OPTIMIZE = True
DEFAULT_MINIFY = True
DEFAULT_SKIP_FUNCTIONS = True


def generate_graph(objects, depth=DEFAULT_GRAPH_DEPTH,
        optimize=DEFAULT_OPTIMIZE, minify=DEFAULT_MINIFY, skip_functions=DEFAULT_SKIP_FUNCTIONS):
    print("Generate graph for %s" % \
        (", ".join("%08X" % id(object) for object in objects)
            if len(objects) < 10 else "%d objects" % len(objects)))
    # TODO: __del__
    # TODO: Dereference members

    def check_owners(target):
        if id(target) in owners:
            return

        ignore.add(id(sys._getframe()))
        sources = gc.get_referrers(target)
        ignore.add(id(sources))
        try:
            master = None

            if isinstance(target, dict):
                for source in sources:
                    if id(source) in ignore:
                        continue

                    if skip_functions and \
                            isinstance(source, types.FunctionType) and \
                            source.__globals__ is target:
                        continue

                    reference = getattr(source, "__dict__", None)
                    if isinstance(reference, types.DictProxyType):
                        reference = gc.get_referents(gc.get_referents(reference))[0]

                    if target is reference:
                        if master is None:
                            master = source
                        else:
                            owners[id(target)] = None
                            return
            elif isinstance(target, tuple):
                for source in sources:
                    if id(source) in ignore:
                        continue

                    if getattr(source, "__bases__", None) is target or getattr(source, "__mro__", None) is target:
                        if master is None:
                            master = source
                        else:
                            owners[id(target)] = None
                            return

            if master is None:
                return
            else:
                owners[id(target)] = master
                return
        finally:
            ignore.remove(id(sources))
            ignore.remove(id(sys._getframe()))
            del sources

    def show_edge(source, target):
        if minify and id(source) in owners:
            if isinstance(source, dict):
                for key, value in source.items():
                    if value is target:
                        membership_edges.append((id(owners[id(source)]), mapping.get(id(target), id(target)), quote(key)))
                        return
            elif isinstance(source, tuple):
                for item in source:
                    if item is target:
                        return

        if mapping.get(id(target), None) == id(source):
            return

        if isinstance(target, dict):
            source_dict = getattr(source, "__dict__", None)
            if isinstance(source_dict, types.DictProxyType):
                source_dict = gc.get_referents(gc.get_referents(source_dict))[0]
            if target is source_dict:
                ownership_edges.append((id(source), mapping.get(id(target), id(target)), "__dict__"))
                return

        if isinstance(source, type):
            if target in source.__bases__:
                if minify:
                    inheritance_edges.append((id(source), mapping.get(id(target), id(target)), ""))
                return

        if getattr(source, "__bases__", None) is target:
            inheritance_edges.append((id(source), mapping.get(id(target), id(target)), "__bases__"))
            return

        if getattr(source, "__mro__", None) is target:
            inheritance_edges.append((id(source), mapping.get(id(target), id(target)), "__mro__"))
            return

        if getattr(source, "__class__", None) is target:
            instance_edges.append((id(source), mapping.get(id(target), id(target)), ""))
            return
        elif getattr(source, "__self__", None) is target:
            ownership_edges.append((id(source), mapping.get(id(target), id(target)), ""))
            return
        elif isinstance(source, dict):
            try:
                label = quote(repr(list(source.keys())[list(source.values()).index(target)]))
            except BaseException:
                label = "?"
            elementary_edges.append((id(source), mapping.get(id(target), id(target)), label))
            return
        elif isinstance(source, (tuple, list)):
            try:
                label = str(source.index(target))
            except BaseException:
                label = "?"
            elementary_edges.append((id(source), mapping.get(id(target), id(target)), label))
            return
        elif isinstance(source, types.FrameType) and source.f_back is target:
            traceback_edges.append((id(source), mapping.get(id(target), id(target)), ""))
            return

        try:
            if target in source:
                elementary_edges.append((id(source), mapping.get(id(target), id(target)), ""))
                return
        except BaseException:
            pass

        for name in dir(source):
            try:
                if target is getattr(source, name):
                    elementary_edges.append((id(source), mapping.get(id(target), id(target)), name))
                    return
            except Exception:
                pass

        if getattr(source, "cell_contents", None) is target:
            elementary_edges.append((id(source), mapping.get(id(target), id(target)), "cell_contents"))
            return

        reference_edges.append((id(source), mapping.get(id(target), id(target)), ""))

    def show_node(target):
        kind = type(target).__name__

        if isinstance(target, type):
            name = target.__name__
            details = " "
            module = target.__module__
            storage = inheritance_nodes
        elif isinstance(target, types.ModuleType):
            name = getattr(target, "__name__", "<no name>")
            details = " "
            module = " "  # target.__package__
            storage = module_nodes
        elif isinstance(target, (types.BuiltinMethodType, types.BuiltinFunctionType)):
            name = target.__name__
            details = " "
            module = " "
            storage = elementary_nodes
        elif isinstance(target, types.FunctionType):
            name = target.__name__
            details = " "
            module = getattr(inspect.getmodule(target), "__name__", " ")
            storage = callable_nodes
        elif isinstance(target, types.CodeType):
            name = target.co_name
            details = " "
            module = getattr(inspect.getmodule(target), "__name__", " ")
            storage = callable_nodes
        elif isinstance(target, types.MethodType):
            if target.__self__ is not None:
                kind = "bound " + kind
            name = target.__func__.__name__
            details = " "
            module = getattr(inspect.getmodule(target), "__name__", " ")
            storage = callable_nodes
        elif isinstance(target, types.FrameType):
            name = target.f_code.co_name  # clarify_source_path(target.f_code.co_filename), target.f_lineno
            details = " "
            module = getattr(inspect.getmodule(target), "__name__", " ")
            storage = callable_nodes
        elif isinstance(target, types.InstanceType):
            name = target.__class__.__name__
            details = " "
            module = target.__module__
            storage = elementary_nodes
        elif type(target).__module__ == "__builtin__":
            name = quote(repr(target))[:40] if isinstance(target, (bytes, numbers.Number, bool, type(None))) else " "
            if isinstance(target, (dict, tuple, list, set)):
                count = len(target)
                details = "1 item" if count == 1 else "%d items" % count
            else:
                details = " "
            module = " "
            storage = elementary_nodes
        else:
            kind = "object"
            name = type(target).__name__
            if isinstance(target, MemoryBase):
                details = ":".join([_f for _f in (getattr(target, "id", None), getattr(target, "name", None)) if _f]).lower()
                if getattr(target, "virtual", None):
                    name += " (Virtual)"
            else:
                details = " "
            module = type(target).__module__
            storage = object_nodes

        for primary in objects:
            if target is primary:
                storage = primary_nodes
                break

        storage.append((id(target), quote("\n".join((kind, name, details, module, "%08X" % id(target))))))

    primary_nodes = []
    inheritance_nodes = []
    callable_nodes = []
    module_nodes = []
    elementary_nodes = []
    object_nodes = []

    membership_edges = []
    callable_edges = []
    traceback_edges = []
    reference_edges = []
    ownership_edges = []
    instance_edges = []
    inheritance_edges = []
    elementary_edges = []

    objects, queue, levels, ignore, mapping, owners = tuple(objects), [], {}, set(), {}, {}

    ignore.add(id(objects))
    ignore.add(id(sys._getframe()))
    ignore.add(id(queue))
    ignore.add(id(owners))

    for target in objects:
        if minify:
            check_owners(target)
        levels[id(target)] = 0
        queue.append(target)

    gc.collect()
    while queue:
        target = queue.pop(0)
        level = levels[id(target)]

        if minify and id(target) in owners:
            mapping[id(target)] = id(owners[id(target)])
        else:
            show_node(target)

        if level > depth:
            continue
        if isinstance(target, (types.ModuleType, bytes, numbers.Number, bool)):
            continue

        sources = gc.get_referrers(target)
        ignore.add(id(sources))
        try:
            for source in sources:
                if id(source) in ignore:
                    continue
                if skip_functions and isinstance(source, types.FunctionType) and source.__globals__ is target:
                    continue

                if id(source) not in levels:
                    if minify:
                        check_owners(source)
                    levels[id(source)] = level + 1
                    queue.append(source)

                show_edge(source, target)
        finally:
            ignore.remove(id(sources))
            del sources

    # D69191 A06C6C     Light Red           Unknown References
    # DEB887 A68A65     Light Brown         Objects, Membership
    # CCC0A8            Light Light Brown
    # D497E3 9F71AA     Light Magenta       Inheritance
    # D8D8D8 A2A2A2     Light Gray          Elementary Objects, Elementary References
    # 57A77A            Ocean Green
    # 65B488            Light Green         Primary Objects
    # 76A3C9            Light Blue          Callable Objects
    # DECD87            Light Yellow        Modules
    # CDC9A5            Light Light Yellow
    # 87D5DE            Light Blue

    # "\tpack=true;\n" \
    yield "digraph ObjectGraph\n" \
        "{\n" \
        "\toverlap=false;\n" \
        "\toutputorder=nodesfirst;\n" \
        "\tbgcolor=\"#FFFFFF\";\n" \
        "\tnode[shape=rectangle, style=filled, penwidth=6, color=\"#FFFFFF\", fillcolor=\"#000000\", fontname=Consolas, fontsize=8];\n" \
        "\tedge[arrowsize=0.75, penwidth=2, color=\"#000000\", fontcolor=\"#000000\", fontname=Consolas, fontsize=8];\n"
    for storage, style in (
            (primary_nodes, 'fillcolor="#65B488"'),
            (inheritance_nodes, 'fillcolor="#D497E3"'),
            (callable_nodes, 'fillcolor="#76A3C9"'),
            (module_nodes, 'fillcolor="#DECD87"'),
            (elementary_nodes, 'fillcolor="#D8D8D8"'),
            (object_nodes, 'fillcolor="#DEB887"')):
        if not storage:
            continue
        yield "\tnode[%s];\n" % style
        for name, label in storage:
            yield "\t%s%s;\n" % (name, '[label="%s"]' % label if label else "")
    for storage, style in (
            (elementary_edges, 'color="#D8D8D8", fontcolor="#A2A2A2", arrowhead=normal, weight=1'),
            (membership_edges, 'color="#DEB887", fontcolor="#A68A65", arrowhead=normal, weight=10'),
            (callable_edges, 'color="#DEB887", fontcolor="#A68A65", arrowhead=normal, weight=30'),
            (traceback_edges, 'color="#76A3C9", fontcolor="#A68A65", arrowhead=normal, weight=30'),
            (reference_edges, 'color="#D69191", fontcolor="#A06C6C", arrowhead=normal, weight=1'),
            (ownership_edges, 'color="#DEB887", fontcolor="#A68A65", arrowhead=empty, weight=1'),
            (instance_edges, 'color="#D497E3", fontcolor="#9F71AA", arrowhead=empty, weight=1'),
            (inheritance_edges, 'color="#D497E3", fontcolor="#9F71AA", arrowhead=normal, weight=10')):
        if not storage:
            continue
        yield "\tedge[%s];\n" % style
        for name1, name2, label in storage:
            yield "\t%s->%s%s;\n" % (name1, name2, '[label=" %s"]' % label if label else "")
    yield "}\n"
