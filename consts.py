
TEXTURE_TYPES: list[str] = [
    'DIFFUSE',
    'BUMP',
    'LIGHTMAP',
    'CUBE',
    'DETAIL',
]


TEXTURE_ENUM: list[tuple[str, str, str]] = [
    ('UNKNOWN',  'Unknown texture slot', 'HTA shaders not support this sampler.'),
    ('DIFFUSE',  'DIFFUSE_MAP_0',        'DIFFUSE_MAP_0 shader sampler.'),
    ('BUMP',     'BUMP_MAP_0',           'BUMP_MAP_0 shader sampler.'),
    ('LIGHTMAP', 'LIGHT_MAP_0',          'LIGHT_MAP_0 shader sampler.'),
    ('CUBE',     'CUBE_MAP_0',           'CUBE_MAP_0 shader sampler.'),
    ('DETAIL',   'DETAIL_MAP_0',         'DETAIL_MAP_0 shader sampler.'),
]
