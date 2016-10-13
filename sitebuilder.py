#!/usr/bin/env python3
"""
Takes all your GitHub pages repos and builds their static sites.
"""

import os
import os.path
import shutil
from subprocess import check_call, check_output, DEVNULL

PATH = 'https://github.com/{username}/{reponame}'
HELPTEXT = """usage: {} [SUBCOMMAND]
Build and rebuild GitHub pages sites.  Typical usage is to run with no
arguments, which runs the "dwim" sub-command.

dwim - Automatically guess the operations necessary to completely build your
       site.  Will tell you what it's doing as it goes. (this is default)
init - Initialize the site by pulling and running the first build.
pull - Pull every repository (but do not build anything).
rebuild - Rebuild the entire site (without pulling first).
build - Pull each repository and rebuild if it updated.
help - Display this help text.
"""


def run(args):
    check_call(args, stdout=DEVNULL, stderr=DEVNULL)


class GhpRepo(object):
    """A class representing a git repository with GitHub pages enabled.

    Has a remote URL, a local directory, and a "build" directory, where the
    actual generated site will be placed. Also, most repositories are on branch
    gh-pages, but some (like *.github.io) are on master, so this accepts a
    branch argument.

    This class allows you to clone, build, update, and rebuild a repo fairly
    easily.  Of course, it just shells out to git and jekyll.

    """

    def __init__(self, name, url, local, output, branch='gh-pages'):
        """Create the class instance.

        This doesn't necessarily clone the repo or build it - in fact, the repo
        may already exist locally.

        """
        self.name = name
        self.url = url
        self.local = local
        self.output = output
        self.branch = branch

    def should_build(self):
        return not os.path.exists(os.path.join(self.local, '.nojekyll'))

    def checkout(self):
        """Check out the repository."""
        run(['git', 'clone', '-b', self.branch, self.url, self.local])

    def current_commit(self):
        """Return the SHA of the current commit."""
        os.chdir(self.local)
        return check_output(['git', 'rev-parse', 'HEAD'])

    def pull(self):
        """Pull from the default remote tracking branch, hopefully.

        Return True if updated, false otherwise.
        """
        os.chdir(self.local)
        old_revision = self.current_commit()
        run(['git', 'pull'])
        return self.current_commit() != old_revision

    def build(self):
        """Run the build command (jekyll) or just copy files if .nojekyll exists."""
        os.chdir(self.local)
        if self.should_build():
            print('=> {}: build via Jekyll'.format(self.name))
            run(['jekyll', 'build', '-d', self.output])
        else:
            print('=> {}: build via copy'.format(self.name))
            if os.path.exists(self.output):
                shutil.rmtree(self.output)
            ignore = shutil.ignore_patterns(
                # may have to include lots of stuff in here
                '.git',
                '.gitignore',
                '.nojekyll'
            )
            shutil.copytree(self.local, self.output, ignore=ignore)
        print('   DONE'.format(self.name))

    def update_and_build(self):
        """Pull, and if the repo has changed, rebuild.

        Return True if the repo updated.  Return False otherwise.
        """
        if self.pull():
            print('=> {}: was out of date'.format(self.name))
            self.build()
            return True
        return False


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
        self.main = None
        for name, branch, path in repos:
            url = PATH.format(username=username, reponame=name)
            localwork = os.path.join(self.work, name)
            localbuild = os.path.join(self.site, path)
            if path == '':  # this is the "main site"
                self.main = GhpRepo(name, url, localwork, localbuild, branch)
            else:
                self.repos.append(GhpRepo(name, url, localwork, localbuild, branch))

    def _initial_checkout(self):
        """Create workdir and clone repos for the first time."""
        os.makedirs(self.work, exist_ok=True)
        if self.main:
            self.main.checkout()
        for repo in self.repos:
            repo.checkout()

    def rebuild(self):
        """Build all repos, assuming they are already cloned."""
        os.makedirs(self.site, exist_ok=True)
        if self.main:
            self.main.build()
        for repo in self.repos:
            repo.build()

    def init(self):
        """Check out and build for the first time."""
        self.initial_checkout()
        self.rebuild()

    def pull(self):
        """Pull all repositories without updating."""
        updated = False
        if self.main and self.main.pull():
            print('=> {}: updated'.format(self.main.name))
            updated = True
        for repo in self.repos:
            if repo.pull():
                print('=> {}: updated'.format(repo.name))
                updated = True
        if updated:
            print('You have pulled but not built.  Your site/ directory will')
            print('only be up-to-date when you run "rebuild".')

    def _update_main(self):
        """Update the main repository, and possibly subdirectories.

        Since the main site resides in the root, when it is regenerated, the
        subdirectories are clobbered! To address this, whenever the main repo
        is rebuilt, all other repos are forced to rebuild.

        """
        if self.main and self.main.update_and_build():
            print('Rebuilding other repos since they may have been clobbered.')
            for repo in self.repos:
                repo.build()
            print('Continuing to update other repos...')

    def build(self):
        """Normal build."""
        self._update_main()
        for repo in self.repos:
            repo.update_and_build()

    def dwim(self):
        """Do what I mean mode!

        This tries to infer what operation should be done based on the state of
        the directories.  The goal here is always a completely built site.

        """
        if not os.path.exists(self.work):
            print('Detected that the work directory does not exist.')
            print('Initializing ...')
            self.init()
        elif not os.path.exists(self.site):
            print('Detected that the site directory does not exist, but your repos are cloned.')
            print('Rebuilding ...')
            self.rebuild()
        else:
            print('Updating your existing site.')
            self.build()


def help():
    print(HELPTEXT.format(sys.argv[0]))


if __name__ == '__main__':
    import sys
    from config import USERNAME, REPOS
    builder = GhpBuilder(USERNAME, REPOS)
    commands = {
        'init': builder.init,
        'build': builder.build,
        'rebuild': builder.rebuild,
        'dwim': builder.dwim,
        'pull': builder.pull,
        'help': help,
    }
    if len(sys.argv) <= 1:
        cmd = 'dwim'
    else:
        cmd = sys.argv[1]
    func = commands.get(cmd)
    if func:
        func()
    else:
        help()
