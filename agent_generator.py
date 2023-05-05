from __future__ import annotations

from argparse import ArgumentParser

import os
from pathlib import Path

from jinja2 import Template, Environment, FileSystemLoader
import yaml

def main() -> None:
  parser = ArgumentParser("agent_generator", description="UVM Agent Generator")
  parser.add_argument("input_file", type=str, help="The input YAML file which creates an agent")

  args = parser.parse_args()

  if not Path(args.input_file).exists():
    raise FileNotFoundError(f"input_file ({args.input_file}) does not exist")

  with open(args.input_file, "r") as fin:
    agent = yaml.safe_load(fin)

  print(agent)

  if not Path(agent['dst_path']).exists():
    Path(agent['dst_path']).mkdir(parents=True)

  env = Environment(loader=FileSystemLoader("agent_templates/"))

  for dir, _, files in os.walk("agent_templates/"):
    _, template_subdir = dir.split("agent_templates/")
    dest_path = os.path.join(agent['dst_path'], template_subdir)
    if not Path(dest_path).exists():
      Path(dest_path).mkdir(parents=True)

    for file in files:
      if "_base." in file:
        continue

      fname, extension = os.path.splitext(file)

      if extension != ".jinja":
        continue

      agent['file'] = os.path.splitext(fname)[0]
      template = env.get_template(os.path.join(template_subdir, file))
      rendered_template = template.render(agent=agent)

      dest_filename = f"{agent['name']}{fname}"
      dest_filepath = os.path.join(dest_path, dest_filename)
      with open(dest_filepath, 'w') as fout:
        fout.write(rendered_template)

if __name__ == "__main__":
  main()
