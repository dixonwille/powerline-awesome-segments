from powerline.lib.unicode import out_u
from powerline.theme import requires_segment_info
from powerline.segments import Segment, with_docstring

import os
import pygit2


staged_mask = (pygit2.GIT_STATUS_INDEX_NEW |
              pygit2.GIT_STATUS_INDEX_MODIFIED |
              pygit2.GIT_STATUS_INDEX_DELETED)

modified_mask = (pygit2.GIT_STATUS_WT_NEW |
              pygit2.GIT_STATUS_WT_MODIFIED |
              pygit2.GIT_STATUS_WT_DELETED)

git_repos = {}

git_icons = {
    'branch': '',
    'behind': '↓',
    'ahead': '↑',
    'staged': '●',
    'modified': '✚',
    'stashed':  '⚑',
    'conflict': '✖',
    'tag': '★'
}

class Statuses(object):
    def __init__(self, repo):
        self.repo = repo
        self.update()

    def update(self):
        self._zero()
        self._update_statuses()
        self._update_stashed()
        self._update_branch()
        self._update_ahead_behind()
        self._update_tags()

    def _update_statuses(self):
        for f, status in self.repo.status().items():
            if status & modified_mask:
                self.modified += 1
            if status & staged_mask:
                self.staged += 1
            if status & pygit2.GIT_STATUS_CONFLICTED:
                self.conflict += 1

    def _update_branch(self):
        if not self.repo.head_is_unborn:
            if self.repo.head_is_detached:
                self.branch_ref = self.repo.head.target
            else:
                branch = self.repo.branches.get(self.repo.head.name[len('refs/heads/'):])
                self.branch = branch.branch_name
                self.branch_ref = self.repo.references.get(self.repo.head.name).target
                try:
                    self.remote_ref = self.repo.references.get(branch.upstream_name).target
                except KeyError:
                    self.remote_ref = None

    def _update_stashed(self):
        stash_file_path = os.path.join(self.repo.path, 'logs/refs/stash')
        if os.path.isfile(stash_file_path):
            f = open(stash_file_path, 'r')
            self.stashed = len(f.readlines())
            f.close()

    # Should be called after _update_branch
    def _update_ahead_behind(self):
        if self.remote_ref is not None:
            ahead, behind = self.repo.ahead_behind(self.branch_ref, self.remote_ref)
            self.ahead = ahead
            self.behind = behind

    # Should be called after _update_branch
    def _update_tags(self):
        if self.branch_ref is not None:
            all_tags = {}
            for ref in self.repo.listall_references():
                if ref.startswith('refs/tags/'):
                    target = self.repo.references.get(ref).peel(pygit2.GIT_OBJ_COMMIT).id
                    if target in all_tags:
                        all_tags[target].append(ref[len('refs/tags/'):])
                    else:
                        all_tags[target] = [ref[len('refs/tags/'):]]
            if self.branch_ref in all_tags:
                self.tags = all_tags[self.branch_ref]

    def _zero(self):
        self.branch = None
        self.branch_ref = None
        self.remote_ref = None
        self.modified = 0
        self.staged = 0
        self.conflict = 0
        self.stashed = 0
        self.ahead = 0
        self.behind = 0
        self.tags = []

@requires_segment_info
class GitSegment(Segment):
    def get_icon(self, icons, icon):
        if icons is not None and icon in icons:
            return out_u(icons[icon])
        return out_u(git_icons[icon])

    def build_segments(self, statuses, icons):
        unborn = not statuses.branch and not statuses.branch_ref and not statuses.remote_ref

        if unborn:
            segments = [{'contents': out_u('[no-commits]'), 'highlight_groups': ['git_head_detached', 'git']}]
        else:
            detached = not statuses.branch and statuses.branch_ref
            dirty = statuses.modified > 0 and statuses.staged > 0

            if detached:
                branch_group = 'git_head_detached'
            elif dirty:
                branch_group = 'git_head_dirty'
            else:
                branch_group = 'git_head_clean'

            branch_disp = statuses.branch if statuses.branch else str(statuses.branch_ref)[0:7]
            segments = [{'contents': out_u('%s %s' % (self.get_icon(icons, 'branch'), statuses.branch)), 'highlight_groups': [branch_group, 'git_branch', 'git']}]

        if statuses.ahead > 0:
            segments.append({'contents': out_u(' %s %s' % (self.get_icon(icons, 'ahead'), statuses.ahead)), 'highlight_groups': ['git_ahead', 'git']})
        if statuses.behind > 0:
            segments.append({'contents': out_u(' %s %s' % (self.get_icon(icons, 'behind'), statuses.behind)), 'highlight_groups': ['git_behind', 'git']})
        if statuses.conflict > 0:
            segments.append({'contents': out_u(' %s %s' % (self.get_icon(icons, 'conflict'), statuses.conflict)), 'highlight_groups': ['git_conflict', 'git']})
        if statuses.stashed > 0:
            segments.append({'contents': out_u(' %s %s' % (self.get_icon(icons, 'stashed'), statuses.stashed)), 'highlight_groups': ['git_stashed', 'git']})
        if statuses.modified > 0:
            segments.append({'contents': out_u(' %s %s' % (self.get_icon(icons, 'modified'), statuses.modified)), 'highlight_groups': ['git_modified', 'git']})
        if statuses.staged > 0:
            segments.append({'contents': out_u(' %s %s' % (self.get_icon(icons, 'staged'), statuses.staged)), 'highlight_groups': ['git_staged', 'git']})
        if len(statuses.tags) > 0:
            for tag in statuses.tags:
                segments.append({'contents': out_u(' %s %s' % (self.get_icon(icons, 'tag'), tag)), 'highlight_groups': ['git_tag', 'git']})
        return segments
    def __call__(self, pl, segment_info, icons=None):
        repo = None
        try:
            repo_path = pygit2.discover_repository(segment_info['getcwd']())
            repo = pygit2.Repository(repo_path)
        except KeyError:
            return

        # Doing this to reserve as much memory usage as possible
        if not repo.path in git_repos:
            statuses = Statuses(repo)
            git_repos[repo.path] = statuses
        else:
            git_repos[repo.path].update()

        return self.build_segments(git_repos[repo.path], icons)

git = with_docstring(GitSegment(),
'''Return information about a git repository
''')
