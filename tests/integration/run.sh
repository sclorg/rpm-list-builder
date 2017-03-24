#!/bin/sh -xe
# shellcheck disable=SC2039

pushd "$(dirname "${0}")/../.." > /dev/null
ROOT_DIR=$(pwd)
popd > /dev/null

TMP_DIR="${ROOT_DIR}/tmp"
RECIPE_DIR="${TMP_DIR}/recipes"
RECIPE_ORG_FILE="${RECIPE_DIR}/ror.yml"
RECEIPE_TEST_FILE="${RECIPE_DIR}/ror_test.yml"
SOURCE_DIR="${TMP_DIR}/source_directory"
WORK_DIR="${TMP_DIR}/work_directory"
BRANCH="rhscl-2.4-rh-ror50-rhel-7"
CUSTOM_DIR="${ROOT_DIR}/tests/fixtures/custom"
SCL_BUILDER="$HOME/.local/bin/rhscl-builder"

before_test() {
    pushd "${ROOT_DIR}"
    make setup-uninstall
    make setup-install
    popd

    if [ ! -d "${TMP_DIR}" ]; then
        mkdir "${TMP_DIR}"
    fi

    # Download recipe files.
    if [ ! -d "${RECIPE_DIR}" ]; then
        pushd "${TMP_DIR}"
        git clone https://github.com/sclorg/rhscl-rebuild-recipes.git recipes
        popd
    fi

    # Create recipe file for test.
    sed '/rubygem-rspec-expectations/,$d' "${RECIPE_ORG_FILE}" \
        > "${RECEIPE_TEST_FILE}"

    # Download packages for tests.
    if [ ! -d "${SOURCE_DIR}" ]; then
        if ! (klist | grep -q 'REDHAT.COM'); then
            echo "Run kinit for rhpkg." 1>&2
            exit 1
        fi

        mkdir "${SOURCE_DIR}"
        pushd "${SOURCE_DIR}"
        PKGS="
            rh-ror50
            rubygem-rspec
            rubygem-rspec-core
            rubygem-rspec-support
            rubygem-diff-lcs
        "
        for PKG in ${PKGS}; do
            rhpkg co -b "${BRANCH}" "${PKG}"
        done
        popd
    fi
}


download_from_local_and_build_dummy_test() {
    "${SCL_BUILDER}" \
        -D local \
        -B dummy \
        -s "${SOURCE_DIR}" \
        "${RECEIPE_TEST_FILE}" \
        rh-ror50
}

download_by_rhpkg_and_build_dummy_test() {
    "${SCL_BUILDER}" \
        -D rhpkg \
        -B dummy \
        -b "${BRANCH}" \
        "${RECEIPE_TEST_FILE}" \
        rh-ror50
}

only_download_test() {
    rm -rf "${WORK_DIR}"
    "${SCL_BUILDER}" \
        -D local \
        -B dummy \
        -s "${SOURCE_DIR}" \
        -C "${WORK_DIR}" \
        "${RECEIPE_TEST_FILE}" \
        rh-ror50
}

only_build_test() {
    "${SCL_BUILDER}" \
        -D none \
        -B dummy \
        -C "${WORK_DIR}" \
        "${RECEIPE_TEST_FILE}" \
        rh-ror50
}

only_build_by_mock_test() {
    "${SCL_BUILDER}" \
        -D none \
        -B mock \
        -C "${WORK_DIR}" \
        -M rhscl-2.4-rh-ror50-rhel-7-x86-64 \
        "${RECEIPE_TEST_FILE}" \
        rh-ror50
}

only_build_by_custom_echo_test() {
    "${SCL_BUILDER}" \
        -D none \
        -B custom \
        -C "${WORK_DIR}" \
        --custom-file "${CUSTOM_DIR}/echo.yml" \
        "${RECEIPE_TEST_FILE}" \
        rh-ror50
}

only_build_by_custom_echo_resume_test() {
    "${SCL_BUILDER}" \
        -D none \
        -B custom \
        -C "${WORK_DIR}" \
        -r 3 \
        --custom-file "${CUSTOM_DIR}/echo.yml" \
        "${RECEIPE_TEST_FILE}" \
        rh-ror50
}

only_build_by_custom_mock_test() {
    "${SCL_BUILDER}" \
        -D none \
        -B custom \
        -C "${WORK_DIR}" \
        --custom-file "${CUSTOM_DIR}/mock.yml" \
        "${RECEIPE_TEST_FILE}" \
        rh-ror50
}

before_test

download_from_local_and_build_dummy_test
download_by_rhpkg_and_build_dummy_test
only_download_test
only_build_test
only_build_by_mock_test
only_build_by_custom_echo_test
only_build_by_custom_echo_resume_test
only_build_by_custom_mock_test
