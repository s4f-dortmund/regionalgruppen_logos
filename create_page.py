from pathlib import Path
import shutil
from create_logos import sanitize_name

OUTDIR = Path('s4f_all_logos').absolute()



if __name__ == "__main__":
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

    template = Path("./template.html").read_text()
    outputpath = Path("build")
    outputpath.mkdir(exist_ok=True)

    shutil.copy2(OUTDIR / "regionalgruppen/s4f_logos_dortmund/s4f_banner_dortmund.svg", outputpath)
    
    lines = []

    for ncat in range(len(all_categories)):
        groups = all_categories[ncat]

        for group in groups:
            name = sanitize_name(group)
            lines.append(f'<li><a href="s4f_logos_{name}.zip">{group}</a></li>')

        content = "<ul>\n" + "\n".join(lines) + "\n</ul>\n"

        with (outputpath / "index.html").open("w") as f:
            f.write(template.replace("{% content %}", content))
