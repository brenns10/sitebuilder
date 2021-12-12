FROM docker.io/ruby:2.7-alpine3.15

RUN apk update \
 && apk add openjdk8-jre \
            python3 \
            texlive \
            texlive-dvi \
            git \
            imagemagick \
 && apk add --virtual .build-dependencies \
                      build-base \
                      ruby-dev \
                      libressl-dev \
 && gem install -N jekyll -v 4.2 \
 && gem install -N webrick -v 1.6 \
 && gem install -N jekyll-paginate -v 1.1 \
 && gem install -N s3_website -v 3.4 \
 && s3_website install \
 && apk del .build-dependencies \
 && mkdir /work \
 && cd /work

ADD sitebuilder.py /usr/bin/sitebuilder
EXPOSE 4000
