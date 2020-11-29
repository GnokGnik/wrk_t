import os
import subprocess
import argparse

import configparser

container_mapping = {

    
}

class OdooSwitcher:
    def __init__(self, config):
        self.config_file = config
        
        self.oca = None
        self.custom = None
        self.community = None
        self.enterprise = None

        self._load_config()

    def _load_config(self):
        self.switcher_config = configparser.ConfigParser()
        self.switcher_config.read('config.cfg')
        
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)
        
        app_configuration = self.config['options']

        self.odoo_version = app_configuration['odoo_version']
        
        self.version_options = self.switcher_config[self.odoo_version]

        self.oca = app_configuration.get('oca',None)
        self.custom = app_configuration.get('custom', None)
        self.odoo_config = app_configuration['config']
         
        if app_configuration.get('include_enterprise', False):
            self.enterprise = self.version_options['enterprise']
        
        if app_configuration.get('include_community', False):
            self.community = self.version_options['community']

    def update_config(self):
        docker_path = self.version_options['docker_path']

        subprocess.run(['ln', '-sfn', self.odoo_config, os.path.join(docker_path, 'config')],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        subprocess.run(['ln', '-sfn', self.oca, os.path.join(docker_path, 'addons_external')], 
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        subprocess.run(['ln', '-sfn', self.custom, os.path.join(docker_path, 'custom')], 
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if self.enterprise:
            subprocess.run(['ln', '-sfn', self.enterprise, os.path.join(docker_path, 'odoo-enterprise')], 
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
            subprocess.run(['rm', os.path.join(docker_path, 'odoo-enterprise')])
        
        if self.community:
            pass


    def run(self):
        print("Reading {0}".format(self.config_file))
        self.update_config()
        print("Updating done[OK].")

parser = argparse.ArgumentParser("Odoo Application Switcher")
parser.add_argument("-config", action="store", dest="config", required=True, help="Application's switcher config file.")
args = parser.parse_args()

if __name__ == '__main__':
    odoo_config = OdooSwitcher(args.config)
    odoo_config.run()