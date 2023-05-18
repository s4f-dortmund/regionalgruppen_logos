from pathlib import Path
import os
import subprocess as sp
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-n', '--n-parallel', type=int, default=1)


OUTDIR = Path('s4f_all_logos').absolute()
MAX_LENGTH = 14

head_logo = r'''
\documentclass{minimal}
\usepackage[paperwidth=10cm, paperheight=10cm, margin=0cm]{geometry}

\input{logo.tex}
\begin{document}
'''

head_banner = r'''
\documentclass[margin=0pt]{standalone}

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
    ret = sp.run([
        'lualatex',
        '--output-directory=' + out_dir,
        '--interaction=nonstopmode',
        '--halt-on-error',
        '--jobname=' + out_name,
        source_file,
    ], stdout=sp.PIPE, stderr=sp.STDOUT)

    if ret.returncode != 0 or not os.path.isfile(os.path.join(out_dir, out_name + '.pdf')):
        print(ret.stdout.decode('utf-8'))
        raise OSError('Calling latex failed')

    os.remove(os.path.join(out_dir, out_name + '.log'))
    os.remove(os.path.join(out_dir, out_name + '.aux'))


def pdf2png(stem, cwd=None, dpi=600):
    sp.run([
        'inkscape',
        stem + '.pdf',
        f'--export-dpi={dpi}',
        '--export-area-page',
        '-o', stem + '.png',
    ], cwd=cwd, stdout=sp.PIPE, stderr=sp.STDOUT, check=True)
    if not os.path.isfile(os.path.join(cwd, stem + '.png')):
        raise OSError('Call to inkscape failed')


def pdf2svg(stem, cwd=None):
    sp.run([
        'inkscape',
        stem + '.pdf',
        '--export-text-to-path',
        '-o', stem + '.svg',
    ], cwd=cwd, stdout=sp.PIPE, stderr=sp.STDOUT, check=True)

    if not os.path.isfile(os.path.join(cwd, stem + '.svg')):
        raise OSError('Call to inkscape failed')


def text_to_path(stem, cwd=None):
    sp.run([
        'inkscape',
        stem + '.pdf',
        '--export-text-to-path',
        '-o', stem + '.pdf',
    ], cwd=cwd, stdout=sp.PIPE, stderr=sp.STDOUT, check=True)

    if not os.path.isfile(os.path.join(cwd, stem + '.pdf')):
        raise OSError('Call to inkscape failed')


def create_all_formats(source_file, filename, groupdir, dpi=600):
    call_latex(source_file, groupdir, filename)
    text_to_path(filename, cwd=groupdir)
    pdf2png(filename, cwd=groupdir, dpi=dpi)
    pdf2svg(filename, cwd=groupdir)


def build_logo(group, filename, groupdir):
    '''
    Create the logos for a group by running
    lualatex on a temporary file and then converting the
    resulting pdf to svg, png and pdf with text converted to path using inkscape.
    '''
    with tempfile.NamedTemporaryFile(mode='w') as f:
        f.write(head_logo)

        if len(group) < MAX_LENGTH:
            f.write(rf'\grouplogo{{{group.upper()}}}')
        else:
            size = 30 * MAX_LENGTH / len(group)
            f.write(rf'\grouplogo[{size:.1f}]{{{group.upper()}}}')

        f.write(foot)
        f.flush()
        create_all_formats(f.name, filename, groupdir)


def build_banner(group, filename, groupdir, padding=False):
    '''
    Create the logos for a group by running
    lualatex on a temporary file and then converting the
    resulting pdf to svg, png and pdf with text converted to path using inkscape.
    '''
    with tempfile.NamedTemporaryFile(mode='w') as f:
        f.write(head_banner)

        p = '*' if padding else ''
        size = min(30, 30 * MAX_LENGTH / len(group))

        f.write(rf'\groupbanner{p}[{size:.1f}]{{{group}}}{{{group.upper()}}}')

        f.write(foot)
        f.flush()
        # we want 100 pixels per cm, not inch
        dpi = 254
        create_all_formats(f.name, filename, groupdir, dpi=dpi)


def build_all(group, outdir_category):
    safe_name = sanitize_name(group)

    groupdir = os.path.join(outdir_category, 's4f_logos_' + safe_name)
    os.makedirs(groupdir, exist_ok=True)

    build_logo(group, 's4f_logo_' + safe_name, groupdir)
    build_banner(group, 's4f_banner_' + safe_name, groupdir)
    build_banner(group, 's4f_banner_padding_' + safe_name, groupdir, padding=True)

    zip_name = f's4f_logos_{safe_name}.zip'
    sp.run(['zip', '-FSr', zip_name, os.path.basename(groupdir)], check=True, stdout=sp.PIPE, stderr=sp.STDOUT, cwd=outdir_category)

    return group


if __name__ == '__main__':
    args = parser.parse_args()

    with open('regionalgruppen.txt') as f:
        regionalgruppen = [l.strip() for l in f]

    with open('bundeslaender.txt') as f:
        bundeslaender = [l.strip() for l in f]

    with open('laender.txt') as f:
        laender = [l.strip() for l in f]

    with open('fachgruppen.txt') as f:
        fachgruppen = [l.strip() for l in f]

    all_categories = [
        regionalgruppen,
        bundeslaender,
        laender,
        fachgruppen,
    ]

    subfolders = [
        'regionalgruppen',
        'bundeslaender',
        'laender',
        'fachgruppen',
    ]

    os.makedirs(OUTDIR, exist_ok=True)

    for ncat in range(len(all_categories)):
        groups = all_categories[ncat]

        outdir_cat = os.path.join(OUTDIR, subfolders[ncat])
        os.makedirs(outdir_cat, exist_ok=True)

        if args.n_parallel == 1:
            for group in groups:
                print('Building', group)
                build_all(group, outdir_cat)
                print('Done')
        else:
            with ThreadPoolExecutor(args.n_parallel) as pool:
                jobs = [pool.submit(build_all, outdir_cat) for group in groups]
                for job in as_completed(jobs):
                    print(job.result())
