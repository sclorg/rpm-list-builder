# Users Guide

This document is to explain use case with actual command line.
About the example, you can refer an integration test script [tests/integration/run.sh](../tests/integration/run.sh) test_foo method too.

For documentation on the recipe file format, see the [RHSCL Rebuild Recipes](https://github.com/sclorg/rhscl-rebuild-recipes).

## Architecture

The application is to help building a list of RPM packages.

And it is structured from several parts that are "Main application", "Recipe", "Download", "Build", "Work directory".

"Main" is a main application that will get "Recipe" data from recipe file for a defined list of the RPM packages and download and build them.

"Download" is how to get a list of building RPM packages.

"Build" is how to build the list of the RPM packages.

"Main" will order "Download" and "Build".

"Work directory" will manage working directory strucure. See below section for detail.


### Structured factors

```

Main --> Recipe (recipe file)
 |
 +-----> Download +-----> Get pacakges from local directory
 |                |
 |                +-----> Get pacakges from repository by rhpkg clone
 |                |
 |                +-----> Custom Download -> Define the behavior
 |                                           by the config file.
 |
 +-----> Build ---+-----> Copr Build to Copr
                  |
                  +-----> Mock Build to Mock
                  |
                  +-----> Custom Build -> Define the behavior
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

If you want to build from your packages on SOURCE_DIRECTORY in local environment. The SOURCE_DIRECTORY is like this. Just put the packages in same directory.

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

1. Application creates work directory to build. Each subdirectory has number directory that means the order of the build. The number directory name may be zero padding (`0..00N`) by considering the maxinum number of packages in the recipe file.

2. The application rename original spec file to `foo.spec.orig`, and create new file `foo.spec` that is editted to inject macros definition in the recipe file.

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

        $ rpmlb -h

2. Below is `rpmlb`'s basic form. You have to set proper download type, build type, recipe file, reicpe ID. If you omit `--download`, `--build`, the default values are used. You can also use short option name too. See the command help for more detail.

        $ rpmlb \
          --download DOWNLOAD_TYPE \
          --build BUILD_TYPE \
          RECIPE_FILE \
          COLLECTION_ID

### Select download type

#### Local

1. If you have not registered your pacakges to the respository yet, you may want to build from your pacakges on SOURCE_DIRECTORY in local environment. In the case, run

        $ rpmlb \
          --download local \
          --source-directory SOURCE_DIRECTORY \
          ...
          RECIPE_FILE \
          COLLECTION_ID

#### Rhpkg

1. If you have registered your packages to the repository, you may want to build from the packages in repository. In the case, run with `--branch`.

        $ rpmlb \
          --download rhpkg \
          --branch BRANCH \
          ...
          RECIPE_FILE \
          COLLECTION_ID

#### Custom download

1. You may want to customize your download way. In case, you can run with `--custom-file`.

        $ rpmlb \
          ...
          --download custom \
          --custom-file CUSTOM_FILE \
          ...
          RECIPE_FILE \
          COLLECTION_ID

2. What is the custom file? See [sample custom files](../tests/fixtures/custom). It is YAML file like `.travis.yml`. You can write shell script in the file.

  * `before_download`: Write commands to run before build.
  * `download`: Write commands to run for each packages in the pacakges directory. You can use environment variable `PKG` to describe the package name.



### Specify work directory

1. As a default behavior of the application creates work directory to `/tmp/rpmlb-XXXXXXXX`. However you want to specifiy the directory, run with `--work-directory`.

        $ rpmlb \
          ...
          --work-directory WORK_DIRECTORY \
          ...
          RECIPE_FILE \
          COLLECTION_ID

### Select build type

#### Mock Build

1. If you wan to build with mock, run with `--mock-config` (it is same with `mock -r`).

        $ rpmlb \
          ...
          --build mock \
          --mock-config MOCK_CONFIG \
          ...
          RECIPE_FILE \
          COLLECTION_ID

#### Copr build

1. Prepare copr repo to build by yourself.
   The feature to create the copr repo by script is still not supported.

2. If you want to delete pacakages in the copr, run

        $ scripts/delete_copr_pkgs.sh COPR_REPO

3. To build for Copr, enter

        $ rpmlb \
          ...
          --build copr \
          --copr-repo COPR_REPO \
          ...
          RECIPE_FILE \
          COLLECTION_ID

#### Custom build

1. You may want to customize your build way. In case, you can run with `--custom-file`.

        $ rpmlb \
          ...
          --build custom \
          --custom-file CUSTOM_FILE \
          ...
          RECIPE_FILE \
          COLLECTION_ID

2. What is the custom file? See [sample custom files](../tests/fixtures/custom). It is YAML file like `.travis.yml`. You can write shell script in the file.

  * `before_build`: Write commands to run before build.
  * `build`: Write commands to run for each packages in the pacakges directory. You can use environment variable `PKG` to describe the package name.

#### Don't build

1. If you don't want to build, only want to download the pacakges to create work directory. and later want to build only. In case, run **without** `--build` or with `--build dummy`. Then you can see the log for the dummy build. This is good to check your recipe file.

        $ rpmlb \
          ...
          --build dummy \
          ...
          RECIPE_FILE \
          COLLECTION_ID


### Resume from any position of pacakges

1. If your build was failed during the process due to some reasons, you want to resume your build. In case run with `--work-directory` and  `--resume`. The resume number is same with the number directory name in work directory. zero padding is ignored. That is ex. 01 => 1, 012 => 12.

        $ rpmlb \
          ...
          --build BUILD_TYPE \
          --work-directory WORK_DIRECTORY \
          --resume 35 \
          ...
          RECIPE_FILE \
          COLLECTION_ID
