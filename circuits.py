import graphviz

class Lambda:
    def __init__(self, arg, body):
        self.arg = arg
        self.body = body

    def __str__(self):
        return f'(λ{self.arg}.{self.body})'

    def __repr__(self):
        return f'Lambda({repr(self.arg)}, {repr(self.body)})'

class Application:
    def __init__(self, func, arg):
        self.func = func
        self.arg = arg

    def __str__(self):
        return f'({self.func} {self.arg})'

    def __repr__(self):
        return f'Application({repr(self.func)}, {repr(self.arg)})'

    def eval(self):
        return eval(str(self), {'PRINT_NUM': lambda f: print(f(lambda x: x + 1)(0))})

class Var:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def __repr__(self):
        return f'Var({repr(self.name)})'

def pull(s):
    parens = 0
    for i, c in enumerate(s):
        if c == '(': parens += 1
        elif c == ')': parens -= 1
        if parens == -1 or (c == ' ' and parens <= 0): return s[:i]
    return s

def tokenize(string):
    res = []
    cur = ''
    for c in string:
        if c in '(λ. )':
            if cur:
                res.append(cur)
                cur = ''
            res.append(c)
        else:
            cur += c
    if cur:
        res.append(cur)
    return res

def parse(expr):
    if expr[0] == '(':
        if expr[1] == 'λ':
            return Lambda(expr[2], parse(pull(expr[4:-1])))
        else:
            func = pull(expr[1:])
            l = len(func)
            args = []
            while l < len(expr) - 2:
                arg = pull(expr[l + 2:])
                l += len(arg) + 1
                args.append(parse(arg))
            return Application(parse(func), args[0])
    elif expr[0] == 'λ':
        return Lambda(expr[1], parse(pull(expr[3:])))
    else:
        return Var(expr[0])

ast = parse(tokenize('λf.λx.λy.((f y) x)'))
ast = parse(tokenize('(λf.((λy.(f (y y))) (λx.(f (x x)))))'))
print(ast)
print(repr(ast))

graph = graphviz.Digraph()
graph.graph_attr['rankdir'] = 'RL'
graph.node_attr['shape'] = 'box'

cluster_number = 0
application_number = 0

def graph_function(context, function, out):
    global graph, cluster_number
    cluster_name = f'cluster_{cluster_number}'
    cluster_number += 1
    cluster = graphviz.Digraph(name=cluster_name)
    cluster.node(function.arg)

    if isinstance(function.body, Lambda):
        graph_function(cluster, function.body, out)
    elif isinstance(function.body, Application):
        graph_application(cluster, function.body, out)
    elif isinstance(function.body, Var):
        graph.edge(f'{function.body}:w', out)

    context.subgraph(cluster)

def graph_application(context, application, out):
    global graph, application_number
    application_name = f'application_{application_number}'
    application_number += 1
    context.node(application_name, label='')
    graph.edge(f'{application_name}:w', out)
    if isinstance(application.func, Lambda):
        graph_function(context, application.func, f'{application_name}:n')
    elif isinstance(application.func, Application):
        graph_application(context, application.func, f'{application_name}:n')
    elif isinstance(application.func, Var):
        graph.edge(f'{application.func}:w', f'{application_name}:n')

    if isinstance(application.arg, Lambda):
        graph_function(context, application.arg, f'{application_name}:e')
    elif isinstance(application.arg, Application):
        graph_application(context, application.arg, f'{application_name}:e')
    elif isinstance(application.arg, Var):
        graph.edge(f'{application.arg}:w', f'{application_name}:e')

graph_function(graph, ast, 'out:e')

graph.view()