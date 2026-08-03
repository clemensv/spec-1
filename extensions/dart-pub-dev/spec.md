# pub.dev Package Registry Mapping - Version 1.0-rc1
<!-- words: advisoriesupdated dartregistries dartregistriescount -->
<!-- words: dartregistriesurl dartregistry dartregistryid executables -->
<!-- words: grantedpoints gz homepage isdiscontinued likecount lowercased -->
<!-- words: maxpoints packageid packagescount packagesurl pubspec sdk sdks -->
<!-- words: sourceurl spdx toolchain toolchains uploader -->

## Abstract

This specification defines an xRegistry extension that expresses the content of
[pub.dev][pub.dev], and any registry implementing the [Pub repository
API][pub API] for Dart and Flutter packages, in terms of the xRegistry document
format and API [specification][xRegistry Core].

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
    - [4.1.1. Projection Identity Rules](#411-projection-identity-rules)
  - [4.2. Resource Identity](#42-resource-identity)
  - [4.3. Version Identity](#43-version-identity)
  - [4.4. Timestamps](#44-timestamps)
- [5. Group: `dartregistry`](#5-group-dartregistry)
- [6. Resource: `package`](#6-resource-package)
  - [6.1. Protocol Tiers](#61-protocol-tiers)
  - [6.2. Pubspec Attributes](#62-pubspec-attributes)
  - [6.3. Environment and Platforms](#63-environment-and-platforms)
  - [6.4. Dependencies](#64-dependencies)
  - [6.5. Archive Attributes](#65-archive-attributes)
  - [6.6. Retraction and Discontinuation](#66-retraction-and-discontinuation)
  - [6.7. Meta Attributes](#67-meta-attributes)
- [7. Conformance](#7-conformance)

## 1. Overview

pub.dev is the package registry for the Dart language and the Flutter
framework. Package metadata originates in a `pubspec.yaml` manifest and is
augmented by registry-computed quality scores.

This specification maps that model into xRegistry: a pub registry is a Group, a
package is a Resource, and a published version is a Version.

Three aspects of the Dart ecosystem shape this mapping. First, a Dart package
declares its SDK compatibility in an `environment` map keyed by SDK name — in
practice `sdk` for the Dart SDK and, for Flutter packages, `flutter` — which are
separate dimensions of compatibility. Second, pub.dev permits `+` build metadata
in versions, which is not a valid xRegistry Entity ID character and therefore
requires transliteration. Third, only part of what pub.dev publishes is defined
by the [Pub repository API][pub API]; the rest is proprietary to pub.dev, and
this specification separates the two ([Section 6.1](#61-protocol-tiers)).

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

**pubspec**: The `pubspec.yaml` manifest declaring a Dart package's identity,
constraints and dependencies.

**publisher**: A verified domain, such as `dart.dev`, under which packages are
published; publisher verification is performed by the registry.

**pub points**: A registry-computed score measuring conformance to Dart
packaging conventions, always expressed as a granted total out of a maximum
obtainable under the scoring model in force at the time of computation.

**retracted**: A per-*version* marker indicating that version should no longer
be selected, while remaining downloadable for existing pubspec locks.

**discontinued**: A per-*package* marker indicating the maintainers no longer
support the package. It is orthogonal to retraction: a discontinued package's
versions all remain resolvable, and a package with a retracted version is not
thereby discontinued.

**topic**: A member of the registry's canonicalized controlled vocabulary of
subject terms, declared in the pubspec `topics` list. Topics are constrained in
number and lexical form and MAY be normalized by the registry; they are not
free-form keywords.

## 3. Registry Model

The formal xRegistry extension model of the Dart Package Registry resides in
the [model.json](model.json) file. It declares one Group type,
`dartregistries`, and one Resource type, `packages`, with `maxversions` of `0`,
`setversionid` and `singleversionroot` `true`, and `versionmode` `manual`. It
constrains the spec-defined `defaultversionsticky` attribute to `false`.

`versionmode` is `manual` rather than `semver`. Because a version containing
build metadata is encoded opaquely (see
[Section 4.3](#43-version-identity)), the resulting `versionid` is not itself a
Semantic Version and cannot be ordered by a `semver` mode; ordering is
determined by the implementation from the raw `version` values.

For easy reference, the JSON serialization of a Dart Package Registry adheres
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

  "dartregistriesurl": "<URL>",
  "dartregistriescount": <UINTEGER>,
  "dartregistries": {
    "<KEY>": {                                  # dartregistryid, e.g. pub
      "dartregistryid": "<STRING>",             # xRegistry core attributes
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

      "sourceurl": "<URL>", ?                  # base URL of this pub server

      "packagesurl": "<URL>",
      "packagescount": <UINTEGER>,
      "packages": {
        "<KEY>": {                              # packageid, e.g. provider
          "packageid": "<STRING>",              # xRegistry core attributes
          "versionid": "<STRING>",              # version, with '+' as '~'
          "self": "<URL>",
          "shortself": "<URL>", ?
          "xid": "<XID>",

          # Start of default Version's attributes
          "epoch": <UINTEGER>,
          "name": "<STRING>", ?                 # canonical package name
          "description": "<STRING>", ?
          "documentation": "<URL>", ?
          "labels": { "<STRING>": "<STRING>" * }, ?
          "createdat": "<TIMESTAMP>",
          "modifiedat": "<TIMESTAMP>",
          "ancestor": "<STRING>",

          # Start of package extension attributes
          "version": "<STRING>", ?              # exact raw pub.dev version
          "homepage": "<STRING>", ?
          "repository": "<STRING>", ?
          "issue_tracker": "<STRING>", ?
          "topics": [ "<STRING>" * ], ?         # canonicalized vocabulary, max 5
          "environment": { "<STRING>": "<STRING>" * }, ?  # sdk, flutter, ...
          "sdk_constraint": "<STRING>", ?       # == environment["sdk"]
          "flutter_constraint": "<STRING>", ?   # == environment["flutter"]
          "declared_platforms": { "<STRING>": <ANY> * }, ?  # values are null
          "retracted": <BOOLEAN>, ?             # THIS VERSION only
          "published": "<TIMESTAMP>", ?         # pub.dev extension
          "archive_url": "<STRING>", ?          # .tar.gz URL, MAY be temporary
          "archive_sha256": "<STRING>", ?
          "pubspec": <ANY>, ?                   # raw pubspec.yaml as JSON

          "dependencies": {
            "<KEY>": {                          # dependency package name
              "source": "hosted" | "sdk" | "git" | "path",
              "constraint": "<STRING>", ?       # e.g. ^6.0.0
              "package": "<XID>", ?             # -> /dartregistries/packages

              # if source == "hosted"
              "hosted_url": "<URL>", ?          # foreign pub repository
              "hosted_name": "<STRING>", ?      # name on that repository

              # if source == "sdk"
              "sdk": "<STRING>", ?              # e.g. flutter

              # if source == "git"
              "git_url": "<STRING>", ?
              "git_ref": "<STRING>", ?
              "git_path": "<STRING>", ?

              # if source == "path"
              "path": "<STRING>" ?
            } *
          }, ?
          "dev_dependencies": { "<KEY>": { ... } * }, ?      # same item shape
          "dependency_overrides": { "<KEY>": { ... } * }, ?  # same item shape

          "package": "<XID>", ?                 # -> /dartregistries/packages
          # End of package extensions and default Version's attributes

          "metaurl": "<URL>",
          "meta": {
            # ... xRegistry core Meta attributes ...

            # Package-wide meta attributes, Pub repository API
            "is_discontinued": <BOOLEAN>, ?
            "replaced_by": "<STRING>", ?        # superseding package name
            "advisories_updated": "<TIMESTAMP>", ?

            # Package-wide meta attributes, pub.dev proprietary
            "publisher": "<STRING>", ?          # verified publisher, e.g. dart.dev
            "likes": <UINTEGER>, ?              # score.likeCount
            "pub_points": <UINTEGER>, ?         # score.grantedPoints
            "max_points": <UINTEGER>, ?         # score.maxPoints
            "download_count_30_days": <UINTEGER>, ?
            "tags": [ "<STRING>" * ], ?         # score.tags, raw
            "license": [ "<STRING>" * ], ?      # derived from license:* tags
            "detected_platforms": [ "<STRING>" * ] ?  # from platform:* tags
          }, ?
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

A Group is one **projection** of an ecosystem's package metadata into
xRegistry. The `dartregistryid` names that projection. For packages projected
from the pub metadata model the `dartregistryid` MUST be `pub`.

The identifier is deliberately not a server, a host or an account. A registry
that serves Dart packages from the public server, from a mirror, from an
internal proxy or from a private hosted server uses the same `pub` Group, so
that `/dartregistries/pub/packages/<packageid>` denotes the same package
wherever it is served.

See [Section 4.1.1](#411-projection-identity-rules) for the rules that govern
this identifier.

#### 4.1.1. Projection Identity Rules

- The identifier MUST be stable across every deployment that serves the same
  projection, and MUST NOT vary by serving host, tenancy or access level. An
  implementation MUST NOT derive it from a DNS name, a URL authority or an
  account name. This is what allows one registry to shadow another: a package
  served from an air-gapped mirror MUST present the same path as the same
  package served from the public server.
- Where pub introduces a metadata model that cannot be projected into the
  attributes defined in this specification without loss or contradiction, that
  model MUST be given a new Group identifier, for example `pub-v2`. Both Groups
  MAY then coexist in one registry, and a client selects the model it
  understands instead of being handed attributes whose meaning has silently
  changed.
- Where two parties project this ecosystem under incompatible interpretations,
  each MUST use a distinct Group identifier. A Group therefore identifies the
  ecosystem together with the reading of it that produced the entries, and two
  entries in the same Group are directly comparable.

Access control is a property of the registry deployment rather than of the
identifier. A registry that exposes only a private server's packages still
exposes them under `pub`, and MAY omit entries the caller is not entitled to
see; a caller MUST NOT infer from an entry's absence that it does not exist
upstream. Where entries drawn from different servers are served together, the
`sourceurl` attribute records which service each Group's entries were projected
from.

### 4.2. Resource Identity

The `packageid` MUST be the package name. Dart package names are lowercase
identifiers composed of ASCII letters, digits and `_`, all of which are valid
xRegistry Entity ID characters, so no encoding is required.

### 4.3. Version Identity

The `versionid` MUST be derived from the pub.dev version string as follows:

- If the raw version is already a valid xRegistry Entity ID, it MUST be used
  unchanged. This is the common case, covering `1.4.0` and `1.0.0-beta.1`.
- Otherwise — that is, when the version contains `+` build metadata, as in
  `2.0.0+1` — each `+` MUST be replaced by `~`, giving `2.0.0~1`.

Percent-encoding MUST NOT be used, because `%` is itself not a valid xRegistry
Entity ID character.

`~` is chosen because it is a valid Entity ID character and cannot occur in a
pub.dev version string: pub.dev versions are Semantic Versions, whose grammar
admits only ASCII alphanumerics, `.`, `-` and `+`. The substitution is therefore
collision-free, and unlike an opaque encoding it leaves the identifier readable
in a URL.

The `versionid` is an identifier, not an encoding, and consumers MUST NOT
attempt to recover the upstream version from it. The exact raw version MUST
always be preserved in the `version` attribute, and consumers requiring the
upstream version string — in particular to address pub.dev itself — MUST read
`version`.

Versions MUST be ordered oldest-first by pub.dev semantic ordering. The highest
version in that ordering is the default Version. Because
`defaultversionsticky` is constrained to `false`, publishing a higher version
advances the default.

### 4.4. Timestamps

An implementation MUST set the core `createdat` attribute of a Version to the
pub.dev `published` value of that version, and `modifiedat` to the time of the
most recent change to the projected metadata. `published` is a pub.dev extension
rather than a Pub repository specification field
([Section 6.1](#61-protocol-tiers)); where the upstream registry does not supply
it, an implementation MUST set `createdat` to the time at which it first
observed the version and MUST omit the `published` attribute rather than
restating that observation time in it.

## 5. Group: `dartregistry`

The Group (`<GROUP>`) name is `dartregistry` (singular); the plural, used as the
collection name, is `dartregistries`. A `dartregistry` represents one
projection of the pub metadata model into xRegistry. Its identifier names that
projection rather than the service that serves it. See
[Section 4.1](#41-group-identity) for how the identifier is formed.

This extension defines the following Group-level extension attributes, in
addition to those inherited from [xRegistry Core][xRegistry Core]:

| xRegistry attribute | Type | Description |
|---|---|---|
| `sourceurl` | `url` | Base URL of the server these packages were projected from, for example `https://pub.dev`. Provenance only. |

## 6. Resource: `package`

The Resource (`<RESOURCE>`) name is `package` (singular); the plural, used as
the collection name, is `packages`.

### 6.1. Protocol Tiers

This specification covers registries implementing the [Pub repository
API][pub API] (repository specification v2), of which pub.dev is one. Only part
of the mapping is grounded in that protocol; the remainder comes from pub.dev's
proprietary "Additional APIs", which no other registry is obliged to offer.
Implementations and consumers MUST distinguish the two tiers.

**Tier 1 — Pub repository specification v2.** Available from any conforming
registry. Comprises the pubspec-derived attributes (`name`, `description`,
`homepage`, `repository`, `issue_tracker`, `topics`, `environment`,
`sdk_constraint`, `flutter_constraint`, `declared_platforms`, `dependencies`,
`dev_dependencies`, `dependency_overrides`, `pubspec`, `version`), the archive
attributes (`archive_url`, `archive_sha256`), the per-version `retracted` flag,
and the package-wide `is_discontinued`, `replaced_by` and `advisories_updated`
meta attributes.

**Tier 2 — pub.dev proprietary.** Every attribute in this tier is OPTIONAL and
an implementation MUST omit it when the upstream registry does not offer the
corresponding API. A consumer MUST NOT require any of them and MUST NOT treat
their absence as an error or as an incomplete projection. The tier comprises:

| Attribute | Upstream source |
|---|---|
| `published` | `published` field of the version object |
| `publisher` | `GET /api/packages/<package>/publisher` |
| `likes` | `likeCount` of `GET /api/packages/<package>/score` |
| `pub_points` | `grantedPoints` of the score endpoint |
| `max_points` | `maxPoints` of the score endpoint |
| `download_count_30_days` | `downloadCount30Days` of the score endpoint |
| `tags` | `tags` of the score endpoint |
| `license` | derived from the `license:*` entries of `tags` |
| `detected_platforms` | derived from the `platform:*` entries of `tags` |

`published` is listed here because the repository specification's version object
does not define a publication timestamp; pub.dev adds one. Where it is absent,
the core `createdat` mapping of [Section 4.4](#44-timestamps) has no upstream
value and an implementation MUST fall back to the time at which it first
observed the version.

### 6.2. Pubspec Attributes

| xRegistry attribute | Type | Pubspec field | Description |
|---|---|---|---|
| `name` | `string` | `name` | The canonical package name. |
| `description` | `string` | `description` | Short description of the package. |
| `homepage` | `string` | `homepage` | Project homepage URL. |
| `repository` | `string` | `repository` | Source repository URL. |
| `issue_tracker` | `string` | `issue_tracker` | Issue tracker URL. |
| `topics` | `array` of `string` | `topics` | Canonicalized subject terms; see below. |
| `version` | `string` | `version` | The exact raw version string. |
| `published` | `timestamp` | — | RFC 3339 publication timestamp. Tier 2. |
| `retracted` | `boolean` | — | Whether *this version* has been retracted; see [Section 6.6](#66-retraction-and-discontinuation). |
| `pubspec` | `any` | — | The complete `pubspec.yaml` for the version, as parsed JSON. |

`pubspec` is retained in full because the pubspec carries publisher-defined
sections — `executables`, `flutter`, `funding`, `false_secrets` — that this
specification does not enumerate, and discarding them would make the projection
lossy. It is the normative fallback: where a structured attribute defined here
and the raw pubspec disagree, the raw pubspec is authoritative.

`topics` is *not* a free-form keyword list, and it is deliberately not renamed
to `keywords`, because doing so would misrepresent it. It is a controlled
vocabulary closer to crates.io categories than to npm keywords:

- at most 5 topics MAY be declared;
- each topic is 2 to 32 characters long;
- each consists of lowercase ASCII letters, digits and hyphens, MUST begin with
  a letter and MUST end with a letter or digit;
- the registry maintains a canonical set and MAY merge alternative spellings
  onto a canonical topic, so the projected value MAY differ from the literal
  text in the publisher's pubspec.

An implementation MUST project the topics as the registry canonicalizes them,
and MUST NOT invent topics from other metadata.

There is no version-level `license` attribute. The Pub repository specification
conveys no licence information at all, and a pubspec has no licence field; see
[Section 6.7](#67-meta-attributes) for where licence data actually comes from
and why it is multi-valued.

### 6.3. Environment and Platforms

| xRegistry attribute | Type | Description |
|---|---|---|
| `environment` | `map` of `string` | The pubspec `environment` section verbatim: SDK name to version constraint. |
| `sdk_constraint` | `string` | Convenience restatement of `environment["sdk"]`, the Dart SDK constraint, e.g. `>=3.0.0 <4.0.0`. |
| `flutter_constraint` | `string` | Convenience restatement of `environment["flutter"]`, present only for Flutter packages. |
| `declared_platforms` | `map` of `any` | The pubspec `platforms` section: platform name to a conventionally null value. |

`environment` is a map, not a fixed pair of fields, because that is what the
pubspec declares. Its keys are SDK names, and while `sdk` and `flutter` are the
only two in common use, the section is open and a projection that recognized
only those two would silently discard any other. `sdk_constraint` and
`flutter_constraint` are retained as conveniences for the two well-known keys:
when present each MUST be byte-identical to the corresponding `environment`
entry, and an implementation MUST NOT populate one without the other being
derivable from `environment`.

The two constraints remain separately addressable because they constrain
independent toolchains: a package can be compatible with a wide range of Dart
SDKs while requiring a narrow Flutter range, or require no Flutter at all.

`declared_platforms` is a *map*, not a list, because the pubspec `platforms`
section is a mapping whose values are conventionally null and are reserved for
future per-platform configuration. Projecting it as a list of names would
discard that structure and would misrepresent a mapping as a sequence. The item
type is `any` so that a non-null value, should one appear, survives.

`declared_platforms` MUST NOT be conflated with `detected_platforms`
([Section 6.7](#67-meta-attributes)). The former is what the publisher asserts;
the latter is what the registry's static analysis concluded. They routinely
disagree — a package that declares nothing may be detected as supporting every
platform, and a package that declares support the analyzer cannot confirm will
not be tagged for it. An implementation MUST NOT derive either from the other.

### 6.4. Dependencies

Runtime dependencies, development dependencies and dependency overrides are
carried in three separate maps, matching the pubspec's own separation.

Each is a **map keyed by dependency package name**, not an array, because that
is the pubspec's own shape and the name is the key. In the pubspec, each value
is a *union*: either a bare version constraint string, or a source descriptor
object. Both forms are projected onto one object shape discriminated by
`source`:

```yaml
"dependencies": {
  "KEY": {                     # dependency package name
    "source": "hosted",        # hosted | sdk | git | path
    "constraint": "STRING", ?  # pub version constraint, e.g. "^1.2.0"
    "package": "XID", ?        # xRegistry reference to the dependency

    "hosted_url": "URL", ?     # source == hosted
    "hosted_name": "STRING", ?

    "sdk": "STRING", ?         # source == sdk, e.g. "flutter"

    "git_url": "STRING", ?     # source == git
    "git_ref": "STRING", ?
    "git_path": "STRING", ?

    "path": "STRING" ?         # source == path
  } *
}
```

- `source` is REQUIRED. The bare-string shorthand `http: ^1.2.0` MUST be
  projected as `{"source": "hosted", "constraint": "^1.2.0"}`; the shorthand and
  an explicit `hosted:` descriptor are the same source kind and MUST NOT be
  distinguished.
- `constraint` MUST be the constraint string exactly as declared. It is a range,
  not a resolved version. It applies to `hosted` dependencies and MAY appear on
  `sdk` dependencies; it MUST be omitted for `git` and `path`.
- `hosted_url` carries `hosted.url`, the base URL of a *foreign* pub repository.
  This is the only construct in a pubspec that expresses a cross-registry
  dependency, and it MUST be preserved: without it a dependency on a package
  from a private repository is indistinguishable from one on a same-named
  package in this registry. `hosted_name` carries `hosted.name` when the package
  is published under a different name on that repository.
- `sdk` carries the `sdk:` key. The dependency is vended by the toolchain and
  has no registry package; `flutter: {sdk: flutter}` — present in essentially
  every Flutter package — is the canonical instance, and a model without this
  source kind cannot represent the majority of the Flutter ecosystem.
- `git_url`, `git_ref` and `git_path` carry the `git:` descriptor, in both its
  string shorthand (`git: <url>`) and its expanded form.
- `path` carries a filesystem path. Such dependencies are not resolvable by a
  registry consumer and are retained only for fidelity.
- `package` is an `xid` targeting `/dartregistries/packages`. Per the xRegistry
  model target grammar, the target names the plural Resource collection. It is
  applicable only when `source` is `hosted` and the dependency resolves within a
  registry covered by this projection; it MUST be omitted when `hosted_url`
  points at a registry that is not.
- `dev_dependencies` are required only to develop and test the package itself
  and MUST NOT be treated as transitive requirements of consumers.
- `dependency_overrides` apply only when the package is the *root* of a
  resolution and are ignored when it is consumed as a dependency. Consumers MUST
  NOT treat them as requirements of the package.

These maps earn their place beside the raw `pubspec` only because they are
lossless with respect to it. An implementation MUST NOT drop a dependency it
cannot classify; if a descriptor uses a source kind not enumerated here, the
implementation MUST omit the entry from the structured map rather than
misclassify it, and consumers MUST consult `pubspec` when exactness matters.

### 6.5. Archive Attributes

| xRegistry attribute | Type | Description |
|---|---|---|
| `archive_url` | `string` | Download URL of the version's `.tar.gz` archive. |
| `archive_sha256` | `string` | SHA-256 checksum of that archive. |

`archive_sha256` is the integrity anchor for the version. Implementations MUST
NOT synthesize it; it MUST be omitted when the registry does not publish it.

`archive_url` is **not stable**. The Pub repository specification permits the
URL to be temporary, and registries commonly return a time-limited signed URL
whose validity is measured in minutes. A cached xRegistry projection will
therefore serve expired download URLs. Accordingly:

- Consumers MUST treat `archive_url` as valid only at the moment the containing
  document was retrieved, and MUST NOT persist it.
- Consumers MUST re-fetch the version metadata to obtain a fresh URL rather than
  reusing a stored one, and MUST NOT interpret a failure to download from a
  stale URL as the version having been removed.
- Implementations that cache upstream responses SHOULD refresh `archive_url` on
  every projection rather than serving it from cache.

`archive_sha256` is unaffected by this and remains the stable identifier of the
archive's content; it is the value consumers MUST use to verify a download and
to compare two archives.

### 6.6. Retraction and Discontinuation

Retraction and discontinuation are two distinct signals at two distinct levels,
and a projection that merges them is wrong in both directions.

| Attribute | Level | Meaning |
|---|---|---|
| `retracted` | Version | *This version* MUST NOT be selected by new resolutions. |
| `is_discontinued` | Package (`meta`) | The *package* is no longer maintained. |
| `replaced_by` | Package (`meta`) | The name of the package that supersedes it. |

- `retracted` is per-version and comes from the `retracted` field of the version
  object. A retracted version remains downloadable so that existing lock files
  keep resolving. Retracting one version says nothing about any other version
  and nothing about the package.
- `is_discontinued` is package-wide and comes from the `isDiscontinued` field of
  the package inspect response. All versions of a discontinued package remain
  resolvable; the flag is advisory. A package can be discontinued with no
  retracted versions, and can have retracted versions without being
  discontinued.
- `replaced_by` is meaningful only when `is_discontinued` is true, and is
  OPTIONAL even then. It is the bare package name; an implementation MUST NOT
  substitute a URL or an `xid` for it, because the named package may not exist
  in the projection.

An implementation MUST NOT set `is_discontinued` from any version's `retracted`
value, MUST NOT set `retracted` from `is_discontinued`, and MUST NOT expose a
single combined flag.

### 6.7. Meta Attributes

The following are declared as Resource `metaattributes` because they are
properties of the package rather than of a single Version. The first three are
Tier 1; the rest are Tier 2 and are OPTIONAL
([Section 6.1](#61-protocol-tiers)).

| xRegistry attribute | Type | Tier | Description |
|---|---|---|---|
| `is_discontinued` | `boolean` | 1 | Whether the package is discontinued. |
| `replaced_by` | `string` | 1 | Name of the superseding package. |
| `advisories_updated` | `timestamp` | 1 | When the package's advisory set last changed. |
| `publisher` | `string` | 2 | The verified publisher domain, e.g. `dart.dev`. |
| `likes` | `integer` | 2 | Number of users who have liked the package (`likeCount`). |
| `pub_points` | `integer` | 2 | Points granted by static analysis (`grantedPoints`). |
| `max_points` | `integer` | 2 | Points obtainable under the scoring model (`maxPoints`). |
| `download_count_30_days` | `integer` | 2 | Downloads over the trailing 30 days. |
| `tags` | `array` of `string` | 2 | Raw analysis tags from the score endpoint. |
| `license` | `array` of `string` | 2 | Detected licences, from the `license:*` tags. |
| `detected_platforms` | `array` of `string` | 2 | Detected platforms, from the `platform:*` tags. |

`advisories_updated` comes from the `advisoriesUpdated` field of the package
inspect response. It is a cache-invalidation signal for the security advisories
endpoint: it changes whenever the set of advisories affecting the package
changes. It does not assert that any advisory exists, and an implementation MUST
NOT infer vulnerability from its presence or recency.

`publisher` is deliberately *not* mapped to the Group. A publisher is a DNS
domain whose ownership was verified once, at the time the publisher was created,
and it is single-valued; but it is neither total nor immutable. The publisher
API returns `null` for packages published under individual uploader accounts
rather than a publisher, and a package MAY be transferred between publishers.
Above all, a pub.dev package name is globally unique across the whole registry
irrespective of publisher, so the publisher carries no disambiguating power.
Grouping by it would make a package's `xid` change on an ownership transfer that
did not change the package at all. This attribute MUST be omitted when the
package is not published under a publisher.

`pub_points` and `max_points` MUST be populated together or not at all. A
granted total is uninterpretable without its denominator, and the denominator is
not a constant: the scoring model gains and retires checks over time, so
`maxPoints` differs between packages analyzed at different times. Consumers MUST
NOT compare two `pub_points` values whose `max_points` differ, and MUST NOT
assume any particular maximum.

`download_count_30_days` replaces the former `popularity` score. The registry no
longer computes a normalized popularity value and no endpoint returns one, so no
such attribute is defined here; an implementation MUST NOT synthesize one. The
download count is an absolute figure over a rolling 30-day window: it is not
normalized, not comparable across registries, and not a ranking.

`tags` is the raw tag list from the score endpoint, retained verbatim because it
is the only carrier of several classes of registry-derived information, and
because the tag vocabulary evolves faster than this specification. `license` and
`detected_platforms` are derived projections of it and MUST be consistent with
it.

`license` is an ARRAY. The Pub repository specification conveys no licence
information whatsoever, and a pubspec has no licence field, so the sole upstream
source is the `license:<id>` entries of the score endpoint's `tags`, which pub.dev
computes by scanning the package's LICENSE file. That detection is regularly
multi-valued — dual- and multi-licensed packages yield several `license:` tags —
so modelling it as a single SPDX string would silently drop all but one and
misstate the licensing of the package. Values are the tag suffixes, lowercased.
They are usually SPDX identifiers but are NOT guaranteed to be, and an
implementation MUST NOT rewrite them into SPDX form or reject values that are not
recognized. Implementations MUST omit the attribute entirely when the registry
reports no detection.

`detected_platforms` is likewise derived, from the `platform:<name>` tags, and
describes the platforms the registry's analysis of the package concluded it
supports. See [Section 6.3](#63-environment-and-platforms) for why this MUST NOT
be merged with the publisher-declared `declared_platforms`.

## 7. Conformance

An implementation conforms to this specification when:

1. It serves a model equivalent to [`model.json`](model.json), and
2. it applies the identity mapping in [Section 4](#4-identity-mapping), and
3. every attribute it populates carries the meaning assigned in
   [Section 6](#6-resource-package).

An implementation MAY expose additional extension attributes. An implementation
MAY omit any attribute for which the upstream registry supplies no value.

[xRegistry Core]: https://xregistry.io/xreg/xregistryspecs/core-v1/docs/spec.html
[pub.dev]: https://pub.dev/
[pub API]: https://github.com/dart-lang/pub/blob/master/doc/repository-spec-v2.md
