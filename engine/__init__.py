from pbr import version

__version_info = version.VersionInfo('engine')
__version__ = __version_info.cached_version_string()
