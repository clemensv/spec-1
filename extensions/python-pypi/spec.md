# PyPI Package Registry Mapping - Version 1.0-rc1

## Abstract

This specification defines an xRegistry extension that expresses the content of
the [Python Package Index][PyPI] (PyPI), and any registry that implements the
PyPI JSON API, in terms of the xRegistry document format and API
[specification][xRegistry Core].

## Table of Contents

- [Abstract](#abstract)
- [Table of Contents](#table-of-contents)
- [1. Overview](#1-overview)
- [2. Notations and Terminology](#2-notations-and-terminology)
  - [2.1. Notational Conventions](#21-notational-conventions)
  - [2.2. Terminology](#22-terminology)
- [3. Registry Model](#3-registry-model)
- [4. Identity Mapping](#4-identity-mapping)
  - [4.1. Group Identity](#41-group-identity)
  - [4.2. Resource Identity](#42-resource-identity)
  - [4.3. Version Identity](#43-version-identity)
  - [4.4. Timestamps](#44-timestamps)
- [5. Group: `pythonregistry`](#5-group-pythonregistry)
- [6. Resource: `package`](#6-resource-package)
  - [6.1. Core Metadata Mapping](#61-core-metadata-mapping)
  - [6.2. Distribution Files](#62-distribution-files)
  - [6.3. Dependencies](#63-dependencies)
  - [6.4. Vulnerabilities](#64-vulnerabilities)
  - [6.5. Meta Attributes](#65-meta-attributes)
- [7. Conformance](#7-conformance)

## 1. Overview

PyPI is the canonical package index for the Python ecosystem. Its JSON API
serves a project document containing project-level metadata, the metadata of a
selected release, the set of distribution files ("artifacts") for that release,
and known security advisories.

Python packaging metadata is standardized by the [Core Metadata
specification][core metadata] and the dependency-specifier grammar of
[PEP 508][PEP 508]. This specification maps that metadata into xRegistry: a
package index is a Group, a project is a Resource, and a release is a Version.

Unlike most package ecosystems, a single Python release is not one artifact but
a *set* of artifacts — a source distribution plus zero or more wheels built for
specific interpreter, ABI and platform tags. This specification therefore models
the release as the Version and the artifacts as an attribute of that Version.

## 2. Notations and Terminology

### 2.1. Notational Conventions

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be
interpreted as described in [RFC 2119](https://tools.ietf.org/html/rfc2119).

In the pseudo JSON format snippets `?` means the preceding attribute is
OPTIONAL, `*` means the preceding attribute MAY appear zero or more times,
and `+` means the preceding attribute MUST appear at least once. The presence
of the `#` character means the remaining portion of the line is a comment.
Whitespace characters in the JSON snippets are used for readability and are
not normative.

### 2.2. Terminology

**project**: A named unit of distribution on PyPI. Project names are matched
after [normalization][name normalization]: runs of `-`, `_` and `.` are
collapsed to a single `-` and the result is lowercased.

**release**: A published version of a project.

**distribution file**: A single downloadable artifact belonging to a release; a
source distribution (`sdist`) or a built distribution (`bdist_wheel`).

**yanked**: A [PEP 592][PEP 592] marker indicating that a distribution file
remains downloadable for reproducibility but MUST NOT be selected by a resolver
unless pinned exactly. Yanking applies to individual distribution files, not to
the release as a whole.

## 3. Registry Model

The formal xRegistry extension model of the Python Package Registry resides in
the [model.json](model.json) file. It declares one Group type,
`pythonregistries`, and one Resource type, `packages`.

The `package` Resource sets `hasdocument` to `false`. A Python release has no
single canonical document; it has a set of distribution files, described by the
`urls` attribute.

For easy reference, the JSON serialization of a Python Package Registry adheres
to this form:

```yaml
{
  "specversion": "<STRING>",
  "registryid": "<STRING>",
  "self": "<URL>",
  "xid": "<XID>",
  "epoch": <UINTEGER>,
  "name": "<STRING>", ?
  "description": "<STRING>", ?
  "documentation": "<URL>", ?
  "labels": { "<STRING>": "<STRING>" * }, ?
  "createdat": "<TIMESTAMP>",
  "modifiedat": "<TIMESTAMP>",

  "capabilities": { ... }, ?
  "model": { ... }, ?
  "modelsource": { ... }, ?

  "pythonregistriesurl": "<URL>",
  "pythonregistriescount": <UINTEGER>,
  "pythonregistries": {
    "<KEY>": {                                  # pythonregistryid, e.g. pypi.org
      "pythonregistryid": "<STRING>",           # xRegistry core attributes
      "self": "<URL>",
      "shortself": "<URL>", ?
      "xid": "<XID>",
      "epoch": <UINTEGER>,
      "name": "<STRING>", ?
      "description": "<STRING>", ?
      "documentation": "<URL>", ?
      "labels": { "<STRING>": "<STRING>" * }, ?
      "createdat": "<TIMESTAMP>",
      "modifiedat": "<TIMESTAMP>",

      "packagesurl": "<URL>",
      "packagescount": <UINTEGER>,
      "packages": {
        "<KEY>": {                              # packageid, e.g. requests
          "packageid": "<STRING>",              # xRegistry core attributes
          "versionid": "<STRING>",              # PEP 440 version, "+" encoded
          "self": "<URL>",
          "shortself": "<URL>", ?
          "xid": "<XID>",

          # Start of default Version's attributes
          "epoch": <UINTEGER>,
          "name": "<STRING>", ?                 # canonical project name
          "description": "<STRING>", ?          # Core Metadata Description
          "documentation": "<URL>", ?
          "labels": { "<STRING>": "<STRING>" * }, ?
          "createdat": "<TIMESTAMP>",
          "modifiedat": "<TIMESTAMP>",
          "ancestor": "<STRING>",

          # Start of package extension attributes
          "summary": "<STRING>", ?
          "license": "<STRING>", ?              # legacy; see 6.1
          "license_expression": "<STRING>", ?   # SPDX; Core Metadata 2.4
          "license_files": [ "<STRING>" * ], ?
          "author": "<STRING>", ?
          "author_email": "<STRING>", ?         # MAY carry "Name" <addr>
          "maintainer": "<STRING>", ?
          "maintainer_email": "<STRING>", ?
          "home_page": "<URL>", ?
          "project_url": "<URL>", ?
          "project_urls": { "<STRING>": "<STRING>" * }, ?
          "keywords": "<STRING>", ?             # comma-separated, as served
          "description_content_type": "<STRING>", ?   # e.g. text/markdown
          "requires_python": "<STRING>", ?            # e.g. >=3.8
          "classifiers": [ "<STRING>" * ], ?
          "provides_extra": [ "<STRING>" * ], ?
          "platform": "<STRING>", ?             # API field, flattened
          "dynamic": [ "<STRING>" * ], ?

          "requires_dist": [
            {
              "specifier": "<STRING>",          # verbatim PEP 508 specifier
              "package": "<XID>" ?              # -> /pythonregistries/packages
            } *
          ], ?

          "urls": [                             # distribution files
            {
              "filename": "<STRING>",
              "packagetype": "<STRING>", ?      # e.g. sdist, bdist_wheel
              "python_version": "<STRING>", ?
              "requires_python": "<STRING>", ?  # MAY differ per file
              "size": <UINTEGER>, ?
              "upload_time": "<STRING>", ?
              "upload_time_iso_8601": "<TIMESTAMP>", ?
              "url": "<URL>",
              "yanked": <BOOLEAN>, ?            # PEP 592 is per-file; see 6.2
              "yanked_reason": "<STRING>", ?
              "core_metadata": <ANY>, ?         # PEP 658/714
              "digests": {
                "sha256": "<STRING>", ?
                "md5": "<STRING>", ?
                "blake2b_256": "<STRING>" ?
              } ?
            } *
          ], ?

          "vulnerabilities": [
            {
              "id": "<STRING>",                 # e.g. an OSV or PYSEC id
              "aliases": [ "<STRING>" * ], ?
              "summary": "<STRING>", ?
              "details": "<STRING>", ?
              "fixed_in": [ "<STRING>" * ], ?
              "link": "<URL>", ?
              "source": "<STRING>", ?
              "withdrawn": "<TIMESTAMP>" ?
            } *
          ], ?

          "replacedby": "<XID>", ?              # -> /pythonregistries/packages
          # End of package extensions and default Version's attributes

          "metaurl": "<URL>",
          "meta": { ... }, ?
          "versionsurl": "<URL>",
          "versionscount": <UINTEGER>,
          "versions": { ... } ?
        } *
      } ?
    } *
  } ?
}
```

## 4. Identity Mapping

### 4.1. Group Identity

The `pythonregistryid` MUST be the DNS name of the index that serves the
metadata, for example `pypi.org`.

### 4.2. Resource Identity

The `packageid` MUST be the project name as served by the index. PyPI project
names consist of ASCII letters, digits, `-`, `_` and `.`, all of which are valid
in an xRegistry Entity ID, so no encoding is required.

Because PyPI treats project names as equivalent under normalization while
xRegistry Entity ID lookup is case-sensitive, implementations MUST choose one
canonical form and serve it consistently. It is RECOMMENDED to use the
normalized form as `packageid`. The name exactly as published MUST be preserved
in the `name` attribute.

### 4.3. Version Identity

The `versionid` MUST be derived from the [PEP 440][PEP 440] version string of
the release. PEP 440 versions can contain a local version segment introduced by
`+`, which is not valid in an xRegistry Entity ID.

A version containing a local version segment MUST have each `+` replaced by `~`,
giving `1.0~ubuntu.1` for the upstream `1.0+ubuntu.1`. Versions without a local
version segment are used verbatim. Percent-encoding MUST NOT be used, because
`%` is itself not a valid Entity ID character.

`~` is a valid Entity ID character and cannot occur in a PEP 440 version, whose
grammar admits only ASCII alphanumerics, `.`, `-`, `_`, `!`, `+` and `*`, so the
substitution is collision-free while leaving the identifier readable.

The `versionid` is an identifier, not an encoding, and consumers MUST NOT
attempt to recover the upstream version from it. The Version's `name` attribute
MUST carry the PEP 440 version string exactly as published, and consumers
addressing PyPI itself MUST read `name`.

Releases are immutable once published. A distribution file of a release MAY be
yanked, which changes `urls[].yanked` and `urls[].yanked_reason` without
changing the artifacts themselves.

### 4.4. Timestamps

An implementation MUST set the core `createdat` attribute of a Version to the
earliest `upload_time_iso_8601` among that release's distribution files, and
`modifiedat` to the time of the most recent change to the projected metadata —
including the upload of an additional file to an existing release, and a change
in yank status.

## 5. Group: `pythonregistry`

The Group (`<GROUP>`) name is `pythonregistry` (singular); the plural, used as
the collection name, is `pythonregistries`. A `pythonregistry` represents one
Python package index provider.

This extension defines no Group-level extension attributes beyond those
inherited from [xRegistry Core][xRegistry Core].

## 6. Resource: `package`

The Resource (`<RESOURCE>`) name is `package` (singular); the plural, used as
the collection name, is `packages`.

### 6.1. Core Metadata Mapping

Attribute names follow the Core Metadata field names, lowercased with `-`
replaced by `_`, which is also the form used by the PyPI JSON API.

| xRegistry attribute | Type | Core Metadata field | Description |
|---|---|---|---|
| `summary` | `string` | `Summary` | One-line description of the project. |
| `license` | `string` | `License` | Legacy free-text license field, deprecated by Core Metadata 2.4 in favour of `license_expression`. Populated only when the index supplies it. |
| `license_expression` | `string` | `License-Expression` | SPDX license expression (Core Metadata 2.4). |
| `license_files` | `array` of `string` | `License-File` | Paths of license files included in the distribution. |
| `author` | `string` | `Author` | Project author. Often absent in modern projects; see below. |
| `author_email` | `string` | `Author-email` | Author contact address, which MAY carry a display name; see below. |
| `maintainer` | `string` | `Maintainer` | Project maintainer. |
| `maintainer_email` | `string` | `Maintainer-email` | Maintainer contact address. |
| `home_page` | `url` | `Home-page` | Project homepage URL. |
| `project_url` | `url` | — | Primary project URL as surfaced by the index. |
| `project_urls` | `map` of `string` | `Project-URL` | Labelled additional URLs, keyed by label. |
| `keywords` | `string` | `Keywords` | Keywords as served by the index: a single comma-separated string, preserved verbatim rather than split, because the delimiter is not normatively specified. |
| `description_content_type` | `string` | `Description-Content-Type` | Media type of the long description, e.g. `text/markdown`. |
| `requires_python` | `string` | `Requires-Python` | PEP 440 specifier constraining the interpreter version. |
| `classifiers` | `array` of `string` | `Classifier` | Trove classifiers categorizing the project. |
| `provides_extra` | `array` of `string` | `Provides-Extra` | Names of optional feature sets ("extras"). |
| `platform` | `string` | `Platform` | Platform compatibility statement. Projects the JSON API's `platform` field, not the `Platform` metadata field directly; see below. |
| `dynamic` | `array` of `string` | `Dynamic` | Fields computed at build time rather than declared statically. |
| `description` | `string` | `Description` | Long description of the project. This is the xRegistry Core `description` attribute; this extension does not redefine it. |
| `requires_dist` | `array` of `object` | `Requires-Dist` | Dependencies, see [6.3](#63-dependencies). |
| `urls` | `array` of `object` | — | Distribution files, including their PEP 592 yank status, see [6.2](#62-distribution-files). |
| `vulnerabilities` | `array` of `object` | — | Known advisories, see [6.4](#64-vulnerabilities). |
| `replacedby` | `xid` | — | Cross-reference to the `package` Resource that supersedes this one, where the index records a rename or replacement. |

`name` and `description` are xRegistry Core attributes carrying the `Name` and
`Description` Core Metadata fields; this extension does not redefine them.

Core Metadata 2.4 introduced `License-Expression` and deprecated `License`. The
two fields are mutually exclusive: an upload that sets both is rejected by PyPI.
An implementation therefore MUST NOT populate both `license` and
`license_expression` for the same Version, and a consumer determining the
license MUST prefer `license_expression` when it is present. A modern
distribution declaring only `License-Expression` projects no `license` value at
all, so a consumer that reads only `license` will see no license for it.
`license_files` projects the `License-File` fields introduced by the same
revision, naming the license documents packaged inside the distribution; the
contents are not projected.

`platform` is typed `string` because it projects the `platform` field served by
the PyPI JSON API, which flattens the multi-use `Platform` Core Metadata field
into a single value. It is not a projection of the metadata field itself and
MUST NOT be interpreted as a structured list; an implementation reading raw
distribution metadata rather than the JSON API MUST perform the same flattening.

The meaning of `author` and `author_email` has shifted with the adoption of
`pyproject.toml` metadata. `Author-email` accepts RFC 5322 address forms, so
tooling commonly emits a single `Author-email` such as
`"A. Author" <a@example.com>` and emits no `Author` at all. A consumer seeking
an author name therefore MUST NOT rely on `author` alone; where `author` is
absent it MUST parse the display names out of `author_email`. The same applies
to `maintainer` and `maintainer_email`. Both attributes are projected verbatim
and MUST NOT be normalized or split by the implementation.

### 6.2. Distribution Files

`urls` enumerates the downloadable artifacts of the release. Each entry has the
following shape:

```yaml
{
  "filename": "STRING",
  "packagetype": "STRING",             # e.g. "sdist", "bdist_wheel"
  "python_version": "STRING",          # the artifact's python tag
  "requires_python": "STRING" ?,       # MAY differ from the release value
  "size": UINTEGER,                    # size in bytes
  "upload_time": "STRING",
  "upload_time_iso_8601": "TIMESTAMP",
  "url": "URL",
  "yanked": BOOLEAN ?,
  "yanked_reason": "STRING" ?,
  "core_metadata": ANY ?,
  "digests": {
    "sha256": "STRING",
    "md5": "STRING" ?,
    "blake2b_256": "STRING" ?
  }
}
```

Implementations MUST populate `digests.sha256` when the index supplies it;
it is the integrity anchor for the artifact. `md5` is retained only for
compatibility with older tooling and MUST NOT be relied upon for integrity.

[PEP 592][PEP 592] defines yanking at *file* granularity: individual
distribution files of one release MAY be yanked independently, so a release MAY
have a yanked wheel alongside a live source distribution. `urls[].yanked` and
`urls[].yanked_reason` are therefore the only yank status this specification
defines, and an installation tool MUST evaluate them per file. There is
deliberately no release-level `yanked` attribute, because it cannot represent
the mixed case without loss; a consumer needing a release-level view MUST derive
it, treating a release as fully yanked only when every entry of `urls` is
yanked. A release whose `urls` is empty or absent has no yank status.

`urls[].requires_python` carries the per-file `Requires-Python` value, which MAY
differ between files of the same release — for example where a wheel for a newer
interpreter was added later. A resolver MUST apply the per-file value when
selecting an artifact and MUST NOT substitute the Version-level
`requires_python`, which is only the value declared by the release's metadata.

`urls[].core_metadata` projects the JSON API's `core-metadata` key, which
reflects the [PEP 658][PEP 658] / [PEP 714][PEP 714] declaration that the
distribution's metadata is available as a separate file alongside the artifact.
When it is present, a client MAY fetch the metadata by appending `.metadata` to
the artifact URL, and so MUST NOT need to download the artifact itself to read
its metadata. The index serves the value either as the boolean `true` or as a
map of hash names to values, so it is typed `any` and preserved verbatim; when
it is a map, a client MUST verify the fetched metadata against the given
digest.

`packagetype` reports the distribution format. `sdist` and `bdist_wheel` account
for essentially all current uploads, but PyPI continues to serve historical
artifacts recorded as `bdist_egg`, `bdist_wininst`, `bdist_msi`, `bdist_dumb`
and `bdist_rpm`, and the enumeration in [model.json](model.json) is therefore
not strict. A consumer MUST tolerate a value outside the enumeration and MUST
NOT assume that an unrecognized value denotes a wheel.

`packagetype` and `python_version` together with the filename's [wheel
tags][wheel] determine artifact applicability; this specification does not
re-encode the tags as separate attributes because the filename is normative.

### 6.3. Dependencies

Each entry of `requires_dist` has the following shape:

```yaml
{
  "specifier": "STRING",  # the verbatim PEP 508 requirement
  "package": "XID" ?      # xRegistry reference to the depended-upon project
}
```

`specifier` MUST be the PEP 508 string exactly as declared, including any
extras, version specifier and environment marker — for example
`requests[socks]>=2.28; python_version < "3.11"`. It MUST NOT be decomposed or
rewritten, because environment markers make the dependency conditional and any
lossy projection would misrepresent the requirement.

`package` is an `xid` targeting `/pythonregistries/packages` and identifies the
depended-upon project within this registry. It MAY be omitted when the target
cannot be resolved.

### 6.4. Vulnerabilities

`vulnerabilities` projects advisories as surfaced by the index, typically
sourced from the [Open Source Vulnerability][OSV] database. Each entry:

```yaml
{
  "id": "STRING",                    # advisory identifier, e.g. "PYSEC-2023-1"
  "aliases": [ "STRING" * ],         # equivalent identifiers, e.g. CVE IDs
  "summary": "STRING" ?,
  "details": "STRING" ?,
  "fixed_in": [ "STRING" * ],        # versions containing the fix
  "link": "URL" ?,
  "source": "STRING" ?,
  "withdrawn": "TIMESTAMP" ?         # set if the advisory was withdrawn
}
```

An advisory with a non-empty `withdrawn` value MUST NOT be treated as an active
vulnerability.

### 6.5. Meta Attributes

The following is declared as a Resource `metaattribute` because it describes the
project as a whole rather than any single Version:

| xRegistry attribute | Type | Description |
|---|---|---|
| `organization` | `string` | The PyPI Organization account that owns the project, where the project belongs to one. |

`organization` is deliberately *not* mapped to the Group. Organization accounts
are opt-in — subscription-based for corporate organizations and free for
community projects — so most projects belong to no organization, and a project
MAY be moved between organizations. Project names are flat and globally unique
on PyPI after [PEP 503][PEP 503] normalisation regardless of organization, so
the organization carries no disambiguating power and grouping by it would make a
project's `xid` change on an ownership move that did not change the project.
This attribute MUST be omitted when the project belongs to no organization.

## 7. Conformance

An implementation conforms to this specification when:

1. It serves a model equivalent to [`model.json`](model.json), and
2. it applies the identity mapping in [Section 4](#4-identity-mapping), and
3. every attribute it populates carries the meaning assigned in
   [Section 6](#6-resource-package).

An implementation MAY expose additional extension attributes. An implementation
MAY omit any attribute for which the upstream index supplies no value.

[xRegistry Core]: https://xregistry.io/xreg/xregistryspecs/core-v1/docs/spec.html
[PyPI]: https://pypi.org/
[core metadata]: https://packaging.python.org/en/latest/specifications/core-metadata/
[name normalization]: https://packaging.python.org/en/latest/specifications/name-normalization/
[PEP 440]: https://peps.python.org/pep-0440/
[PEP 503]: https://peps.python.org/pep-0503/
[PEP 508]: https://peps.python.org/pep-0508/
[PEP 592]: https://peps.python.org/pep-0592/
[PEP 658]: https://peps.python.org/pep-0658/
[PEP 714]: https://peps.python.org/pep-0714/
[wheel]: https://packaging.python.org/en/latest/specifications/binary-distribution-format/
[OSV]: https://osv.dev/
