#!/usr/bin/env python3
"""
Takes all your GitHub pages repos and builds their static sites.
"""

import os
import os.path
import shutil
from subprocess import check_call, check_output

PATH = 'https://github.com/{username}/{reponame}'


class GhpRepo(object):
    """A class representing a git repository with GitHub pages enabled.

    Has a remote URL, a local directory, and a "build" directory, where the
    actual generated site will be placed. Also, most repositories are on branch
    gh-pages, but some (like *.github.io) are on master, so this accepts a
    branch argument.

    This class allows you to clone, build, update, and rebuild a repo fairly
    easily.  Of course, it just shells out to git and jekyll.

    """

    def __init__(self, url, local, output, branch='gh-pages'):
        """Create the class instance.

        This doesn't necessarily clone the repo or build it - in fact, the repo
        may already exist locally.

        """
        self.url = url
        self.local = local
        self.output = output
        self.branch = branch

    def checkout(self):
        """Check out the repository."""
        check_call(['git', 'clone', '-b', self.branch, self.url, self.local])
        self.should_build = not os.path.exists(os.path.join(self.local, '.nojekyll'))

    def current_commit(self):
        """Return the SHA of the current commit."""
        os.chdir(self.local)
        return check_output(['git', 'rev-parse', 'HEAD'])

    def pull(self):
        """Pull from the default remote tracking branch, hopefully."""
        os.chdir(self.local)
        check_call(['git', 'pull'])
        self.should_build = not os.path.exists(os.path.join(self.local, '.nojekyll'))

    def build(self):
        """Run the build command (jekyll) or just copy files if .nojekyll exists."""
        os.chdir(self.local)
        if self.should_build:
            check_call(['jekyll', 'build', '-d', self.output])
        else:
            if os.path.exists(self.output):
                shutil.rmtree(self.output)
            ignore = shutil.ignore_patterns(
                # may have to include lots of stuff in here
                '.git',
                '.gitignore',
                '.nojekyll'
            )
            shutil.copytree(self.local, self.output, ignore=ignore)

    def update_and_build(self):
        """Pull, and if the repo has changed, rebuild."""
        old_revision = self.current_commit()
        self.pull()
        if self.current_commit() != old_revision:
            self.build()


class GhpBuilder(object):
    """This class represents a collection of GitHub pages repositories to deploy.

    Construct an instance of this object to build your complete GitHub pages
    website for later deployment.

    """

    def __init__(self, username, repos, directory=os.getcwd()):
        directory = os.path.abspath(directory)
        self.username = username
        self.directory = directory
        self.work = os.path.join(directory, 'work')
        self.site = os.path.join(directory, 'site')
        self.repos = []
        for name, branch, path in repos:
            url = PATH.format(username=username, reponame=name)
            localwork = os.path.join(self.work, path)
            localbuild = os.path.join(self.site, path)
            self.repos.append(GhpRepo(url, localwork, localbuild, branch))

    def initial_build(self):
        """Clone and build for the first time"""
        os.makedirs(self.work, exist_ok=True)
        os.makedirs(self.site, exist_ok=True)
        for repo in self.repos:
            repo.checkout()
            repo.build()

    def build(self):
        """Call initial_build() if this is the first time, otherwise update and build."""
        if not (os.path.exists(self.work) and os.path.exists(self.site)):
            self.initial_build()
            return

        for repo in self.repos:
            repo.update_and_build()


if __name__ == '__main__':
    from config import USERNAME, REPOS
    builder = GhpBuilder(USERNAME, REPOS)
    builder.build()
