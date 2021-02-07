import os
import subprocess as sp
import tempfile
from concurrent.futures import ThreadPoolExecutor
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-n', '--n-parallel', type=int, default=1)


OUTDIR = os.path.abspath('s4f_all_logos')
MAX_LENGTH = 14

head_logo = r'''
\documentclass{minimal}
\usepackage[paperwidth=10cm, paperheight=10cm, margin=0cm]{geometry}

\input{logo.tex}
\begin{document}
'''

head_banner = r'''
\documentclass{minimal}
\usepackage[paperwidth=14.3cm, paperheight=2.5cm, margin=0cm]{geometry}

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


def call_latex(source_file, out_dir, out_name):
    sp.run([
        'lualatex',
        '--output-directory=' + out_dir,
        '--interaction=nonstopmode',
        '--halt-on-error',
        '--jobname=' + out_name,
        source_file,
    ], stdout=sp.PIPE, check=True)
    os.remove(os.path.join(out_dir, out_name + '.log'))
    os.remove(os.path.join(out_dir, out_name + '.aux'))


def pdf2png(stem, cwd=None, dpi=600):
    sp.run([
        'inkscape',
        stem + '.pdf',
        f'--export-dpi={dpi}',
        '--export-area-page',
        '-o', stem + '.png',
    ], cwd=cwd, stdout=sp.PIPE, check=True)


def pdf2svg(stem, cwd=None):
    sp.run([
        'inkscape',
        stem + '.pdf',
        '--export-text-to-path',
        '-o', stem + '.svg',
    ], cwd=cwd, stdout=sp.PIPE, check=True)


def text_to_path(stem, cwd=None):
    sp.run([
        'inkscape',
        stem + '.pdf',
        '--export-text-to-path',
        '-o', stem + '.pdf',
    ], cwd=cwd, stdout=sp.PIPE, check=True)


def create_all_formats(source_file, filename, groupdir, dpi=600):
    call_latex(source_file, groupdir, filename)
    text_to_path(filename, cwd=groupdir)
    pdf2png(filename, cwd=groupdir, dpi=dpi)
    pdf2svg(filename, cwd=groupdir)


def build_logo(regionalgruppe, filename, groupdir):
    '''
    Create the logos for a regionalgroup by running
    lualatex on a temporary file and then converting the
    resulting pdf to svg, png and pdf with text converted to path using inkscape.
    '''
    with tempfile.NamedTemporaryFile(mode='w') as f:
        f.write(head_logo)

        if len(regionalgruppe) < MAX_LENGTH:
            f.write(rf'\regionallogo{{{regionalgruppe.upper()}}}')
        else:
            size = 30 * MAX_LENGTH / len(regionalgruppe)
            f.write(rf'\regionallogo[{size:.1f}]{{{regionalgruppe.upper()}}}')

        f.write(foot)
        f.flush()
        create_all_formats(f.name, filename, groupdir)


def build_banner(regionalgruppe, filename, groupdir, padding=False):
    '''
    Create the logos for a regionalgroup by running
    lualatex on a temporary file and then converting the
    resulting pdf to svg, png and pdf with text converted to path using inkscape.
    '''
    with tempfile.NamedTemporaryFile(mode='w') as f:
        f.write(head_banner)

        p = '*' if padding else ''
        size = min(30, 30 * MAX_LENGTH / len(regionalgruppe))

        f.write(rf'\regionalbanner{p}[{size:.1f}]{{{regionalgruppe}}}{{{regionalgruppe.upper()}}}')

        f.write(foot)
        f.flush()
        # we want 100 pixels per cm, not inch
        dpi = 254
        create_all_formats(f.name, filename, groupdir, dpi=dpi)


def build_all(regionalgruppe):
    safe_name = sanitize_name(regionalgruppe)

    groupdir = os.path.join(OUTDIR, 's4f_logos_' + safe_name)
    os.makedirs(groupdir, exist_ok=True)

    build_logo(regionalgruppe, 's4f_logo_' + safe_name, groupdir)
    build_banner(regionalgruppe, 's4f_banner_' + safe_name, groupdir)
    build_banner(regionalgruppe, 's4f_banner_padding_' + safe_name, groupdir, padding=True)

    zip_name = f's4f_logos_{safe_name}.zip'
    sp.run(['zip', '-FSr', zip_name, os.path.basename(groupdir)], cwd=OUTDIR)


if __name__ == '__main__':
    args = parser.parse_args()

    with open('regionalgruppen.txt') as f:
        regionalgruppen = [l.strip() for l in f]

    os.makedirs(OUTDIR, exist_ok=True)

    if args.n_parallel == 1:
        for regionalgruppe in regionalgruppen:
            print('Building', regionalgruppe)
            build_all(regionalgruppe)
            print('Done')
    else:
        with ThreadPoolExecutor(args.n_parallel) as pool:
            pool.map(build_all, regionalgruppen)
