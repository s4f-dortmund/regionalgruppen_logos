import os
import subprocess as sp
import tempfile
from concurrent.futures import ThreadPoolExecutor


OUTDIR = os.path.abspath('build')
MAX_LENGTH = 14

head = r'''
\input{logo.tex}
\begin{document}
'''

foot = r'''
\end{document}
'''


def build_logo(regionalgruppe):
    with tempfile.NamedTemporaryFile(mode='w') as f:
        f.write(head)

        if len(regionalgruppe) < MAX_LENGTH:
            f.write(rf'\regionallogo{{{regionalgruppe.upper()}}}')
        else:
            size = 30 * MAX_LENGTH / len(regionalgruppe)
            f.write(rf'\regionallogo[{size:.1f}]{{{regionalgruppe.upper()}}}')

        f.write(foot)
        f.flush()

        filename = 's4f_logo_' + (
            regionalgruppe.lower()
            .replace('/', '-')
            .replace(' ', '')
            .replace('ä', 'ae')
            .replace('ö', 'oe')
            .replace('ü', 'ue')
            .replace('ß', 'ss')
        )

        sp.run([
            'lualatex',
            '--output-directory=' + OUTDIR,
            '--interaction=nonstopmode',
            '--halt-on-error',
            '--jobname=' + filename,
            f.name,
        ], stdout=sp.PIPE, check=True)

        sp.run([
            'inkscape',
            filename + '.pdf',
            '--without-gui',
            '--export-dpi=600',
            '--export-area-drawing',
            '--export-png=' + filename + '.png',
        ], cwd=OUTDIR, stdout=sp.PIPE, check=True)

        sp.run([
            'inkscape',
            filename + '.pdf',
            '--without-gui',
            '--export-text-to-path',
            '--export-plain-svg=' + filename + '.svg',
        ], cwd=OUTDIR, stdout=sp.PIPE, check=True)

    print(regionalgruppe, 'done')


if __name__ == '__main__':
    with open('regionalgruppen.txt') as f:
        regionalgruppen = [l.strip() for l in f]

    os.makedirs(OUTDIR, exist_ok=True)
    with ThreadPoolExecutor(8) as pool:
        pool.map(build_logo, regionalgruppen)
