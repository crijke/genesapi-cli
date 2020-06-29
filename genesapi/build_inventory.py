"""
build schema out of cubes


schema layout:

- statistic:
  - measure:
    - dimension:
      - value

{
  "12111": {
    "title_de": "Zensus 2011",
    "title_en": "2011 census",
    "description_de": "...",
    "valid_from": "2011-05-09T00:00:00",
    "periodicity": "EINMALIG",
    "name": "12111",
    "measures": {
      "BEVZ20": {
        "name": "BEVZ20",
        "title_de": "Bevölkerung",
        "measure_type": "W-MM",
        "atemporal": true,
        "meta_variable": false,
        "valid_from": "1950-01-01T00:00:00",
        "summable": true,
        "title_en": "Bevölkerung",
        "definition_de": "...",
        "values": [],
        "dimensions": {
          "ALTX20": {
            "name": "ALTX20",
            "title_de": "Altersgruppen (unter 3 bis 75 u. m.)",
            "measure_type": "K-SACH-MM",
            "atemporal": false,
            "meta_variable": false,
            "valid_from": "1950-01-01T00:00:00",
            "GLIED_TYP": "DAVON",
            "STD_SORT": "FS",
            "summable": false,
            "title_en": "Altersgruppen (unter 3 bis 75 u. m.)",
            "definition_de": "...",
            "values": [
              {
                "title_de": "unter 3 Jahre",
                "title_en": "unter 3 Jahre",
                "name": "ALT000B03",
                "dimension_name": "ALTX20",
                "value_id": "dd25a6d4cf0a23fd750fb618196b4ad351badbbf",
                "key": "ALT000B03"
              },
            ...

"""

import json
import logging
import sys

from genesapi.storage import Storage, CubeSchema
from genesapi.util import cube_serializer

logger = logging.getLogger(__name__)


def _dumper(value):
    if isinstance(value, set):
        return list(value)
    return cube_serializer(value)


def main(args):
    storage = Storage(args.directory)
    inventory = {}
    logger.info('building inventory')
    for cube in storage._cubes:
        try:
            logger.info('Loading `%s` ...' % cube.name)
            statistic_info = cube.metadata['statistic']
            statistic_key = statistic_info['name']
            cube_schema = CubeSchema(cube)
            measures = cube_schema.measures
            dimensions = cube_schema.dimensions
            region_levels = cube_schema.region_levels
            if len(region_levels) != 1:
                raise ValueError('legions_levels does not have length 1')
            level = next(iter(region_levels))
            if statistic_key in inventory:
                measures_inventory = inventory[statistic_key]['measures']
            else:
                inventory[statistic_key] = {'statistic': statistic_key}
                inventory[statistic_key]['measures'] = {}
                measures_inventory = inventory[statistic_key]['measures']
            for measure_key in measures.keys():
                if measure_key not in measures_inventory:
                    measures_inventory[measure_key] = {'0': [], '1': [], '2': [], '3': [],  '4': []}
                current_measure_inventory = measures_inventory[measure_key]
                current_measure_inventory[str(level)].append(list(dimensions.keys()))
        except KeyError:
            logger.warn('No metadata for cube `%s`' % cube.name)
    sys.stdout.write(json.dumps(inventory, default=_dumper))
