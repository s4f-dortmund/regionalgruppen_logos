import os
import subprocess as sp
import tempfile
from concurrent.futures import ThreadPoolExecutor
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-n', '--n-parallel', type=int, default=1)


OUTDIR = os.path.abspath('s4f-regionalgruppen-logos')
MAX_LENGTH = 14

head = r'''
\input{logo.tex}
\begin{document}
'''

foot = r'''
\end{document}
'''


def sanitize_name(name):
    '''remove or replace non-ascii and special characters from name'''
    return (
        name.lower()
        .replace('/', '-')
        .replace('(', '_')
        .replace(')', '')
        .replace(' ', '')
        .replace('ä', 'ae')
        .replace('ö', 'oe')
        .replace('ü', 'ue')
        .replace('ß', 'ss')
    )


def build_logo(regionalgruppe):
    '''
    Create the logos for a regionalgroup by running
    lualatex on a temporary file and then converting the
    resulting pdf to svg, png and pdf with text converted to path using inkscape.
    '''
    with tempfile.NamedTemporaryFile(mode='w') as f:
        f.write(head)

        if len(regionalgruppe) < MAX_LENGTH:
            f.write(rf'\regionallogo{{{regionalgruppe.upper()}}}')
        else:
            size = 30 * MAX_LENGTH / len(regionalgruppe)
            f.write(rf'\regionallogo[{size:.1f}]{{{regionalgruppe.upper()}}}')

        f.write(foot)
        f.flush()

        name = sanitize_name(regionalgruppe)

        filename = 's4f_logo_' + name
        groupdir = os.path.join(OUTDIR, name)
        os.makedirs(groupdir, exist_ok=True)

        sp.run([
            'lualatex',
            '--output-directory=' + groupdir,
            '--interaction=nonstopmode',
            '--halt-on-error',
            '--jobname=' + filename,
            f.name,
        ], stdout=sp.PIPE, check=True)
        os.remove(os.path.join(groupdir, filename + '.log'))
        os.remove(os.path.join(groupdir, filename + '.aux'))

        sp.run([
            'inkscape',
            filename + '.pdf',
            '--without-gui',
            '--export-dpi=600',
            '--export-area-page',
            '--export-png=' + filename + '.png',
        ], cwd=groupdir, stdout=sp.PIPE, check=True)

        sp.run([
            'inkscape',
            filename + '.pdf',
            '--without-gui',
            '--export-text-to-path',
            '--export-plain-svg=' + filename + '.svg',
        ], cwd=groupdir, stdout=sp.PIPE, check=True)

        sp.run([
            'inkscape',
            filename + '.pdf',
            '--without-gui',
            '--export-text-to-path',
            '--export-pdf=' + filename + '.pdf',
        ], cwd=groupdir, stdout=sp.PIPE, check=True)


if __name__ == '__main__':
    args = parser.parse_args()

    with open('regionalgruppen.txt') as f:
        regionalgruppen = [l.strip() for l in f]

    os.makedirs(OUTDIR, exist_ok=True)

    if args.n_parallel == 1:
        for regionalgruppe in regionalgruppen:
            print('Building', regionalgruppe)
            build_logo(regionalgruppe)
            print('Done')
    else:
        with ThreadPoolExecutor(args.n_parallel) as pool:
            pool.map(build_logo, regionalgruppen)
