import os, io, base64, contextlib, sys, traceback
os.environ['MPLBACKEND'] = 'Agg'
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
import nbformat

path = sys.argv[1]
nb = nbformat.read(path, as_version=4)
ns = {'__name__': '__main__'}
counter = 0
for cell in nb.cells:
    if cell.cell_type != 'code':
        continue
    counter += 1
    cell['outputs'] = []
    cell['execution_count'] = counter
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            exec(cell.source, ns)
    except Exception as e:
        text = buf.getvalue()
        if text:
            cell['outputs'].append(nbformat.v4.new_output('stream', name='stdout', text=text))
        cell['outputs'].append(nbformat.v4.new_output('error', ename=type(e).__name__,
                              evalue=str(e), traceback=traceback.format_exc().splitlines()))
        nbformat.write(nb, path)
        print('FAILED at cell', counter, '\n', cell.source[:120], '\n', traceback.format_exc())
        sys.exit(1)
    text = buf.getvalue()
    if text:
        cell['outputs'].append(nbformat.v4.new_output('stream', name='stdout', text=text))
    for num in plt.get_fignums():
        fig = plt.figure(num); b = io.BytesIO()
        fig.savefig(b, format='png', dpi=110, bbox_inches='tight'); b.seek(0)
        cell['outputs'].append(nbformat.v4.new_output('display_data',
                              data={'image/png': base64.b64encode(b.read()).decode()}, metadata={}))
    plt.close('all')
nbformat.write(nb, path)
print('OK executed', path, '| code cells:', counter)
