from pathlib import Path
import shutil
from create_logos import sanitize_name

OUTDIR = Path('s4f_all_logos').absolute()


categories = {
    'laender': "Länder",
    'bundeslaender': "Bundesländer",
    'fachgruppen': "Fachgruppen",
    'regionalgruppen': "Regionalgruppen",
}

edit_url = 'https://github.com/s4f-dortmund/regionalgruppen_logos/edit/main'



if __name__ == "__main__":

    groups = {}
    for category in categories:
        with open(f'{category}.txt') as f:
            groups[category] = f.read().splitlines()


    template = Path("./template.html").read_text()
    outputpath = Path("build")
    outputpath.mkdir(exist_ok=True)

    shutil.copy2(OUTDIR / "regionalgruppen/s4f_logos_dortmund/s4f_banner_dortmund.svg", outputpath)
    group_lines = []
    edit_lines = []

    for category, subgroups in groups.items():
        category_label = categories[category]

        edit_lines.append(f'  <li><a target="_blank" href="{edit_url}/{category}.txt">')
        edit_lines.append(f'    {category_label}: <code>{category}.txt</code>')
        edit_lines.append(f'  </a></li>')

        group_lines.append(f"<h4>{category_label}</h4>")
        group_lines.append("<ul>")
        for group in subgroups:
            name = sanitize_name(group)
            group_lines.append(f'<li><a href="s4f_logos_{name}.zip">{group}</a></li>')
        group_lines.append("</ul>")

    groups = "\n".join(group_lines)
    editing = "\n".join(edit_lines)

    with (outputpath / "index.html").open("w") as f:
        f.write(template.replace("{% content %}", groups).replace("{% editing %}", editing))
