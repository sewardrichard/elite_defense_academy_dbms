import importlib, importlib.util, sys
mods=['reportlab.lib.colors','reportlab.lib.pagesizes','reportlab.platypus','reportlab.lib.styles','reportlab.graphics.shapes','reportlab.graphics.charts.pie']
for m in mods:
    spec = importlib.util.find_spec(m)
    print(m, 'spec=', bool(spec))
    try:
        importlib.import_module(m)
        print('OK', m)
    except Exception as e:
        print('ERR', m, type(e).__name__, e)
print('PY', sys.executable)
print('TOP_REPORTLAB_SPEC=', bool(importlib.util.find_spec('reportlab')))
