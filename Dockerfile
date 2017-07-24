FROM fedora

ARG PYTHON
ARG EXTRA_PKGS
ARG DNF=dnf

ENV TEST_USER_ID 1000

WORKDIR /opt/rpm-list-builder
COPY . .

RUN "${DNF}" -y install \
    --setopt=install_weak_deps=false \
    --setopt=tsflags=nodocs \
    --setopt=deltarpm=0 \
    rpm-build git "/usr/bin/${PYTHON}" ${EXTRA_PKGS} \
    && "${DNF}" clean all

RUN "${PYTHON}" -m ensurepip \
    && "${PYTHON}" -m pip install --upgrade pip setuptools \
    && "${PYTHON}" -m pip install tox

RUN useradd -u "${TEST_USER_ID}" tester

RUN chown -R "${TEST_USER_ID}" .

USER "${TEST_USER_ID}"

ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

CMD ["/usr/bin/tox"]
