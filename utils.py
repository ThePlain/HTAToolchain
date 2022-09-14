import bpy
import bpy.types

import pathlib
import xml.etree.ElementTree as xml

from . import consts


def load_texture_mapping(operator: bpy.types.Operator, allowed: bool) -> dict[str, str]:
    if not allowed:
        return {}

    if not consts.preferences.path:
        return {}

    game = pathlib.Path(consts.preferences.path)
    path = game / 'data/models/modeltextures.xml'

    if not path.exists():
        operator.report({'ERROR'}, f'Texture mapping file "{path}" not found!')
        return {}

    with path.open('r', encoding='cp1251') as stream:
        file = xml.parse(stream)

    mapping = dict()

    root = file.getroot()
    for map in root:
        key = map.get('name')
        val = map.get('path')

        value: pathlib.Path = game / val

        if not value.exists():
            operator.report({'ERROR'}, f'Texture not found: {value}')
            continue

        mapping[key.lower()] = game / val

    operator.report({'INFO'}, f'Loaded mapping for {len(mapping)} texture(s).')

    return mapping