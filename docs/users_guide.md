# Users Guide

This document is to explain use case with actual command line.
About the example, you can refer an integration test script [tests/integration/run.sh](../tests/integration/run.sh) test_foo method too.

## Architecture

This application is to to help rebuild packages.

And it is structured from several parts that are "Main application", "Recipe", "Download", "Build", "Work directory".

"Main application" is directer program.
That gets "Recipe" data from recipe file.


### Structured factors

```

Main --> Recipe (recipe file)
 |
 +-----> Download +-----> Get pacakges from local directory
 |                |
 |                +-----> Get pacakges from repository by rhpkg clone
 |
 +-----> Build ---+-----> Copr Build to Copr
                  |
                  +-----> Mock Build to Mock
                  |
                  +-----> Custome Build -> Define the behavior
                                           by the config file.
```

### Relationship of Recipe file, Source directory and Work directory

#### Recipe file (ex. `ror50.yml`)

```
rh-ror50:
  packages:
    - rh-ror50:
        macros:
          install_scl: 0
    # Packages required by RSpec, Cucumber
    - rubygem-rspec
    - rubygem-rspec-core:
        replaced_macros:
          need_bootstrap_set: 1
    - rubygem-rspec-support:
        replaced_macros:
          need_bootstrap_set: 1
    - rubygem-diff-lcs:
        macros:
          _with_bootstrap: 1
```

#### Source directory

```
source_directory/
├── rh-ror50
│   ├── LICENSE
│   ├── README
│   ├── rh-ror50.spec
│   └── sources
├── rubygem-diff-lcs
│   ├── rubygem-diff-lcs.spec
│   └── sources
├── rubygem-rspec
│   ├── rubygem-rspec.spec
│   └── sources
├── rubygem-rspec-core
│   ├── rspec-core-3.5.4-Fixes-for-Ruby-2.4.patch
│   ├── rspec-related-create-full-tarball.sh
│   ├── rubygem-rspec-core.spec
│   └── sources
└── rubygem-rspec-support
    ├── rspec-related-create-full-tarball.sh
    ├── rubygem-rspec-support-3.2.1-callerfilter-searchpath-regex.patch
    ├── rubygem-rspec-support-3.6.0.beta2-fix-for-ruby-2.4.0.patch
    ├── rubygem-rspec-support-3.6.0.beta2-fix-for-ruby-2.4.0-tests.patch
    ├── rubygem-rspec-support.spec
    └── sources
```

#### Work directory

```
work_directory/
├── 1
│   └── rh-ror50
│       ├── LICENSE
│       ├── README
│       ├── rh-ror50.spec
│       ├── rh-ror50.spec.orig
│       └── sources
├── 2
│   └── rubygem-rspec
│       ├── rubygem-rspec.spec
│       ├── rubygem-rspec.spec.orig
│       └── sources
├── 3
│   └── rubygem-rspec-core
│       ├── rspec-core-3.5.4-Fixes-for-Ruby-2.4.patch
│       ├── rspec-related-create-full-tarball.sh
│       ├── rubygem-rspec-core.spec
│       ├── rubygem-rspec-core.spec.orig
│       └── sources
├── 4
│   └── rubygem-rspec-support
│       ├── rspec-related-create-full-tarball.sh
│       ├── rubygem-rspec-support-3.2.1-callerfilter-searchpath-regex.patch
│       ├── rubygem-rspec-support-3.6.0.beta2-fix-for-ruby-2.4.0.patch
│       ├── rubygem-rspec-support-3.6.0.beta2-fix-for-ruby-2.4.0-tests.patch
│       ├── rubygem-rspec-support.spec
│       ├── rubygem-rspec-support.spec.orig
│       └── sources
└── 5
    └── rubygem-diff-lcs
        ├── rubygem-diff-lcs.spec
        ├── rubygem-diff-lcs.spec.orig
        └── sources
```


## Tutorial

1. First of all, run below command to see the command help.

        $ sclrbh -h

2. Below is `sclrbh`'s basic form. You have to set proper download type, build type, recipe file, reicpe ID. If you omit `--download`, `--build`, the default values are used. You can also use short option name too. See the command help.

        $ sclrbh \
          --download DOWNLOAD_TYPE \
          --build BUILD_TYPE \
          RECIPE_FILE \
          RECIPE_ID

### Select download type

### Select build type

#### Mock Build

#### Copr build

1. Prepare copr repo to build by yourself.
   The feature to create the copr repo by script is still not supported.

2. If you want to delete pacakages in the copr, enter

        $ scripts/delete_copr_pkgs COPR_REPO

3. If you want to build from pacakges in your local (= SOURCE_DIRECTORY), enter

        $ sclrbh \
          ...
          --copr-repo COPR_REPO \
          RECIPE_FILE \
          RECIPE_ID

#### Custom build
