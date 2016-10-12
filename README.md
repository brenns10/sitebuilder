sitebuilder
===========

This repository contains a simple Python tool for building all of your GitHub
pages static sites at once, in a somewhat similar way to how it's done in GitHub
pages.

It's great if you have a bunch of stuff on GitHub pages, but you'd like to
migrate to AWS (for SSL + custom domain reasons, perhaps).

Usage
-----

You need to have Python 3, Ruby+Jekyll+github-pages gem installed.

Then, create a file called `config.py` containing info about your GitHub pages
repositories.  Mine is given below as an example:

```python
USERNAME = 'brenns10'
REPOS = [
    # (repo, branch, url)
    ('brenns10.github.io', 'master', ''),
    ('talks', 'gh-pages', 'talks/'),
    ('notes', 'gh-pages', 'notes/'),
    ('libstephen', 'gh-pages', 'libstephen/'),
    ('cky', 'gh-pages', 'cky/'),
    ('yams', 'gh-pages', 'yams/'),
    ('nosj', 'gh-pages', 'nosj/'),
]
```

Finally, run `python sitebuilder.py` and the magic should happen. To view your
site, you could:

```bash
$ cd site
$ python -m http.server
```

And then navigate to http://localhost:8000/

Any time you update a github pages repository, you can update it by simply
running `python sitebuilder.py` again.

Advanced Usage
--------------

Typically, running `python sitebuilder.py` will do what you need, but there are
subcommands that can perform more fine grained control:

- `dwim` - does the same thing as running with no subcommand. That is,
  initialize if not already initialized, and build the site.
- `init` - initialize repositories and build
- `pull` - pull repositories, but don't build
- `build` - pull and build out of date repositories
- `rebuild` - build all repositories (don't pull)
- `help` - show help text

Deployment
----------

Although this project doesn't do much to assist with deployment, a good next
step would be to use the `s3_website` gem to deploy your `site` folder to AWS
and Cloudfront!
