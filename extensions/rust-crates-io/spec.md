# Rust Crate Registry Mapping - Version 1.0-rc1
<!-- words: backported cfg cksum crateid cratelinks cratescount cratesurl -->
<!-- words: curated deps homepage hypermedia lockfiles msrv namespace -->
<!-- words: namespaces readme rustregistries rustregistriescount -->
<!-- words: rustregistriesurl rustregistry rustregistryid serde sourceurl -->
<!-- words: spdx sys toml trustpub unyank unyanked vendored -->

## Abstract

This specification defines an xRegistry extension that expresses the content of
[crates.io][crates.io], and any registry implementing the Cargo registry API, in
terms of the xRegistry document format and API [specification][xRegistry Core].

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
- [5. Group: `rustregistry`](#5-group-rustregistry)
- [6. Resource: `crate`](#6-resource-crate)
  - [6.1. Manifest Metadata](#61-manifest-metadata)
  - [6.2. Default Version Selection](#62-default-version-selection)
  - [6.3. Artifact and Integrity Attributes](#63-artifact-and-integrity-attributes)
  - [6.4. Features](#64-features)
  - [6.5. Dependencies](#65-dependencies)
  - [6.6. Registry Statistics and Crate Links](#66-registry-statistics-and-crate-links)
  - [6.7. Yanking](#67-yanking)
  - [6.8. Ownership and Provenance](#68-ownership-and-provenance)
- [7. Conformance](#7-conformance)

## 1. Overview

crates.io is the package registry for the Rust ecosystem. A *crate* is the unit
of distribution; its metadata originates in the `[package]` section of the
crate's `Cargo.toml` manifest and is augmented by registry-maintained
statistics.

This specification maps that model into xRegistry: a crate registry is a Group,
a crate is a Resource, and a published crate version is a Version.

Cargo's crate namespace is flat and globally unique — there are no scopes,
vendors or namespaces — which makes the identity mapping unusually direct. The
interesting modelling questions are instead about how crates.io designates a
crate's default version, about yanking, and about the split between the JSON
API (`GET /api/v1/crates/<name>`) and the sparse registry index, which is the
only source for dependency, feature and checksum data.

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

**crate**: A Rust library or binary published to a registry. Crate names are
globally unique within a registry.

**yank**: A registry operation that prevents new dependency resolutions from
selecting a version while leaving the version downloadable so that existing
lockfiles continue to build.

**category**: A registry-curated slug, drawn from a fixed taxonomy, classifying
a crate by purpose.

**keyword**: A publisher-supplied free-form term. Unlike categories, keywords
are not curated.

## 3. Registry Model

The formal xRegistry extension model of the Rust Crate Registry resides in the
[model.json](model.json) file. It declares one Group type, `rustregistries`,
and one Resource type, `crates`.

The `crate` Resource sets `hasdocument` to `false`. The published `.crate`
archive is a build input, not a metadata document, and is referenced by URL.

The `crate` Resource sets `maxversions` to `0` (unbounded, since crates.io never
removes a published version), `setversionid` to `true` (the `versionid` is
derived from the published version string, not registry-assigned),
`singleversionroot` to `true`, and `versionmode` to `manual`. `versionmode` is
`manual` because the default Version is the registry-computed `default_version`
(see [Section 6.2](#62-default-version-selection)), which is neither the newest
by publication time nor the highest by SemVer precedence.

Attributes are partitioned by the scope at which crates.io reports them.
Version-level fields — everything drawn from `Cargo.toml` or from an index entry
— are declared in the model's `attributes` list. Crate-level fields, which
describe the crate as a whole rather than any one release, are declared in
`metaattributes` and therefore appear in the Resource's `meta` sub-object.

For easy reference, the JSON serialization of a Rust Crate Registry adheres to
this form:

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

  "rustregistriesurl": "<URL>",
  "rustregistriescount": <UINTEGER>,
  "rustregistries": {
    "<KEY>": {                                  # rustregistryid, e.g. crates-io
      "rustregistryid": "<STRING>",             # xRegistry core attributes
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

      "sourceurl": "<URL>", ?                  # index URL of this registry

      "cratesurl": "<URL>",
      "cratescount": <UINTEGER>,
      "crates": {
        "<KEY>": {                              # crateid, e.g. serde_json
          "crateid": "<STRING>",                # xRegistry core attributes
          "versionid": "<STRING>",              # the crate version
          "self": "<URL>",
          "shortself": "<URL>", ?
          "xid": "<XID>",

          # Start of default Version's attributes
          "epoch": <UINTEGER>,
          "name": "<STRING>", ?                 # canonical crate name
          "description": "<STRING>", ?
          "documentation": "<STRING>", ?        # docs URL, e.g. docs.rs
          "labels": { "<STRING>": "<STRING>" * }, ?
          "createdat": "<TIMESTAMP>",
          "modifiedat": "<TIMESTAMP>",
          "ancestor": "<STRING>",

          # Start of crate extension attributes (Version-level)
          "num": "<STRING>", ?                  # exact upstream version string
          "homepage": "<STRING>", ?
          "repository": "<STRING>", ?
          "license": "<STRING>", ?              # an SPDX expression, not a list
          "license_file": "<STRING>", ?         # used when no SPDX expression
          "categories": [ "<STRING>" * ], ?     # crates.io category slugs
          "keywords": [ "<STRING>" * ], ?
          "downloads": <INTEGER>, ?             # downloads of THIS version
          "crate_size": <UINTEGER>, ?           # .crate archive size in bytes
          "cksum": "<STRING>", ?                # SHA-256 of the .crate archive
          "dl_path": "<STRING>", ?
          "readme_path": "<STRING>", ?
          "features": { "<STRING>": [ "<STRING>" * ] * }, ?
          "features2": { "<STRING>": [ "<STRING>" * ] * }, ?
          "v": <UINTEGER>, ?                    # index schema version
          "rust_version": "<STRING>", ?         # MSRV
          "edition": "<STRING>", ?              # 2015 | 2018 | 2021 | 2024 | ...
          "lib_links": "<STRING>", ?            # Cargo manifest `links` key
          "has_lib": <BOOLEAN>, ?
          "bin_names": [ "<STRING>" * ], ?
          "yanked": <BOOLEAN>, ?                # THIS version only
          "yank_message": "<STRING>", ?
          "published_by": { ... }, ?
          "audit_actions": [ { ... } * ], ?
          "dependencies": [ { ... } * ], ?
          # End of crate extensions and default Version's attributes

          "metaurl": "<URL>",
          "meta": {
            "crateid": "<STRING>",
            "self": "<URL>",
            "xid": "<XID>",
            "epoch": <UINTEGER>,
            "createdat": "<TIMESTAMP>",
            "modifiedat": "<TIMESTAMP>",
            "readonly": <BOOLEAN>,
            "compatibility": "<STRING>",
            "defaultversionid": "<STRING>",
            "defaultversionurl": "<URL>",
            "defaultversionsticky": false,      # MUST be false

            # Start of crate extension attributes (Resource-level)
            "default_version": "<STRING>", ?    # crates.io default version
            "max_version": "<STRING>", ?        # DEPRECATED upstream
            "max_stable_version": "<STRING>", ? # DEPRECATED upstream
            "newest_version": "<STRING>", ?     # DEPRECATED upstream
            "num_versions": <UINTEGER>, ?
            "downloads": <INTEGER>, ?           # all-time, all versions
            "recent_downloads": <INTEGER>, ?    # last 90 days
            "yanked": <BOOLEAN>, ?              # ALL versions are yanked
            "trustpub_only": <BOOLEAN>, ?
            "owners": [ { ... } * ], ?
            "crate_links": { ... } ?            # typed CrateLinks struct
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
xRegistry. The `rustregistryid` names that projection. For crates projected from
the crates.io index and API model the `rustregistryid` MUST be `crates-io`.

The identifier is deliberately not a registry deployment, a host or an account.
A registry that serves crates from the public service, from a mirror, from a
vendored index or from an alternate registry that follows the same index format
uses the same `crates-io` Group, so that
`/rustregistries/crates-io/crates/<crateid>` denotes the same crate wherever it
is served.

See [Section 4.1.1](#411-projection-identity-rules) for the rules that govern
this identifier.

#### 4.1.1. Projection Identity Rules

- The identifier MUST be stable across every deployment that serves the same
  projection, and MUST NOT vary by serving host, tenancy or access level. An
  implementation MUST NOT derive it from a DNS name, a URL authority or an
  account name. This is what allows one registry to shadow another: a crate
  served from an air-gapped mirror MUST present the same path as the same crate
  served from the public service.
- Where the Rust ecosystem introduces an index or metadata model that cannot be
  projected into the attributes defined in this specification without loss or
  contradiction, that model MUST be given a new Group identifier, for example
  `crates-io-v2`. Both Groups MAY then coexist in one registry, and a client
  selects the model it understands instead of being handed attributes whose
  meaning has silently changed.
- Where two parties project this ecosystem under incompatible interpretations,
  each MUST use a distinct Group identifier. A Group therefore identifies the
  ecosystem together with the reading of it that produced the entries, and two
  entries in the same Group are directly comparable.

Access control is a property of the registry deployment rather than of the
identifier. A registry that exposes only an alternate registry's crates still
exposes them under `crates-io` when they follow that index model, and MAY omit
entries the caller is not entitled to see; a caller MUST NOT infer from an
entry's absence that it does not exist upstream. Where entries drawn from
different services are served together, the `sourceurl` attribute records which
service each Group's entries were projected from.

### 4.2. Resource Identity

The `crateid` MUST be the crate name. Cargo restricts crate names to ASCII
letters, digits, `-` and `_`, all of which are valid xRegistry Entity ID
characters, so no encoding is required.

crates.io treats `-` and `_` as equivalent when checking for name collisions but
does not merge such crates once published. Implementations MUST use the name
exactly as published and MUST NOT normalize separators.

### 4.3. Version Identity

The `versionid` MUST be derived from the crate version, which Cargo requires to
be a [Semantic Version][semver]. Versions containing build metadata (`+`) are
not valid xRegistry Entity IDs.

A version containing build metadata MUST have each `+` replaced by `~`, giving
`1.0.0~sha.a1b2` for the upstream `1.0.0+sha.a1b2`. Versions without build
metadata are used verbatim. Percent-encoding MUST NOT be used, because `%` is
itself not a valid Entity ID character.

`~` is a valid Entity ID character and cannot occur in a Semantic Version, whose
grammar admits only ASCII alphanumerics, `.`, `-` and `+`, so the substitution
is collision-free while leaving the identifier readable.

The `versionid` is an identifier, not an encoding, and consumers MUST NOT
attempt to recover the upstream version from it. The exact upstream string MUST
be preserved in the `num` attribute — named after the crates.io field of the
same name — and consumers addressing crates.io MUST read `num`.

Published crate versions are immutable: crates.io does not permit a version to
be overwritten or deleted. Implementations MUST report published versions as
immutable Versions.

### 4.4. Timestamps

An implementation MUST set the core `createdat` attribute of a Version to the
crates.io `created_at` value of that version, and `modifiedat` to its
`updated_at` value. The crate-level `created_at` and `updated_at` values MUST be
carried by the Resource's `meta.createdat` and `meta.modifiedat`. Because the
core attributes carry these values in full fidelity, this specification
deliberately defines no `created_at` or `updated_at` extension attribute at
either level, and implementations MUST NOT introduce one.

## 5. Group: `rustregistry`

The Group (`<GROUP>`) name is `rustregistry` (singular); the plural, used as the
collection name, is `rustregistries`. A `rustregistry` represents one
projection of the crates.io metadata model into xRegistry. Its identifier names
that projection rather than the service that serves it. See
[Section 4.1](#41-group-identity) for how the identifier is formed.

This extension defines the following Group-level extension attributes, in
addition to those inherited from [xRegistry Core][xRegistry Core]:

| xRegistry attribute | Type | Description |
|---|---|---|
| `sourceurl` | `url` | Base URL of the index these crates were projected from, for example `https://index.crates.io`. Provenance only. |

## 6. Resource: `crate`

The Resource (`<RESOURCE>`) name is `crate` (singular); the plural, used as the
collection name, is `crates`.

### 6.1. Manifest Metadata

All attributes in this section are Version-level: their values come from the
`[package]` section of a single version's `Cargo.toml` and MAY differ between
versions of the same crate.

| xRegistry attribute | Type | `Cargo.toml` field | Description |
|---|---|---|---|
| `name` | `string` | `package.name` | The canonical crate name. |
| `num` | `string` | `package.version` | The exact upstream version string, preserved verbatim. |
| `description` | `string` | `package.description` | Short description of the crate. |
| `homepage` | `string` | `package.homepage` | Project homepage URL. |
| `repository` | `string` | `package.repository` | Source repository URL. |
| `documentation` | `string` | `package.documentation` | Documentation URL; defaults to the docs.rs page when unset upstream. |
| `license` | `string` | `package.license` | SPDX license expression, which MAY combine identifiers with `OR` / `AND`. |
| `license_file` | `string` | `package.license-file` | Repository-relative path to a license text that has no SPDX expression. |
| `categories` | `array` of `string` | `package.categories` | Curated category slugs. |
| `keywords` | `array` of `string` | `package.keywords` | Publisher-supplied keywords. |
| `rust_version` | `string` | `package.rust-version` | The minimum supported Rust version (MSRV). |
| `edition` | `string` | `package.edition` | The Rust language edition. The enumeration is open; new editions are added over time. |
| `lib_links` | `string` | `package.links` | The native library this version links against. |
| `has_lib` | `boolean` | — | Whether this version publishes a library target. |
| `bin_names` | `array` of `string` | — | The names of the binary targets published by this version. |

`license` is a single string, not an array, because Cargo requires an SPDX
*expression*; the boolean relationship between multiple licenses is encoded in
the expression itself and MUST NOT be discarded by splitting it.

`license` is a **version-level** attribute. It is not reported on the crate
object returned by `GET /api/v1/crates/<name>`; it appears only on version
objects and in the manifest. A crate MAY legitimately have neither `license` nor
`license_file` — crates.io does not require licensing metadata — and
implementations MUST NOT synthesize a value when both are absent.

The `lib_links` attribute carries Cargo's `package.links` manifest key, which
declares the native library a `-sys` crate links against. It is deliberately
*not* named `links`, because crates.io uses `links` for the crate-level
hypermedia structure described in
[Section 6.6](#66-registry-statistics-and-crate-links). crates.io itself
disambiguates the manifest key as `lib_links` on its version objects, and this
specification follows that naming.

### 6.2. Default Version Selection

crates.io exposes four crate-level pointers into the version history. Three of
them — `max_version`, `max_stable_version` and `newest_version` — are marked
`deprecated` in the crates.io API schema. They are retained in this
specification only so that existing clients can be served, and this
specification therefore places no normative requirement on them beyond
reporting them faithfully.

| xRegistry attribute (in `meta`) | Type | Status | Description |
|---|---|---|---|
| `default_version` | `string` | Current | The version crates.io designates as the crate's default: the highest non-yanked, non-pre-release version where one exists. |
| `max_version` | `string` | DEPRECATED upstream | The highest version by SemVer precedence, including pre-releases and yanked versions. |
| `max_stable_version` | `string` | DEPRECATED upstream | The highest version by SemVer precedence excluding pre-releases. |
| `newest_version` | `string` | DEPRECATED upstream | The most recently *published* version, which need not be the highest. |

An implementation MUST set the Resource's `meta.defaultversionid` to the
`versionid` derived from `default_version`. `default_version` is the upstream
concept that corresponds exactly to xRegistry's own default Version: it is a
single, registry-computed designation of "the version a consumer gets when it
does not ask for a particular one", which is precisely what
`meta.defaultversionid` denotes. No derivation, ranking or tie-breaking is
performed by the implementation; the registry's designation is authoritative.

Because the default Version always tracks the registry's computation,
`meta.defaultversionsticky` MUST be `false`. The model pins it to that value.

An implementation MUST NOT populate `default_version` by computing it from
`max_version`, `max_stable_version` or `newest_version`, and MUST NOT populate
any of those three from `default_version`. Where the upstream registry does not
supply a deprecated pointer, the corresponding attribute MUST be omitted rather
than synthesized. The four values are independent: `newest_version` reflects
publication order, `max_version` SemVer precedence, `max_stable_version` SemVer
precedence over stable releases only, and `default_version` additionally
excludes yanked versions. A backported patch to an older release line, or a yank
of the highest stable release, makes them differ.

Where a registry implementing the Cargo API supplies none of the four, an
implementation MAY select any published Version as the default, and SHOULD
prefer the highest non-yanked, non-pre-release version so as to match what
Cargo resolves for an unconstrained dependency.

### 6.3. Artifact and Integrity Attributes

These Version-level attributes describe the published `.crate` archive. Apart
from `downloads`, they originate in the sparse registry index rather than in the
JSON API.

| xRegistry attribute | Type | Description |
|---|---|---|
| `cksum` | `string` | The lowercase hexadecimal SHA-256 checksum of the published `.crate` archive. |
| `crate_size` | `uinteger` | The size of the `.crate` archive in bytes. |
| `dl_path` | `string` | The registry-relative path from which the `.crate` archive is downloaded. |
| `readme_path` | `string` | The registry-relative path from which the rendered README is retrieved. |
| `downloads` | `integer` | The download count for this specific version. |
| `v` | `uinteger` | The registry index schema version of this version's index entry. |

`cksum` is the sole integrity anchor for a published version. An implementation
that has access to the registry index MUST populate it, and MUST reproduce the
recorded digest verbatim rather than recomputing it. Consumers SHOULD verify a
downloaded archive against `cksum` before use.

`v` governs how the feature tables are interpreted. A consumer that does not
recognise the value of `v` MUST refuse to use the index entry, as required by
the Cargo index format, rather than degrading to a best-effort interpretation.

### 6.4. Features

| xRegistry attribute | Type | Description |
|---|---|---|
| `features` | `map` of `array` of `string` | Each feature name maps to the list of features it enables. |
| `features2` | `map` of `array` of `string` | Feature entries requiring index format version 2 or later. |

`features2` exists solely because the version 1 index format cannot express
weak dependency features (`dep_name?/feat_name`) or explicit dependency
activation (`dep:dep_name`). It is a transport artefact, not a semantic
distinction: a consumer MUST merge `features2` into `features` before resolving,
and the two maps MUST NOT declare the same feature name.

### 6.5. Dependencies

The `dependencies` attribute is an `array` of `object`, projected from the
`deps` array of the version's registry index entry. Each element has the
following attributes.

| Attribute | Type | Description |
|---|---|---|
| `name` | `string` | The name the dependency is referred to by in this crate. When the dependency was renamed this is the local alias. |
| `req` | `string` | The Cargo SemVer requirement the dependency version must satisfy, for example `^1.0`. |
| `features` | `array` of `string` | The features of the dependency explicitly enabled by this crate. |
| `optional` | `boolean` | Whether the dependency is optional. |
| `default_features` | `boolean` | Whether the default features of the dependency are enabled. |
| `target` | `string` | The Cargo target expression gating the dependency, for example `cfg(windows)`. ABSENT when unconditional. |
| `kind` | `string` | `normal`, `dev` or `build`. The enumeration is open. |
| `registry` | `string` | The index URL of the registry the dependency resolves from. ABSENT when it is the same registry as the crate. |
| `package` | `string` | The real crate name when the dependency was renamed. ABSENT when it was not. |

`optional` and `default_features` are the *upstream index field names*, carried
through unchanged. They are ordinary attribute names within the `dependencies`
object and have no relationship to xRegistry's own notion of attribute
optionality.

`name` and `package` MUST NOT be conflated. When `package` is present, `name` is
the alias by which the crate's own source refers to the dependency, and
`package` is the crate that must actually be resolved; an implementation that
drops `package` produces an unresolvable dependency graph.

Dependencies are Version-level. They are not reported on the crate object, and
an implementation MUST NOT hoist the default Version's dependencies to the
Resource's `meta`.

### 6.6. Registry Statistics and Crate Links

These attributes are crate-level and appear in the Resource's `meta`
sub-object.

| xRegistry attribute (in `meta`) | Type | Description |
|---|---|---|
| `downloads` | `integer` | Cumulative all-time download count summed over every version. |
| `recent_downloads` | `integer` | Download count over the trailing 90-day window. |
| `num_versions` | `uinteger` | The number of published versions, including yanked ones. |
| `trustpub_only` | `boolean` | Whether the crate may only be published through Trusted Publishing. |
| `crate_links` | `object` | The crates.io `CrateLinks` structure. |

These values are registry-operator statistics rather than manifest data. They
MUST be omitted when the registry does not supply them rather than defaulted
to `0`.

`crate_links` is **not** a free-form string-to-string map. Upstream it is a
typed `CrateLinks` structure with a fixed set of six members, each of which is
individually nullable, so an implementation MUST omit an absent member rather
than emitting an empty string.

| `crate_links` member | Type | Description |
|---|---|---|
| `version_downloads` | `string` | Registry-relative path to per-version download statistics. |
| `versions` | `string` | Registry-relative path to the crate's version list. ABSENT when the list was inlined in the response. |
| `owners` | `string` | Registry-relative path to the combined owner list. |
| `owner_team` | `string` | Registry-relative path to the team owners. |
| `owner_user` | `string` | Registry-relative path to the individual user owners. |
| `reverse_dependencies` | `string` | Registry-relative path to the crates that depend on this crate. |

All six values are registry-relative paths, not absolute URLs, and MUST be
resolved against the registry's API base URI before use.

The attribute is named `crate_links` rather than `links` to avoid a collision
with Cargo's `package.links` manifest key, which declares the native library a
crate links against and is an entirely unrelated, Version-level value. Since
both would otherwise occupy the name `links` within the same Resource, this
specification adopts crates.io's own disambiguation and models the manifest key
as `lib_links` (see [Section 6.1](#61-manifest-metadata)).

Reverse dependencies are not projected as an attribute. They are a query over
the whole registry rather than a property of the crate, and are reachable
through `crate_links.reverse_dependencies`.

### 6.7. Yanking

Yanking is reported at two different scopes, with two different meanings, and
the two MUST NOT be conflated.

| xRegistry attribute | Scope | Description |
|---|---|---|
| `yanked` | Version | Whether *this specific version* has been yanked. |
| `yank_message` | Version | The operator-supplied explanation recorded when this version was yanked. |
| `yanked` (in `meta`) | Resource | Whether **every** version of the crate has been yanked. |

The crate-level `yanked` is a conjunction over the whole version history: it is
`true` only when no unyanked version remains. It does **not** report the yank
status of the latest version, of `default_version`, or of any other single
version. An implementation MUST NOT populate the crate-level `yanked` from any
individual version's status, and MUST NOT populate a version's `yanked` from the
crate-level value.

`yank_message` is ABSENT when the version is not yanked, and MAY be ABSENT for a
yanked version when the operator supplied no explanation. Its presence therefore
MUST NOT be used to infer yank status; `yanked` is the only authority.

A yanked version MUST remain listed in the Versions collection, because yanking
does not remove the artifact and existing lockfiles still resolve to it.

crates.io already excludes yanked versions when computing `default_version`, so
an implementation that follows [Section 6.2](#62-default-version-selection)
performs no yank filtering of its own. Where no `default_version` is supplied,
an implementation MUST NOT select a yanked version as the default Version while
a non-yanked version exists.

### 6.8. Ownership and Provenance

| xRegistry attribute | Scope | Type | Description |
|---|---|---|---|
| `published_by` | Version | `object` | The registry user that published this version. |
| `audit_actions` | Version | `array` of `object` | The recorded `publish`, `yank` and `unyank` actions for this version, in chronological order. |
| `owners` (in `meta`) | Resource | `array` of `object` | The users and teams authorized to publish new versions. |

`published_by` is ABSENT for versions published before crates.io began recording
the publisher; an implementation MUST NOT substitute an owner for it, since
ownership can change after publication whereas the publisher of a version
cannot.

Each `owners` element carries a `kind` of `user` or `team`; the enumeration is
open so that registries implementing the Cargo API may define further owner
kinds.

## 7. Conformance

An implementation conforms to this specification when:

1. It serves a model equivalent to [`model.json`](model.json), and
2. it applies the identity mapping in [Section 4](#4-identity-mapping), and
3. every attribute it populates carries the meaning assigned in
   [Section 6](#6-resource-crate).

An implementation MAY expose additional extension attributes. An implementation
MAY omit any attribute for which the upstream registry supplies no value.

[xRegistry Core]: https://xregistry.io/xreg/xregistryspecs/core-v1/docs/spec.html
[crates.io]: https://crates.io/
[semver]: https://semver.org/
