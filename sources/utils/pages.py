import codecs


import types

from utils.auxiliary import align
from utils.representation import represent
from utils.tracing import describe_exception, \
    describe_thread, extract_exception_trace, format_exception_trace


PAGE_STYLES = """\
body{margin:0;min-width:50rem;color:black;background:white;\
font-family:"Trebuchet MS",Helvetica,sans-serif;font-size:2rem}\
.heading{padding:1rem 2rem;color:white;background:brown;font-size:1.5em}\
.content{padding:1rem 2rem 2rem}\
.extra{padding:1rem 2rem 2rem}\
.extra:empty{display:none}\
"""

PAGE_SCRIPTS = """\
function expand(e){\
for(var t=e.firstChild;t&&t.nodeType!=Node.ELEMENT_NODE;)t=t.nextSibling;\
for(t.style.display="none",t=t.nextSibling;t&&t.nodeType!=Node.ELEMENT_NODE;)t=t.nextSibling;\
t.style.display="block"}\
function copy(e){\
var t=document.createElement("textarea");\
t.style.position="fixed",t.style.top="0",t.style.left="0",t.style.width="0",t.style.height="0";\
t.style.visible="hidden",t.value=e,document.body.appendChild(t);\
try{t.select(),document.execCommand("Copy")}finally{document.body.removeChild(t)}}\
"""

PAGE_TEMPLATE = """\
<head>
<title>{title}</title>
<style>{styles}</style>
<script>{scripts}</script>
</head>
<body>
<div class="heading">{heading}</div>
<div class="content">{content}</div>
<div class="extra">{extra}</div>
</body>
"""


def compose_page(content, title=None, heading=None, extra=None, styles=None, scripts=None):
    if not title:
        title = "VDOM Server"

    if not heading:
        heading = title

    if styles:
        styles = [PAGE_STYLES, styles]
    else:
        styles = [PAGE_STYLES]

    if scripts:
        scripts = [PAGE_SCRIPTS, scripts]
    else:
        scripts = [PAGE_SCRIPTS]

    if isinstance(extra, types.FunctionType):
        extra = extra()

    if isinstance(extra, tuple):
        extra_styles, extra_scripts, extra = extra
        if isinstance(extra_styles, (tuple, list)):
            styles.extend(extra_styles)
        elif extra_styles:
            styles.append(extra_styles)
        if isinstance(extra_scripts, (tuple, list)):
            scripts.extend(extra_scripts)
        if extra_scripts:
            scripts.append(extra_scripts)
    elif isinstance(extra, bytes):
        pass
    else:
        extra = ""

    return PAGE_TEMPLATE.format(
        styles="\n".join(styles), scripts="\n".join(scripts),
        title=title, heading=heading, content=content,
        extra=extra)


TRACE_STYLES = """\
.extra{font-family:Consolas,monaco,monospace;font-size:.4em}\
.extra .debug{margin:0 -1rem;overflow:hidden;background:url("data:image/svg+xml;utf8,\
<svg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 10 10'>\
<path d='M-2,2 l4,-4 M0,10 l10,-10 M8,12 l4,-4' stroke='black' stroke-opacity='0.03' stroke-width='3.5'/>\
</svg>")}
.extra .error{position:relative;padding:.5rem 3rem .5rem 1rem;\
color:gold;background-color:brown;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;\
font-weight:bold;background-image:url("data:image/svg+xml;utf8,\
<svg xmlns='http://www.w3.org/2000/svg' width='32' height='32' viewBox='0 0 10 10'>\
<path d='M-2,2 l4,-4 M0,10 l10,-10 M8,12 l4,-4' stroke='black' stroke-opacity='0.1' stroke-width='3.5'/>\
</svg>")}\
.extra .section{margin:1rem}\
.extra .cause{color:brown}\
.extra .cause .items{border-color:brown}\
.extra .locals{color:sienna}\
.extra .locals .items{border-color:sienna}\
.extra .thread{color:steelblue}\
.extra .thread .items{border-color:steelblue}\
.extra .other .thread{color:darkcyan}\
.extra .other .thread .items{border-color:darkcyan}\
.items{margin-top:.2rem;border-top:1px dashed gray;padding:.2rem 0 0 1.8rem}\
.items > div{display:flex;border-radius:2px;padding:0 .25rem;justify-content:stretch;overflow:hidden}\
.items > div:hover{background:rgba(0,0,0,0.05)}\
.items > div > div{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}\
.items > div > div:not(:only-of-type):first-of-type{flex:0 0 35rem}\
.items > div > div:not(:only-of-type):not(:last-of-type):after{content:"\\00a0\
\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\
\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\
\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\
\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\
\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\
\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\
\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\
\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026\\2026"}\
.items > div > div:not(:only-of-type):not(:first-of-type):before{content:"\\00a0"}\
.items > div > div:not(:only-of-type):not(:first-of-type){overflow:hidden;text-overflow:ellipsis;\
white-space:nowrap;\flex:1 1 1rem}\
.expand{margin:calc(-0.25rem - 1px);border:1px solid rgba(0,0,0,0.075);border-radius:2px;padding:.25rem;\
background-color:rgba(255,255,255,0.5);cursor:pointer}\
.expand:hover{border-color:rgba(0,0,0,0);background-color:rgba(0,0,0,0.05)}\
.copy{position:absolute;right:1rem;cursor:pointer;font-variant:small-caps}\
.copy:hover{color:white}\
"""


def compose_trace(information=None):
    values = extract_exception_trace(information, locals=True, threads=True)
    if values is None:
        return

    description, causes, trace, locals, threads = values
    report = format_exception_trace(information, locals=True, threads=True)

    lines = []
    lines.append("<div class=\"debug stripes\">")

    lines.append("<div class=\"error stripes\">")
    lines.append("<span class=\"copy\" onclick='copy(\"%s\")'>copy</span>" % codecs.encode(report, "js"))
    lines.append(codecs.encode(description, "html"))
    lines.append("</div>")

    if causes:
        lines.append("<div class=\"cause section\">")
        lines.append("<div>Caused by:</div>")
        lines.append("<div class=\"items\">")
        for _, exception, _ in causes:
            lines.append("<div><div>%s</div></div>" % codecs.encode(describe_exception(exception), "html"))
        lines.append("</div>")
        lines.append("</div>")

    lines.append("<div class=\"locals section\" onclick=\"expand(this)\">")
    lines.append("<div class=\"expand\">Locals...</div>")
    lines.append("<div style=\"display: none\">Locals:")
    lines.append("<div class=\"items\">")
    for name, value in locals.items():
        lines.append("<div><div>%s</div><div>%s</div></div>" % (codecs.encode(name, "html"), codecs.encode(value, "html")))
    lines.append("</div>")
    lines.append("</div>")
    lines.append("</div>")

    lines.append("<div class=\"thread section\">")
    lines.append("<div>Traceback for %s:</div>" % codecs.encode(describe_thread(), "html"))
    lines.append("<div class=\"items\">")
    for path, line, function, statement in trace:
        lines.append("<div><div>%s:%d:%s</div><div>%s</div></div>" % (codecs.encode(path, "html"), line, codecs.encode(function, "html"), statement))
    lines.append("</div>")
    lines.append("</div>")

    lines.append("<div class=\"other\" onclick=\"expand(this)\">")
    lines.append("<div class=\"thread section\"><div class=\"expand\">Threads...</div></div>")
    lines.append("<div style=\"display: none\">")
    for thread, thread_trace in threads.items():
        lines.append("<div class=\"thread section\">")
        lines.append("<div>Traceback for %s:</div>" % codecs.encode(describe_thread(thread), "html"))
        lines.append("<div class=\"items\">")
        for path, line, function, statement in thread_trace:
            lines.append("<div><div>%s:%d:%s</div><div>%s</div></div>" % (codecs.encode(path, "html"), line, codecs.encode(function, "html"), statement))
        lines.append("</div>")
        lines.append("</div>")
    lines.append("</div>")
    lines.append("</div>")

    lines.append("</div>")

    return TRACE_STYLES, None, "".join(lines)
