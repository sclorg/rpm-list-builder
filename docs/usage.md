# Usage

## Get packages from recipe.

## Builds

### Mock Build

### Copr build

sclrbh supports copr, mock and custom build.

* Prepare copr repo to build.

* If you want to delete pacakages in the copr, enter

```bash
$ scripts/delete_copr_pkgs COPR_REPO
```

* If you want to build from pacakges in your local (= SOURCE_DIRECTORY), enter


```bash
$ sclrbh \
  -D local \
  -s SOURCE_DIRECTORY \
  -C COPR_REPO \
  RECIPE_FILE \
  RECIPE_ID
```
