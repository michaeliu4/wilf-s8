# Set up the GitHub repository and frozen release

This document records the author-side release procedure. For the current
public snapshot, use the versioned link in the README. The local tests do
not require GitHub authentication. For a later version, choose a new tag;
do not repeat repository creation if the remote already exists.

## 1. Install the local tools

The simplest supported route is Ubuntu 24.04 or WSL2 with Ubuntu:

```sh
sudo apt-get update
sudo apt-get install -y git gh make g++ python3-venv latexmk texlive-latex-extra texlive-fonts-recommended cm-super
cd wilf-s8
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python src/package_repository.py --check-manifest
make check
make paper test-references
```

On macOS, use GNU g++ (not merely the Xcode `g++` alias for Clang),
Python, GNU Make and MacTeX/TeX Live; several programs use GNU headers.
The Ubuntu/WSL recipe above is the supported installation recipe and the
one used for local verification. No font files are included.
The full mathematical regression is `make verify`; fresh long counts
have separate commands in [REPRODUCING.md](REPRODUCING.md).

## 2. Decide reuse terms and the actual repository name

Add the author-selected license text for the code and the intended data
terms, for example as `LICENSE-CODE` and `LICENSE-DATA`. A single file
may cover both if its terms explicitly do so. Decide separately how the
paper itself is licensed. Preserve any earlier-stage third-party notices.
This package does not choose or grant a license; see
[LICENSE_STATUS.md](../LICENSE_STATUS.md).

Choose an available repository name. The following prompts are examples
for a new repository; use your actual account or organization, not the
literal word `OWNER`:

```sh
read -r -p 'GitHub owner (account or organization): ' OWNER
read -r -p 'Repository name [wilf-s8]: ' NAME
NAME=${NAME:-wilf-s8}
REPO="$OWNER/$NAME"
TAG=v1.0.0
python src/configure_release.py \
  --repository "$REPO" --tag "$TAG" \
  --code-license LICENSE-CODE --data-license LICENSE-DATA
make release-check
```

The script edits `release.json`, `CITATION.cff`, the README's release block,
the manuscript's availability block, and the reuse-terms index. It configures an **intended**
release URL; it does not publish anything, check ownership, or establish
public availability. The actual link becomes usable only after step 5. The prepared revision-7
verification record identifies the pre-configuration PDF; retain it as
historical evidence and record the checks of the configured PDF separately.
Using one license file for both scopes is supported by passing its path
to both options. The checker verifies paths and synchronized metadata,
not the legal adequacy of the terms.

## 3. Freeze the source/PDF pair and initialize Git

```sh
make paper test-references
make check
make package
# Optional before freezing: make verify

git init -b main
git config core.autocrlf false
git add .
git status --short
git commit -m 'Release companion for manuscript revision 8'
```

Configure your actual Git author identity if Git requests it. Do not copy
someone else's identity from an example. Inspect the staged files before
committing: there should be no credentials, local binaries, virtual
environments or private review correspondence. `.gitattributes` preserves
the supplied evidence bytes. `dist/` is ignored and its ZIP is uploaded
as a release asset rather than committed inside the repository.

`make package` writes `dist/wilf-s8-1.0.0.zip` and its `.sha256` file for
TAG `v1.0.0`. The ZIP includes the manuscript and the SHA-256 manifest;
repeated packaging of the same payload produces the same archive bytes.
Run it again after any authorized source or metadata change, and commit
the resulting updated manifest/PDF before tagging.

## 4. Create the repository and enable immutable releases

```sh
gh auth login
gh repo create "$REPO" --public --source=. --remote=origin --push
```

This creates a public repository. To stage privately instead, use
`--private`; it must be made anonymously accessible before being cited as
public evidence. For an existing, empty remote, add that actual `origin`
and push instead of running `gh repo create` again. Do not overwrite a
nonempty repository without reconciling its existing history.

In the repository's **Settings → General → Releases**, enable
**release immutability** before publishing the release. GitHub documents
that the setting applies to future releases. Once an immutable release
is published, its tag and attached assets cannot be changed in place;
prepare every asset before publication. Corrections require a new tag
and release. This protects a snapshot, not a guarantee that GitHub will
host the project forever. A separate archival DOI snapshot may be added
later where appropriate, using its actual assigned identifier.

## 5. Upload all assets to a draft, then publish

The following commands use the same shell variables as above:

```sh
git tag -a "$TAG" -m 'Code, certificates and manuscript revision 8'
git push origin "$TAG"

gh release create "$TAG" \
  "dist/wilf-s8-${TAG#v}.zip" \
  "dist/wilf-s8-${TAG#v}.zip.sha256" \
  manuscript/main.pdf \
  --repo "$REPO" --verify-tag --draft \
  --title 'Wilf S8: manuscript and computational companion' \
  --notes-file docs/RELEASE_NOTES.md
```

Inspect the draft's tag, commit and all three assets. Confirm that the
documented checks passed for that exact source and that the attached PDF
is the intended version.
Then publish deliberately:

```sh
gh release edit "$TAG" --repo "$REPO" --draft=false
```

Do not use `--clobber` to revise a published mathematical release. Keep the
old release and publish corrections under a new version. The release
notes are editable independently of immutable assets; do not treat notes
alone as a fixed certificate.

## 6. Test the actual reader path

Open the release URL in a signed-out/private browser. Download the ZIP
and compare its SHA-256 with the attached checksum, then extract it and
run:

```sh
python3 src/package_repository.py --check-manifest
python3 src/check_certificate.py
python3 src/check_recount_records.py
```

Confirm that the PDF's availability URL resolves to that same release
without institutional or personal login. Record the actual release URL,
tag and commit in the submission records. Local preparation
do not establish this anonymous-access check. Submit the PDF only after
the real release and reuse terms are in place.

## 7. Subsequent versions

Modify the source on a new commit. Configure a new unused tag, rebuild,
review the differences, run the affected tests, package, commit and
publish a new immutable release. Never move the previously cited tag.
The theorem numbers may change; scripts and prose should refer to stable
labels or descriptive names rather than stale numeric locators.

## Official instructions checked on 21 September 2026

- [Create a repository from local source](https://cli.github.com/manual/gh_repo_create).
- [Create a release and attach assets](https://cli.github.com/manual/gh_release_create) and [publish a draft](https://cli.github.com/manual/gh_release_edit).
- [Immutable-release protections and draft-first workflow](https://docs.github.com/en/code-security/concepts/supply-chain-security/immutable-releases).
- [Enable release immutability](https://docs.github.com/en/code-security/how-tos/secure-your-supply-chain/establish-provenance-and-integrity/prevent-release-changes).
- [CITATION.cff](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-citation-files) and [repository licensing](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository).
