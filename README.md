# rhscl-builder

This tool helps you to build packages for Red Hat Software Collection from the [recipe files](https://github.com/sclorg/rhscl-rebuild-recipes).

## License

GPL-2.0

## Usage

Currently this tool supports copr build.

* Prepare copr repo to build.

* If you want to delete pacakages in the copr, enter

```bash
$ tools/delete_copr_pkgs COPR_REPO
```

* If you want to build from pacakges in your local (= SOURCE_DIRECTORY), enter


```bash
$ rhscl-builder \
  -D local \
  -s SOURCE_DIRECTORY \
  -C COPR_REPO \
  RECIPE_FILE \
  RECIPE_ID
```
