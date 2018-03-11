import os

from powerline.lib.unicode import out_u
from powerline.theme import requires_segment_info
from powerline.segments import Segment, with_docstring

cwd_icons = {
    'root': '/',
    'home': '~',
    'ellipsis': '...',
    'separator': '/'
}

@requires_segment_info
class CwdPathSegment(Segment):
    def get_icon(self, icons, icon):
        if icons is not None and icon in icons:
            return out_u(icons[icon])
        return out_u(cwd_icons[icon])

    def get_shortend_path(self, pl, segment_info, icons, shorten_home):
        try:
            path = out_u(segment_info['getcwd']())
        except OSError as e:
            if e.errno == 2:
                # user most porbably deleted the directory
                # this happens when removing files from Mercurial repos for example
                pl.warn('Current directory not found')
                return '[not found]'
            else:
                raise
        if shorten_home:
            home = segment_info['home']
            if home:
                home = out_u(home)
                if path.startswith(home):
                    icn = self.get_icon(icons, 'home')
                    path = icn + path[len(home):]
        return path

    def __call__(self, pl, segment_info,
                dir_shorten_len=None,
                dir_limit_depth=None,
                icons=None,
                shorten_home=True):
        cwd = self.get_shortend_path(pl, segment_info, icons, shorten_home)
        cwd_split = cwd.split(os.sep)
        cwd_split_len = len(cwd_split)
        # Shorten the direcotry names
        cwd = [i[0:dir_shorten_len] if dir_shorten_len and i else i for i in cwd_split[:-1]] + [cwd_split[-1]]
        if dir_limit_depth and cwd_split_len > dir_limit_depth + 1:
            del(cwd[0:-dir_limit_depth])
            cwd.insert(0, self.get_icon(icons, 'ellipsis'))
        if not cwd[0]:
            cwd[0] = self.get_icon(icons, 'root')
        ret = []
        for part in cwd:
            if not part:
                continue
            part += self.get_icon(icons, 'separator')
            ret.append({
                'contents': part,
                'highlight_groups': ['cwd']
            })
        ret[-1]['highlight_groups'] = ['cwd:current_folder', 'cwd']
        ret[-1]['contents'] = ret[-1]['contents'][:-1]
        return ret

cwdpath = with_docstring(CwdPathSegment(),
'''Return the current working directory.

Returns a segment list to create a breadcrumb-like effect.

:param int dir_shorten_len:
	shorten parent directory names to this length (e.g.
	:file:`/long/path/to/powerline` → :file:`/l/p/t/powerline`)
:param int dir_limit_depth:
	limit directory depth to this number (e.g.
	:file:`/long/path/to/powerline` → :file:`⋯/to/powerline`)
:param dict icons:
    dict for overriding default icons (e.g.
    ``{'root': u'/'}``)
:param bool shorten_home:
	Shorten home directory to ``~``.

Highlight groups used: ``cwd:current_folder`` or ``cwd``. It is recommended to define all highlight groups.
''')
