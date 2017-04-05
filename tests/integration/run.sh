#!/bin/bash
# shellcheck disable=SC2039

pushd "$(dirname "${0}")/../.." > /dev/null
ROOT_DIR=$(pwd)
popd > /dev/null

TMP_DIR="${ROOT_DIR}/tmp"
RECIPE_DIR="${TMP_DIR}/recipes"
SOURCE_DIR="${TMP_DIR}/source_directory"
WORK_DIR="${TMP_DIR}/work_directory"
CUSTOM_DIR="${ROOT_DIR}/tests/fixtures/custom"
CLI="sclrbh"
RECIPE_ORG_FILE="${RECIPE_DIR}/ror.yml"
RECIPE_ID="rh-ror50"
RECEIPE_TEST_MIN_FILE="${RECIPE_DIR}/ror_test_min.yml"
RECEIPE_TEST_MACRO_FILE="${RECIPE_DIR}/ror_test_macro.yml"
BRANCH="rhscl-2.4-rh-ror50-rhel-7"
MOCK_CONFIG="rhscl-2.4-rh-ror50-rhel-7-x86-64"
LOG_FILE="integration.log"

before_test() {
    if [ ! -d "${TMP_DIR}" ]; then
        mkdir "${TMP_DIR}"
    fi

    # Download recipe files.
    if [ ! -d "${RECIPE_DIR}" ]; then
        pushd "${TMP_DIR}"
        git clone https://github.com/sclorg/rhscl-rebuild-recipes.git recipes
        popd
    fi

    # Create recipe files for test.
    sed '/rubygem-rspec-core/,$d' "${RECIPE_ORG_FILE}" \
        > "${RECEIPE_TEST_MIN_FILE}"
    sed '/rubygem-rspec-expectations/,$d' "${RECIPE_ORG_FILE}" \
        > "${RECEIPE_TEST_MACRO_FILE}"

    # Check Kerberos for rhpkg.
    if ! (klist | grep -q 'REDHAT.COM'); then
        echo "ERROR: Run kinit for rhpkg." 1>&2
        exit 1
    fi

    # Download packages for tests to source directory.
    if [ ! -d "${SOURCE_DIR}" ]; then
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

    return 0
}

make_test_dir() {
    mktemp -d --suffix="-sclrbh"
}

prepare_work_dir() {
    rm -rf "${WORK_DIR}" || :
    mkdir "${WORK_DIR}"

    "${CLI}" \
        --download "local" \
        --source-directory "${SOURCE_DIR}" \
        --work-directory "${WORK_DIR}" \
        "${RECEIPE_TEST_MACRO_FILE}" \
        "${RECIPE_ID}"
    return "${?}"
}

download_only_test() {
    local test_work_dir=""

    test_work_dir="$(make_test_dir)"
    "${CLI}" \
        --download "local" \
        --source-directory "${SOURCE_DIR}" \
        --work-directory "${test_work_dir}" \
        "${RECEIPE_TEST_MIN_FILE}" \
        "${RECIPE_ID}"
    local status="${?}"
    rm -rf "${test_work_dir}"
    return "${status}"
}

download_from_local_and_build_with_dummy_test() {
    local test_work_dir=""

    test_work_dir="$(make_test_dir)"
    "${CLI}" \
        --download "local" \
        --build dummy \
        --source-directory "${SOURCE_DIR}" \
        --work-directory "${test_work_dir}" \
        "${RECEIPE_TEST_MIN_FILE}" \
        "${RECIPE_ID}"
    local status="${?}"
    rm -rf "${test_work_dir}"
    return "${status}"
}

download_by_rhpkg_and_build_with_dummy_test() {
    "${CLI}" \
        --download rhpkg \
        --build dummy \
        --branch "${BRANCH}" \
        "${RECEIPE_TEST_MIN_FILE}" \
        "${RECIPE_ID}"
    return "${?}"
}

download_with_custom_and_build_with_dummy_test() {
    "${CLI}" \
        --download custom \
        --build dummy \
        --custom-file "${CUSTOM_DIR}/echo.yml" \
        "${RECEIPE_TEST_MIN_FILE}" \
        "${RECIPE_ID}"
    return "${?}"
}

build_only_test() {
    prepare_work_dir

    "${CLI}" \
        --work-directory "${WORK_DIR}" \
        "${RECEIPE_TEST_MIN_FILE}" \
        "${RECIPE_ID}"
    return "${?}"
}

build_only_with_mock_test() {
    local config_file="/etc/mock/${MOCK_CONFIG}.cfg"
    if [ ! -f "${config_file}" ]; then
        echo "PENDING: mock config file not found: ${config_file}"
        return 0
    fi
    prepare_work_dir

    "${CLI}" \
        --build mock \
        --work-directory "${WORK_DIR}" \
        -M "${MOCK_CONFIG}" \
        "${RECEIPE_TEST_MIN_FILE}" \
        "${RECIPE_ID}"
    return "${?}"
}

# TODO: build_only_with_copr_test

build_only_with_custom_echo_test() {
    prepare_work_dir

    "${CLI}" \
        --build custom \
        --work-directory "${WORK_DIR}" \
        --custom-file "${CUSTOM_DIR}/echo.yml" \
        "${RECEIPE_TEST_MIN_FILE}" \
        "${RECIPE_ID}"
    return "${?}"
}

build_only_with_custom_mock_test() {
    prepare_work_dir

    "${CLI}" \
        --build custom \
        --work-directory "${WORK_DIR}" \
        --custom-file "${CUSTOM_DIR}/rhpkg_mock.yml" \
        "${RECEIPE_TEST_MIN_FILE}" \
        "${RECIPE_ID}"
    return "${?}"
}

build_only_resume_test() {
    prepare_work_dir

    "${CLI}" \
        --build custom \
        --work-directory "${WORK_DIR}" \
        --resume 3 \
        --custom-file "${CUSTOM_DIR}/echo.yml" \
        "${RECEIPE_TEST_MACRO_FILE}" \
        "${RECIPE_ID}"
    return "${?}"
}

download_and_build_with_custom_echo_test() {
    local test_work_dir=""

    test_work_dir="$(make_test_dir)"
    "${CLI}" \
        --download custom \
        --build custom \
        --work-directory "${test_work_dir}" \
        --custom-file "${CUSTOM_DIR}/echo.yml" \
        "${RECEIPE_TEST_MACRO_FILE}" \
        "${RECIPE_ID}"
    return "${?}"
}

download_and_build_with_custom_mock_test() {
    local test_work_dir=""

    test_work_dir="$(make_test_dir)"
    "${CLI}" \
        --download custom \
        --build custom \
        --work-directory "${test_work_dir}" \
        --custom-file "${CUSTOM_DIR}/rhpkg_mock.yml" \
        "${RECEIPE_TEST_MIN_FILE}" \
        "${RECIPE_ID}"
    return "${?}"
}

run_test() {
    test_funcs=(
        download_only_test
        download_from_local_and_build_with_dummy_test
        download_by_rhpkg_and_build_with_dummy_test
        download_with_custom_and_build_with_dummy_test
        build_only_test
        # The test takes long time
        build_only_with_mock_test
        build_only_with_custom_echo_test
        # The test takes long time
        build_only_with_custom_mock_test
        build_only_resume_test
        download_and_build_with_custom_echo_test
        # The test takes long time
        download_and_build_with_custom_mock_test
    )
    rm -f "${LOG_FILE}" || :
    local ret_status="0"
    for test_func in "${test_funcs[@]}"; do
        local is_ok="1"
        cat << EOF | tee -a "${LOG_FILE}"
== TEST: ${test_func} ==
EOF
        local result=""
        result=$(
            (
                time (
                    eval "${test_func}"
                ) >> "${LOG_FILE}" 2>&1
            )
        )
        # shellcheck disable=SC2181
        if [ "${?}" != "0" ]; then
            is_ok="0"
            ret_status="1"
        fi

        if [ "${is_ok}" = "1" ]; then
            echo "  > [OK]" | tee -a "${LOG_FILE}"
        else
            echo "  > [FAILURE]" | tee -a "${LOG_FILE}"
        fi
        echo "${result}" | tee -a "${LOG_FILE}"
    done

    return "${ret_status}"
}

STATUS=0
(
    time (
        before_test && run_test
    ) 2>&1
) | tee -a "${LOG_FILE}"
if [ "${PIPESTATUS[0]}" -ne 0 ]; then
    STATUS=1
fi
echo "exist status: ${STATUS}"
exit "${STATUS}"
