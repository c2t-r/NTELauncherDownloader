import os
import shutil
import xml.etree.ElementTree as et
from configparser import ConfigParser
from pathlib import Path

import httpx

INSTALLE_LOCATION = Path("../Launcher")
VERSION_API = "https://ntecdn1.perfectworld.com/hd/publish_PC/launcher/Version.ini"


def getAttributes(node: et.Element | None) -> dict[str, str]:
  if node is None:
    raise ValueError("Node not found")
  return node.attrib


def main() -> None:
  print("Hello from ntelauncher!")

  response = httpx.get(VERSION_API)
  parser = ConfigParser()
  parser.read_string(response.text)

  version = parser["VERSION"]["Version"]
  build = parser["VERSION"]["Build"]
  url = parser["VERSION"]["FileListURL"]
  print(version, build, url)

  response = httpx.get(url)
  root = et.fromstring(response.text)
  print(root)

  baseUrl = getAttributes(root.find("Url"))["BaseUrl"]
  version = getAttributes(root.find("ProductVersion"))["Version"]
  paths = root.findall("File")
  i = 1
  for element in paths:
    attrb = getAttributes(element)
    path = attrb["Path"]
    url = f"{baseUrl}/{version}{path}.zip"

    # if path.startswith("/obs/") or path.startswith("/qml/"):
    #  print(f"[{i}/{len(paths)}] Skipping {path}")
    #  i += 1
    #  continue

    response = httpx.get(url)
    location = INSTALLE_LOCATION / path[1:]
    location.parent.mkdir(parents=True, exist_ok=True)

    tempFile = Path("temp.zip")
    tempFile.write_bytes(response.content)
    shutil.unpack_archive(tempFile, location.parent)
    os.remove(tempFile)

    print(f"[{i}/{len(paths)}] Downloaded {path}")
    i += 1


if __name__ == "__main__":
  main()
