FROM fedora

ARG PYTHON
ARG EXTRA_PKGS
ARG DNF=dnf

RUN $DNF -y install --setopt=install_weak_deps=false --setopt=tsflags=nodocs \
    --setopt=deltarpm=0 \
    rpm-build git /usr/bin/$PYTHON $EXTRA_PKGS \
    && $DNF clean all

RUN $PYTHON -m ensurepip \
    && $PYTHON -m pip install --upgrade pip setuptools \
    && $PYTHON -m pip install tox

RUN useradd -u 1000 tester

ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

USER 1000

CMD ["/usr/bin/tox"]
