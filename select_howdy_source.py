#!/usr/bin/python3

import subprocess
import shutil
import string
from typing import Dict, List, Any

# The Howdy config file that we will butcher
howdyConfig = "/usr/lib/security/howdy/config.ini"

# A list of video sources
# Sources are discovered by `v4l2-ctl --list-devices`
# The first device found in this list is used. If none is found, Howdy will be disabled
videoSources = [{"ident": "BRIO", "devIdx": 2}, {"ident": "IntegratedXX", "devIdx": 0}]

def findPreferredSource(availableSources, preferredSources):
  """
  Iterates over the list of preferred sources and tries to find a matching block in the available sources list.
  [Return] - the found source block or None if nothing found
  """

  foundSource = None

  idx = 0
  while foundSource == None and idx < len(preferredSources):
    preferredSource = preferredSources[idx]

    innerIdx = 0
    while foundSource == None and innerIdx < len(availableSources):
      if (preferredSource["ident"] in availableSources[innerIdx]["ident"]):
        foundSource = {
            "preferredSource": preferredSource,
            "availableSource": availableSources[innerIdx]
          }
      else:
        innerIdx += 1

    idx += 1
    

  return foundSource


def parseVideoSources(lines: List[str]) -> List[Any]:
  parsed = []
  currentDevice = None
  for idx in range(len(lines)):
    line = lines[idx]
    if len(line.strip()) > 0:
      if not line[0] in string.whitespace and line.strip().endswith(":"):
        if currentDevice != None:
          parsed.append(currentDevice)
          currentDevice = None

        currentDevice = {"ident": line.strip(), "devices": []}

      elif line[0] in string.whitespace and line.strip().startswith("/dev"):
        currentDevice["devices"].append(line.strip())

    else:
      # block is finished
       if currentDevice != None:
        parsed.append(currentDevice)
        currentDevice = None

  return parsed


def applyChanges(line: str, changes: Dict[str, str]) -> str:
  newLine = line
  for key in changes:
    value = changes[key]
    if key in line:
      if not value in line:
        newLine = f"{key} = {value}"

  return newLine


def modifyHowdyConfig(configPath: str, changes: Dict[str, str]) -> None:
  fileModified = False

  with open(configPath) as howdy:
    howdyIni = howdy.read().splitlines()

  for idx in range(len(howdyIni)):
    line = howdyIni[idx]
    newLine = applyChanges(line, changes)
    if newLine != line:
      howdyIni[idx] = newLine
      fileModified = True

  if fileModified:
    # backup file
    shutil.copyfile(configPath, f"{configPath}.bak")
    with open(configPath, "w") as output:
      output.write("\n".join(howdyIni))

### MAIN

def main():
  result = subprocess.run(["v4l2-ctl", "--list-devices"], capture_output=True, text=True)
  parsed = parseVideoSources(result.stdout.splitlines())
  source = findPreferredSource(parsed, videoSources)

  if source != None:
    # Found a video source that we can use
    device = source["availableSource"]["devices"][source["preferredSource"]["devIdx"]]
    print(f"device found is {device}")
    modifyHowdyConfig(howdyConfig, {"device_path": device, "disabled": "false"})

  else:
    # found no video source, ensure Howdy is disabled
    print("disable howdy")
    modifyHowdyConfig(howdyConfig, {"disabled": "true"})


main()
