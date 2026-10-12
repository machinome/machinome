# Machinome - Source code for machines
# Copyright (C) 2023-2026 Luis Henrique Cassis Fagundes
# SPDX-License-Identifier: GPL-2.0-or-later OR CERN-OHL-S-2.0+
#
# The repository's steps, one command each (change `release-tooling`,
# ADR-192). Run from the repository root, after `make sync`; `make` alone
# lists the targets. uv and npm are found on the PATH.

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.DEFAULT_GOAL := help
# One step at a time, even under -j: the suites share their build
# directories, and `make test` stops at the first failure.
.NOTPARALLEL:
MAKEFLAGS += --no-builtin-rules --no-builtin-variables

UV := uv
NPM := npm
PYTHON := $(CURDIR)/.venv/bin/python
# The workspace's commands first, as an activated venv puts them: the suites
# run `machinome`, `playwright` and the venv's tools as subprocesses.
export PATH := $(CURDIR)/.venv/bin:$(PATH)
DOCS_VENV := .docs-venv

# Every distribution of the repository, by its directory under packages/;
# the layout test holds this list to the directories there.
PACKAGES := \
	machinome \
	machinome-engine-brep \
	machinome-engine-mesh \
	machinome-mechanics \
	machinome-movie \
	machinome-node-build123d \
	machinome-node-cadquery \
	machinome-node-freecad \
	machinome-node-jscad \
	machinome-node-molejo \
	machinome-node-openscad \
	machinome-node-solid2 \
	machinome-node-step \
	machinome-node-stl \
	machinome-skills \
	machinome-studio \
	machinome-viewer \
	machinome-viewer-openscad

# The packages with tests of their own, in the order `make test` runs them;
# the core's suite tests the extension packages.
TESTED := machinome machinome-mechanics machinome-skills machinome-viewer \
	machinome-movie machinome-studio
UNTESTED := $(filter-out $(TESTED),$(PACKAGES))

# The npm member that builds the browser viewer's bundle, the movie's Node
# side, whose tests CI runs by project, and the studio's frontend, which
# builds the studio's browser surface.
WIDGET := packages/machinome-viewer/machinome/viewer/web/widget
MOVIE_JS := packages/machinome-movie/machinome/movie/js
STUDIO_FRONTEND := packages/machinome-studio/machinome/studio/frontend

# The npm members that keep a lock of their own, which npm reads only
# outside the workspace.
MEMBER_LOCKS := $(MOVIE_JS)

# The set's version, declared once: `current_version` of .bumpversion.cfg.
CURRENT := $(shell sed -n 's/^current_version = //p' .bumpversion.cfg)
RELEASE := dist/v$(CURRENT)

# What the targets write and `make clean` removes: never .venv/, an npm
# install, a release folder under dist/ or a tracked file.
CLEAN := $(DOCS_VENV) packages/machinome/docs/_build packages/*/build \
	$(WIDGET)/dist packages/machinome-studio/machinome/studio/static

.PHONY: help version bump sync test lint docs widget dist upload check clean \
	bundle $(addprefix test-,$(PACKAGES))

help: ## List the targets
	@awk -F ':.*## ' '/^[a-z]+:.*## / {printf "  make %-8s %s\n", $$1, $$2}' $(firstword $(MAKEFILE_LIST))

version: ## Print the set's version, current_version of .bumpversion.cfg
	@echo $(CURRENT)

bump: ## Move the set to VERSION=X.Y.Z: every copy and every lock; no commit, no tag
	@test -n "$(VERSION)" || { echo 'make bump: name the version: make bump VERSION=X.Y.Z' >&2; exit 2; }
	@test "$(VERSION)" != "$(CURRENT)" || { echo 'make bump: the set is at $(CURRENT) already' >&2; exit 2; }
	@git diff --quiet HEAD || { echo 'make bump: the tracked files have changes; commit them first:' >&2; git status --short --untracked-files=no >&2; exit 1; }
	$(PYTHON) -m bumpversion --no-commit --no-tag --new-version $(VERSION) patch
	$(NPM) install --package-lock-only --no-audit --no-fund
	@for member in $(MEMBER_LOCKS); do \
	  copy=$$(mktemp -d); \
	  cp $$member/package.json $$member/package-lock.json $$copy/; \
	  (cd $$copy && $(NPM) install --package-lock-only --no-audit --no-fund); \
	  cp $$copy/package-lock.json $$member/package-lock.json; rm -rf $$copy; \
	done
	$(UV) lock
	@git diff --stat
	@git status --short

sync: ## Install the workspace from its locks: every package editable, the npm members, Chromium
	@command -v $(UV) >/dev/null || { echo 'make sync: uv is not on the PATH' >&2; exit 1; }
	@command -v $(NPM) >/dev/null || { echo 'make sync: npm is not on the PATH; install Node.js 22 or newer' >&2; exit 1; }
	$(UV) sync --python 3.12
	$(NPM) ci --no-audit --no-fund
	playwright install chromium

test: $(if $(PKG),test-$(PKG),$(addprefix test-,$(TESTED))) ## Run the tests of PKG=<package>, or of every package with tests, stopping at the first failure

bundle:
	$(NPM) run build --workspace $(WIDGET)

test-machinome: bundle
	cd packages/machinome && $(PYTHON) -m pytest

test-machinome-mechanics test-machinome-skills:
	cd packages/$(@:test-%=%) && $(PYTHON) -m pytest

test-machinome-viewer:
	$(NPM) run typecheck --workspace $(WIDGET)
	$(NPM) test --workspace $(WIDGET)
	$(NPM) run build --workspace $(WIDGET)
	cd packages/machinome-viewer && $(PYTHON) -m pytest

test-machinome-movie:
	cd packages/machinome-movie && $(PYTHON) -m pytest
	$(NPM) test --workspace $(MOVIE_JS) -- --project pure --project stage

# The studio's tests serve its built surface; its browser tests run when
# MACHINOME_STUDIO_E2E=1 is set (change `join-studio`).
test-machinome-studio:
	$(NPM) test --workspace $(STUDIO_FRONTEND)
	$(NPM) run build --workspace $(STUDIO_FRONTEND)
	cd packages/machinome-studio && $(PYTHON) -m pytest

$(addprefix test-,$(UNTESTED)):
	@echo 'make test: $(@:test-%=%) keeps no tests of its own; the core'"'"'s suite tests it: make test PKG=machinome' >&2; exit 2

test-%:
	@echo 'make test: $* is not a package; the packages are $(PACKAGES)' >&2; exit 2

lint: ## Check the style of every package's sources with black and flake8, as CI does
	@status=0; cd packages/machinome; \
	$(PYTHON) -m black --check machinome tests ../machinome-*/machinome || status=1; \
	$(PYTHON) -m flake8 --max-line-length=89 machinome tests ../machinome-*/machinome || status=1; \
	exit $$status

docs: bundle ## Build the viewer's bundle, then the manual with warnings as errors, from docs/requirements.txt alone, into packages/machinome/docs/_build/html
	test -x $(DOCS_VENV)/bin/python || $(UV) venv --python 3.12 $(DOCS_VENV)
	$(UV) pip install --python $(DOCS_VENV)/bin/python -r packages/machinome/docs/requirements.txt
	cd packages/machinome && $(CURDIR)/$(DOCS_VENV)/bin/python -m sphinx -b html -W -E docs docs/_build/html

widget: ## Install the npm workspace from its lock and build its bundles
	$(NPM) ci --no-audit --no-fund
	$(NPM) run build --workspaces --if-present

dist: ## Build, check and smoke every archive of the commit into dist/vX.Y.Z; upload nothing
	@git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo 'make dist: a release is built from a Git checkout' >&2; exit 1; }
	@test -z "$$(git status --porcelain)" || { echo 'make dist: the tree differs from its commit; commit or remove:' >&2; git status --short >&2; exit 1; }
	@copy=$$(mktemp -d "$${TMPDIR:-/tmp}/machinome-dist-XXXXXX"); \
	trap 'rm -rf "$$copy"' EXIT; \
	git archive HEAD | tar -x -C "$$copy"; \
	echo "$$ scripts/check-dist --out $(RELEASE), in a copy of the commit $$(git rev-parse --short HEAD)"; \
	cd "$$copy" && $(PYTHON) scripts/check-dist --out $(CURDIR)/$(RELEASE)

upload: ## Upload dist/vX.Y.Z to PyPI with twine; run by no other target
	@test -n "$$(ls -A $(RELEASE) 2>/dev/null)" || { echo 'make upload: no archives in $(RELEASE); make dist builds them' >&2; exit 1; }
	$(PYTHON) -m twine upload $(RELEASE)/*

check: ## Build, check and smoke every archive from the tree and from a clean copy of its tracked files; keep nothing
	$(PYTHON) scripts/check-dist
	@copy=$$(mktemp -d "$${TMPDIR:-/tmp}/machinome-check-XXXXXX"); \
	trap 'rm -rf "$$copy"' EXIT; \
	git ls-files -z | tar --null -T - -cf - | tar -x -C "$$copy"; \
	echo "$$ scripts/check-dist in a clean copy of the tracked files, $$copy"; \
	cd "$$copy" && $(PYTHON) scripts/check-dist

clean: ## Remove what the targets wrote: the docs venv, the manual's build, build scratch, the bundle
	rm -rf $(CLEAN)
