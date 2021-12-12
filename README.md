sitebuilder
===========

This repo contains the tools I use to build and deploy my website. I started my
website using Github Pages, but quickly realized I prefer more customization:
for example, being able to add plugins to Jekyll for LaTeX math, etc. I ended up
switching to S3 + Cloudfront, which is great, except that I need to build and
deploy the site manually.

As I've changed computers (or just performed software upgrades), I've noticed
that Jekyll, Ruby, Java, LaTeX, or something else will change and break my
build, or just cause files to change slightly. I want my site to build
consistently, and as reproducible as possible, so I've created these tools to
ensure the site stays the same. There are two components:

1. `sitebuilder.py` is a script which orchestrates several Github repositories
   and branches. It can automatically pull them, notice updates, and regenerate
   a site from them.
2. `Dockerfile` builds a container which can run sitebuilder, as well as Jekyll,
   LaTeX, and my website deployment tool (s3_website). For the most part I
   intend to build this image and then reuse it for all my site builds.

Usage
-----

The prebuilt image is available [on Docker
Hub](https://hub.docker.com/r/brenns10/sitebuilder). You can easily pull it:

``` bash
podman pull docker.io/brenns10/sitebuilder:latest
# you could use Docker too, if you're into running as root :)
```

Then, you can use any of the tools installed within the image like so:

``` bash
# Run sitebuilder -h
podman run -p 4000:4000 -v $(pwd):/work -w /work --rm -it docker.io/brenns10/sitebuilder sitebuilder -h

# Run jekyll
podman run -p 4000:4000 -v $(pwd):/work -w /work --rm -it docker.io/brenns10/sitebuilder jekyll -h

# Run s3_website
podman run -p 4000:4000 -v $(pwd):/work -w /work --rm -it docker.io/brenns10/sitebuilder s3_website -h
```

For the most part, I just use the sitebuilder command on its own, followed by
`sitebuilder deploy`.

Should You Use This?
--------------------

No.
