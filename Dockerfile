FROM fedora

ARG PYTHON
ARG EXTRA_PKGS

RUN dnf -y install --setopt=install_weak_deps=false --setopt=tsflags=nodocs \
    --setopt=deltarpm=false \
    rpm-build git /usr/bin/$PYTHON $EXTRA_PKGS \
    && dnf clean all

RUN $PYTHON -m ensurepip \
    && $PYTHON -m pip install --upgrade pip setuptools \
    && $PYTHON -m pip install tox

RUN useradd -u 1000 tester

ENV LANG=C.UTF-8 LC_ALL=C.UTF-8

USER 1000

CMD ["/usr/bin/tox"]
