import re
import operator
import os


VAR_TOKEN_START = "{{"
VAR_TOKEN_END = "}}"
TOK_REGEX = re.compile( r"(%s.*?%s)" % ( VAR_TOKEN_START, VAR_TOKEN_END ) )
WHITESPACE = re.compile(r'\s+')

ARITHMATIC_REGEX = re.compile(r"({{(\s*?\d*\s*?(\+|-|\*|\/)\s*?\d*\s*?)*?}})")

LHS_REGEX = re.compile(r"(\d*?\s*?(\+|-|\*|\/))")
RHS_REGEX = re.compile(r"((\+|-|\*|\/)\s*?\d*?)")

logical_opreators = {
    '<': operator.lt,
    '>': operator.gt,
    '==': operator.eq,
    '!=': operator.ne,
    '<=': operator.le,
    '>=': operator.ge
}

arithmatic_opreators = {
    '+': operator.add,
    '-': operator.sub,
    '*': operator.mul,
    '/': operator.truediv,
    '%': operator.mod,
}


def resolve(name, context):
    if name.startswith('..'):
        context = context.get('..', {})
        name = name[2:]
    try:
        for tok in name.split('.'):
            context = context[tok]
        return context
    except:
        return ''

class Engine:
    def __init__(self,
                 template_folder=f"{os.getcwd()}\\templates",
                 static_folder=f"{os.getcwd()}\\static"):
        self.template_folder = template_folder
        self.static_folder = static_folder

    def render_template(self, path, **kwargs):
        template = TemplateManager(os.path.join(self.template_folder, path))
        c = Compiler(template.read).compile(kwargs)
        return c

class Compiler:
    def __init__(self, template_string):
        self.template_string = template_string

    def each_fragment(self):
        for fragment in TOK_REGEX.split(self.template_string):
            if VAR_TOKEN_START in fragment:
                yield fragment

    def compile(self, context):
        root = self.template_string
        for fragment in self.each_fragment():
            frag = _Fragment(fragment)
            v = _Variable(frag.clean).render_variable(context)
            root = root.replace(frag.give, v)
        return root

class TemplateManager:
    def __init__(self, path):
        self.template = open(path, 'r', encoding='utf-8')
        self.read = self.raw_read()

    def raw_read(self):
        return self.template.read()

class _Variable:
    def __init__(self, name):
        self.name = name

    def render_variable(self, context):
        return resolve(self.name, context)

class _Fragment:
    def __init__(self, raw_text):
        self.raw = raw_text
        self.clean = self.clean_fragment()
        self.give = self.give_fragment()

    def give_fragment(self):
        if VAR_TOKEN_START in self.raw[:2]:
            return self.raw
        return ''

    def clean_fragment(self):
        if VAR_TOKEN_START in self.raw[:2]:
            return self.raw.strip()[2:-2].strip()
        return self.raw

