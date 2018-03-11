from powerline.lib.unicode import out_u
from powerline.theme import requires_segment_info
from powerline.segments import Segment, with_docstring
from powerline.lib.shell import readlines, which

go_icons = {
    'gopher': ''
}

@requires_segment_info
class GoSegment(Segment):
    def __init__(self):
        if not which('go'):
            raise OSError('go executable is not available')

    def get_icon(self, icons, icon):
        if icons is not None and icon in icons:
            return out_u(icons[icon])
        return out_u(go_icons[icon])

    def _gocmd(self, segment_info, *args):
        return readlines(('go',) + args, segment_info['getcwd']())

    def get_go_path(self, segment_info):
        return next(iter(self._gocmd(segment_info, 'env', 'GOPATH')))

    def get_go_version(self, segment_info):
        version_line = next(iter(self._gocmd(segment_info, 'version')))
        # Expects `go version go##### os/arch`
        return version_line.split(' ')[2][len('go'):]

    def __call__(self, pl, segment_info, icons=None):
        cwd = segment_info['getcwd']()
        gopath = self.get_go_path(segment_info)
        if not cwd.startswith(gopath):
            return None
        version = self.get_go_version(segment_info)
        return [{'contents': out_u('%s %s' % (self.get_icon(icons, 'gopher'), version)), 'highlight_groups': ['go']}]

go = with_docstring(GoSegment(),
'''Return information about the go workspace
''')
