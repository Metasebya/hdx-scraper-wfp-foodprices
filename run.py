#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Top level script. Calls other functions that generate datasets that this script then creates in HDX.

"""
import logging
from os.path import join, expanduser

from hdx.hdx_configuration import Configuration
from hdx.utilities.downloader import Download
from hdx.utilities.path import temp_dir

from wfpfood import generate_dataset_and_showcase, get_countriesdata, generate_joint_dataset_and_showcase, generate_resource_view


# Remove 2 lines below if you don't want emails when there are errors
#from hdx.facades import logging_kwargs
#logging_kwargs['smtp_config_yaml'] = join('config', 'smtp_configuration.yml')

from hdx.facades.simple import facade

logger = logging.getLogger(__name__)

lookup = 'hdx-scraper-wfp-foodprices'


def main():
    """Generate dataset and create it in HDX"""

    with temp_dir('wfp-foodprices') as folder:
        with Download() as downloader:
            config = Configuration.read()

            countries_url = config['countries_url']
            wfpfood_url = config['wfpfood_url']
            country_correspondence = config['country_correspondence']
            shortcuts = config['shortcuts']

            countriesdata = get_countriesdata(countries_url, downloader, country_correspondence)
            logger.info('Number of datasets to upload: %d' % len(countriesdata))

            for countrydata in countriesdata:
                dataset, showcase = generate_dataset_and_showcase(wfpfood_url, downloader, folder, countrydata, shortcuts)
                if dataset:
                    dataset.update_from_yaml()
                    dataset['notes'] = dataset['notes'] % 'Food Prices data for %s. Food prices data comes from the World Food Programme and covers' % countrydata['name']
                    dataset.create_in_hdx()
                    showcase.create_in_hdx()
                    showcase.add_dataset(dataset)
                    resource_view = generate_resource_view(dataset)
                    resource_view.create_in_hdx()

            logger.info('Individual country datasets finished.')

            generate_joint_dataset_and_showcase(wfpfood_url, downloader, folder, countriesdata)

    logger.info('Done')


if __name__ == '__main__':
    facade(main, user_agent_config_yaml=join(expanduser('~'), '.useragents.yml'), user_agent_lookup=lookup, project_config_yaml=join('config', 'project_configuration.yml'))


