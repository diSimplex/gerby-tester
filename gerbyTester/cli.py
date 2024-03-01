
import argparse
import os
import random
import sys
import tomllib
import yaml

# see: https://requests.readthedocs.io/en/latest/
import requests

# see: https://lxml.de/lxmlhtml.html#html-diff
# see: https://html5lib.readthedocs.io/en/latest/
# see: https://github.com/html5lib/html5lib-python
# see: https://xmldiff.readthedocs.io/en/stable/
# see: https://github.com/Shoobx/xmldiff

def tomlUsage(aKey) :
  print(f"The gerbyTest TOML file MUST define the key [{aKey}]")
  sys.exit(1)

def loadConfig(cmdArgs) :
  # Load the TOML configuration values
  config = {
    'verbose' : False,
    'quiet'   : False
  }
  tConfig = {}
  aConfigPath = cmdArgs['configPath']
  try:
    with open(aConfigPath, 'rb') as tomlFile :
      tConfig = tomllib.load(tomlFile)
  except Exception as err :
    print(f"Could not load configuration from [{aConfigPath}]")
    print(repr(err))

  # merge in the TOML config
  for aKey, aValue in tConfig.items() :
    config[aKey] = aValue

  if cmdArgs['verbose'] : config['verbose'] = cmdArgs['verbose']
  if cmdArgs['quiet']   : config['quiet']   = cmdArgs['quiet']

  if 'local_url'     not in config : tomlUsage('local_url')
  if 'external_url'  not in config : tomlUsage('external_url')
  if 'tags_path'     not in config : tomlUsage('tags_path')
  if 'percent_cover' not in config : tomlUsage('percent_cover')

  config['tags_path'] = os.path.abspath(
    os.path.expanduser(config['tags_path'])
  )

  # report the configuration if verbose
  if config['verbose'] :
    print(f"Loaded config from: [{aConfigPath}]\n")
    print("----- command line arguments -----")
    print(yaml.dump(cmdArgs))
    print("---------- configuration ---------")
    print(yaml.dump(config))
    print("\n----------------------------------")

  return config

def loadTags(tagsPath) :
  try :
    with open(tagsPath) as tagsFile :
      tagsLines = tagsFile.readlines()
  except Exception as err :
    print(f"Could not load the tags from: [{tagsPath}]")
    print(repr(err))
    sys.exit(2)

  tags = []
  for aTagLine in tagsLines :
    if aTagLine.startswith('#') : continue
    aTag, _ = aTagLine.split(',')
    tags.append(aTag)

  return tags

def cli() :
  # setup the command line arguments
  parser = argparse.ArgumentParser()
  parser.add_argument(
    'configPath',
    help="The path to a TOML file describing what to test."
  )
  parser.add_argument(
    '-v', '--verbose', action='store_true', default=False,
    help="Be verbose [False]"
  )
  parser.add_argument(
    '-q', '--quiet', action='store_true', default=False,
    help="Be quiet [False]"
  )

  # load the TOML configuration file
  config = loadConfig(vars(parser.parse_args()))

  theTags       = loadTags(config['tags_path'])
  externalURL   = config['external_url']
  localURL      = config['local_url']
  numberOfTests = int(config['percent_cover'] * len(theTags) / 100)

  print(f"Testing {numberOfTests} tags out of {len(theTags)} ({config['percent_cover']}%)")
  for i in range(numberOfTests) :
    aTagToTest = random.choice(theTags)
    aTagPath = f"/tag/{aTagToTest}"
    print(f"Test[{i}]: Testing tag {aTagToTest} ({aTagPath})")

    response = requests.get(externalURL+aTagPath, stream=False)
    print(response.status_code, response.reason)
    print("--------------------------------------")
    print(response.content.decode('utf-8'))
    print("--------------------------------------")
