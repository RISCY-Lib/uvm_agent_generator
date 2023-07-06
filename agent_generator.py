#!/usr/bin/env python3

#####################################################################################
# Tool to Generate UVM Agent Skeleton Code
# Copyright (C) 2023  RISCY-Lib Contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#####################################################################################

from __future__ import annotations

from argparse import ArgumentParser

import os
from pathlib import Path

import jinja2
import yaml

from dataclasses import dataclass, field

@dataclass
class AgentConfig:
  name: str
  ports: dict[str, str] = field(default_factory=dict)
  copyright: str = ""


@dataclass
class AgentFileConfig(AgentConfig):
  filename: str = ""

  @classmethod
  def from_agent_config(cls, cfg: AgentConfig, filename: str) -> AgentFileConfig:
    return cls(name=cfg.name, filename=filename, ports=cfg.ports, copyright=cfg.copyright)


def create_agent(cfg: AgentConfig, dst: str) -> None:
  """Create an agent using the specified agent config and place it in the specified location

  Args:
      cfg (AgentConfig): The config to use for generating the agent template
      dst (str): The path to where the skeleton should be placed
  """
  if not Path(dst).exists():
    Path(dst).mkdir(parents=True)

  jenv = jinja2.Environment(loader=jinja2.FileSystemLoader("agent_templates/"))

  for dir, _, files in os.walk("agent_templates/"):
    _, template_subdir = dir.split("agent_templates/")
    dest_path = os.path.join(dst, template_subdir)

    if not Path(dest_path).exists():
      Path(dest_path).mkdir(parents=True)

    for file in files:
      # Check this is a file to use
      fname, extension = os.path.splitext(file)
      fname_base, _ = os.path.splitext(fname)

      if "_base." in file:
        continue

      if extension != ".jinja":
        continue

      # Create the AgentFile
      agent = AgentFileConfig.from_agent_config(cfg, fname_base)
      template = jenv.get_template(os.path.join(template_subdir, file))
      rendered_template = template.render(agent=agent)

      dest_filename = f"{cfg.name}{fname}"
      dest_filepath = os.path.join(dest_path, dest_filename)
      with open(dest_filepath, "w") as fout:
        fout.write(rendered_template)


#####################################################################################
# Main Script
#####################################################################################
def main() -> None:
  parser = ArgumentParser("agent_generator", description="UVM Agent Generator")
  parser.add_argument("agent_name", type=str, help="The name of the agent skeleton to generate")
  parser.add_argument("--dst", "-d", type=str, default=None, help="The destination directory for the agent")

  args = parser.parse_args()

  agent_cfg = AgentConfig(name=args.agent_name)

  if args.dst is None:
    args.dst = f"./{args.agent_name}_agent"

  create_agent(agent_cfg, args.dst)


if __name__ == "__main__":
  main()
