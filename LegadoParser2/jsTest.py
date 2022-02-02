from RuleJs.JS import EvalJs

with open('jsTest.js', 'r', encoding='utf-8') as f:
    js = f.read()
    evalJs = EvalJs({})
    print(evalJs.eval('js=1'))
