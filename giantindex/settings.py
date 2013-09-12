__author__ = 'Michael Craft <mcraft@peak15.org>'

import os
import ConfigParser

def get():
    """
    Return a dict of settings and their values
    from attempting to load a settings file in this order:
        ./giantindex.cfg
        ~/.giantindex.cfg
        /etc/giantindex.cfg

    Or None if not found.
    """

    # Locate configuration file
    cfg_name = 'giantindex.cfg'
    if os.access(cfg_name, os.R_OK):
        cfgFile = cfg_name
    elif os.access(os.path.expanduser('~/.' + cfg_name), os.R_OK):
        cfgFile = os.path.expanduser('~/.' + cfg_name)
    elif os.access(os.path.join('/etc/', cfg_name), os.R_OK):
        cfgFile = os.path.join('/etc/', cfg_name)
    else:
        #print('Could not load ./giantindex.cfg, ~/.giantindex.cfg, or /etc/giantindex.cfg')
        return None

    config = ConfigParser.RawConfigParser()
    config.read(cfgFile)

    settings = {}

    for key in ('host', 'user', 'passwd', 'db'):
        settings[key] = config.get('database', key)
    for key in ('include', 'exclude'):
        settings[key] = config.get('indexer', key)

    return settings

class ConfigurationNotFoundException(Exception):
    def __str__(self):
        return "Could not load configuration from ./giantindex.cfg, ~/.giantindex.cfg, or /etc/giantindex.cfg."