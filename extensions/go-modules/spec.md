# Go Module Proxy Mapping - Version 1.0-rc1

## Abstract

This specification defines an xRegistry extension that expresses the content of
the [Go module ecosystem][Go modules], as served by a [GOPROXY][GOPROXY]
implementation such as `proxy.golang.org`, in terms of the xRegistry document
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
  - [4.2. Resource Identity](#42-resource-identity)
  - [4.3. Case Escaping](#43-case-escaping)
  - [4.4. Version Identity](#44-version-identity)
  - [4.5. Timestamps](#45-timestamps)
- [5. Group: `goregistry`](#5-group-goregistry)
- [6. Resource: `module`](#6-resource-module)
  - [6.1. Identity Attributes](#61-identity-attributes)
  - [6.2. Module-Wide Meta Attributes](#62-module-wide-meta-attributes)
  - [6.3. Major Version Suffixes](#63-major-version-suffixes)
  - [6.4. Module Deprecation](#64-module-deprecation)
  - [6.5. GOPROXY Endpoint Attributes](#65-goproxy-endpoint-attributes)
  - [6.6. Checksum Attributes](#66-checksum-attributes)
  - [6.7. Version Classification](#67-version-classification)
  - [6.8. `go.mod` Directives](#68-gomod-directives)
  - [6.9. Retraction](#69-retraction)
- [7. Conformance](#7-conformance)

## 1. Overview

The Go module ecosystem has no central package registry in the conventional
sense. A module is identified by its *module path*, which is a URL-like string
whose first component is a domain name; module content is fetched from a module
proxy implementing the GOPROXY protocol, and integrity is guaranteed by a
transparency log — the checksum database.

This yields a two-level namespace that maps naturally onto xRegistry: the
domain component of a module path is a Group, the remainder is a Resource, and
each published module version is a Version.

Two properties of the Go ecosystem drive this mapping and are addressed
explicitly below. First, module paths contain `/`, which is not a legal
xRegistry Entity ID character. Second, Go module versions are immutable by
construction: the checksum database makes any republication of a version
detectable, so the Version identity is genuinely content-stable.

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

**module path**: The canonical identifier of a Go module, such as
`github.com/pkg/errors`. Its first component is a domain name.

**GOPROXY**: The HTTP protocol by which Go tooling fetches module metadata and
content.

**checksum database**: An append-only transparency log recording the hash of
every module version, allowing tampering to be detected.

**pseudo-version**: A synthesized version such as
`v0.0.0-20210101000000-abcdef012345`, generated for a commit that carries no
semantic version tag. It encodes a UTC timestamp and a commit prefix.

**retraction**: A `retract` directive in a later `go.mod` declaring that a
range of earlier versions of the same module should not be selected.

**dirhash**: The `h1:` hash form recorded in `go.sum` and in the checksum
database: the base64 SHA-256 of a canonically formatted listing of the file
hashes of the artifact.

## 3. Registry Model

The formal xRegistry extension model of the Go Module Registry resides in the
[model.json](model.json) file. It declares one Group type, `goregistries`, and
one Resource type, `modules`.

The `module` Resource sets `hasdocument` to `false`. The module zip is
referenced by URL through `zip_url`.

For easy reference, the JSON serialization of a Go Module Registry adheres to
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

  "goregistriesurl": "<URL>",
  "goregistriescount": <UINTEGER>,
  "goregistries": {
    "<KEY>": {                                  # goregistryid, e.g. github.com
      "goregistryid": "<STRING>",               # xRegistry core attributes
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

      "modulesurl": "<URL>",
      "modulescount": <UINTEGER>,
      "modules": {
        "<KEY>": {                              # moduleid, e.g. pkg:errors
          "moduleid": "<STRING>",               # xRegistry core attributes
          "versionid": "<STRING>",              # e.g. v1.9.0
          "self": "<URL>",
          "shortself": "<URL>", ?
          "xid": "<XID>",

          # Start of default Version's attributes
          "epoch": <UINTEGER>,
          "name": "<STRING>", ?                 # canonical module path
          "description": "<STRING>", ?
          "documentation": "<URL>", ?
          "labels": { "<STRING>": "<STRING>" * }, ?
          "createdat": "<TIMESTAMP>",
          "modifiedat": "<TIMESTAMP>",
          "ancestor": "<STRING>",

          # Start of module extension attributes
          "modulepath": "<STRING>", ?           # e.g. github.com/pkg/errors

          "info_url": "<URL>", ?                # GOPROXY .info endpoint
          "mod_url": "<URL>", ?                 # GOPROXY .mod endpoint
          "zip_url": "<URL>", ?                 # GOPROXY .zip endpoint

          "gomod_hash": "<STRING>", ?           # go.sum h1: dirhash
          "zip_hash": "<STRING>", ?             # go.sum h1: dirhash

          "pseudo_version": <BOOLEAN>, ?        # e.g. v0.0.0-2021...-abcdef
          "pre_release": <BOOLEAN>, ?
          "incompatible": <BOOLEAN>, ?          # upstream +incompatible

          # go.mod directives of this version
          "go_version": "<STRING>", ?           # 'go' directive, e.g. 1.21.0
          "toolchain": "<STRING>", ?            # e.g. go1.21.4
          "require": [                          # 'require' directives
            {
              "path": "<STRING>",
              "version": "<STRING>",
              "indirect": <BOOLEAN> ?
            } *
          ], ?
          "replace": [                          # 'replace' directives
            {
              "old_path": "<STRING>",
              "old_version": "<STRING>", ?
              "new_path": "<STRING>",
              "new_version": "<STRING>" ?
            } *
          ], ?
          "exclude": [                          # 'exclude' directives
            { "path": "<STRING>", "version": "<STRING>" } *
          ], ?
          "retract": [                          # 'retract' directives
            {
              "low": "<STRING>",
              "high": "<STRING>",
              "rationale": "<STRING>" ?
            } *
          ], ?
          "godebug": { "<STRING>": "<STRING>" * }, ?
          "tool": [ "<STRING>" * ], ?
          "ignore": [ "<STRING>" * ], ?
          # End of module extensions and default Version's attributes

          "metaurl": "<URL>",
          "meta": {                             # module-wide facts
            # xRegistry core meta attributes
            "latest_version": "<STRING>", ?     # from the @latest endpoint
            "repository": "<URL>", ?            # VCS URL inferred from the path
            "major_version_suffix": "<STRING>", ?   # e.g. /v2
            "deprecated_message": "<STRING>", ? # from the go.mod comment
            "retractions": [                    # effective retracted ranges
              {
                "low": "<STRING>",
                "high": "<STRING>",
                "rationale": "<STRING>", ?
                "declared_in": "<STRING>" ?
              } *
            ] ?
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

There is no `dependencies` attribute. A Go build resolves dependencies by
minimal version selection over the whole module graph, so the requirements
listed in a single `go.mod` do not describe what a consumer will actually
build against; projecting them would assert a resolution that Go does not make.
The `require` directives are nevertheless projected verbatim, as directives,
by [Section 6.8](#68-gomod-directives).

Attributes that are facts about the module as a whole rather than about any one
published version — the latest version, the inferred repository, the major
version suffix, the deprecation notice and the effective retraction set — are
declared as Resource meta attributes and appear under `meta`, not on each
Version.

## 4. Identity Mapping

### 4.1. Group Identity

The `goregistryid` MUST be the first component of the canonical module path —
the domain — for example `github.com`, `golang.org` or `4d63.com`.

This is a *namespace*, not a registry service: module content for all such
namespaces is served by the same proxy. The Group nevertheless represents the
domain, because that is the only stable partitioning of the Go module namespace
and it matches how Go developers reason about module identity.

### 4.2. Resource Identity

The `moduleid` MUST be the remainder of the module path after the domain
component, with each remaining `/` separator replaced by `:`.

| Module path | `goregistryid` | `moduleid` |
|---|---|---|
| `github.com/pkg/errors` | `github.com` | `pkg:errors` |
| `github.com/pkg/errors/v2` | `github.com` | `pkg:errors:v2` |
| `golang.org/x/net` | `golang.org` | `x:net` |
| `4d63.com/biblepassageapi` | `4d63.com` | `biblepassageapi` |
| `example.com` | `example.com` | `@` |

A major-version suffix is part of the module path and is retained verbatim, as
the third row shows; see [Section 6.3](#63-major-version-suffixes).

The `:` substitution is collision-free: `/` is not a legal xRegistry Entity ID
character, and `:` is not a legal character in a Go module path, so no module
path can contain a `:` that would be mistaken for a separator. Percent-encoding
MUST NOT be used, because `%` is itself not a valid Entity ID character.

A module whose path is exactly a domain root has no remainder. Such a module
MUST use the reserved `moduleid` `@`, which cannot collide with any real path
component because `@` is not permitted in a Go module path.

Where the resulting `moduleid` would exceed the xRegistry limit of 128
characters, it MUST instead be `xh~` followed by the lowercase hex SHA-256 of
the UTF-8 bytes of the canonical module path. `xh~` is a reserved prefix and
MUST NOT be emitted otherwise.

The `moduleid` is an identifier, not an encoding, and consumers MUST NOT attempt
to recover the module path from it. The canonical module path MUST be preserved
in both the `name` and `modulepath` attributes, and consumers addressing a
module proxy MUST read `modulepath`.

### 4.3. Case Escaping

The GOPROXY protocol escapes uppercase ASCII letters in module paths by
prefixing them with `!` and lowercasing them, so that the protocol is safe on
case-insensitive filesystems:

```text
github.com/BurntSushi/toml  →  github.com/!burnt!sushi/toml
```

This escaping is a property of the *proxy transport*, not of module identity,
and `!` is not a valid xRegistry Entity ID character in any case. xRegistry
Entity IDs MUST therefore use the canonical, unescaped form, preserving the
original case. Implementations SHOULD additionally accept the escaped form on
input and resolve it to the canonical identity.

The problem that `!lower` solves does, however, apply here. An xRegistry
`<SINGULAR>id` MUST be unique *case-insensitively* within its parent, while Go
module paths are case-sensitive. Two module paths in the same namespace that
differ only in case therefore cannot both be represented by their canonical
form.

Such a collision is rare but MUST be handled deterministically rather than by
silently dropping a module. Where two or more module paths in one
`goregistry` differ only in case, the implementation MUST retain the canonical
form for the lexicographically smallest path and MUST assign every other
colliding path a `moduleid` of `xh~` followed by the lowercase hex SHA-256 of
the UTF-8 bytes of its canonical module path. Each module's true path remains
available in `modulepath` regardless of which form its identifier takes.

### 4.4. Version Identity

The `versionid` MUST be derived from the canonical Go version string, including
the leading `v`, for example `v1.2.3` or `v0.0.0-20210101000000-abcdef012345`.

Go permits build metadata introduced by `+`, notably the `+incompatible` suffix
applied to major versions at or above `v2` published without a module path
suffix. `+` is not a valid xRegistry Entity ID character, so each `+` MUST be
replaced by `~`, giving `v2.0.0~incompatible` for the upstream
`v2.0.0+incompatible`. Versions without build metadata are used verbatim.
Percent-encoding MUST NOT be used, because `%` is itself not a valid Entity ID
character.

`~` is a valid Entity ID character and cannot occur in a Go version string,
whose grammar admits only ASCII alphanumerics, `.`, `-` and `+`, so the
substitution is collision-free while leaving the identifier readable.

The `versionid` is an identifier, not an encoding, and consumers MUST NOT
attempt to recover the upstream version from it. The Version's `name` attribute
MUST carry the canonical Go version string exactly, and consumers addressing a
module proxy MUST read `name`.

Go module versions are immutable. Implementations MUST report published versions
as immutable Versions.

### 4.5. Timestamps

An implementation MUST set the core `createdat` attribute of a Version to the
`Time` value returned by the GOPROXY `@v/<version>.info` endpoint, and
`modifiedat` to the time of the most recent change to the projected metadata.

## 5. Group: `goregistry`

The Group (`<GROUP>`) name is `goregistry` (singular); the plural, used as the
collection name, is `goregistries`. A `goregistry` represents one Go module
namespace identified by a domain.

This extension defines no Group-level extension attributes beyond those
inherited from [xRegistry Core][xRegistry Core].

## 6. Resource: `module`

The Resource (`<RESOURCE>`) name is `module` (singular); the plural, used as the
collection name, is `modules`.

### 6.1. Identity Attributes

| xRegistry attribute | Type | Description |
|---|---|---|
| `name` | `string` | The canonical module path, e.g. `github.com/pkg/errors`. |
| `modulepath` | `string` | The canonical module path reconstructed from the Group and Resource identity, including any major-version suffix. Always equal to `name`; retained because it names the Go concept explicitly. |

### 6.2. Module-Wide Meta Attributes

Some facts describe the module, not a published version of it. They are declared
as Resource meta attributes and appear under `meta`.

| xRegistry meta attribute | Type | Description |
|---|---|---|
| `latest_version` | `string` | The canonical Go version reported by the proxy's `@latest` endpoint. |
| `repository` | `url` | The version control repository URL inferred from the module path. |
| `major_version_suffix` | `string` | The `/vN` suffix carried by the module path, e.g. `/v2`. Absent for `v0` and `v1` paths. |
| `deprecated_message` | `string` | The module deprecation notice. See [Section 6.4](#64-module-deprecation). |
| `retractions` | `array` | The effective set of retracted version ranges. See [Section 6.9](#69-retraction). |

`latest_version` and `repository` are properties of the module as a whole: a
Version does not have a "latest version", and every Version of a module resolves
to the same repository. Placing them on each Version would repeat one fact once
per Version and invite them to disagree.

`repository` is *inferred*, not authoritative: the Go module path encodes the
repository location by convention, but a module served through a vanity import
domain resolves indirectly. Implementations MUST omit `repository` rather than
guess when the mapping is not determinable.

### 6.3. Major Version Suffixes

From major version `v2` onwards, Go requires the major version to appear as a
`/vN` suffix on the module path itself. The consequence is that

```text
example.com/m        and        example.com/m/v2
```

are **distinct modules**, not two version ranges of one module. They have
distinct module paths, distinct import paths, may be built into the same binary
simultaneously, and have independent version streams.

This extension MUST therefore represent them as **distinct `module` Resources**.
Implementations MUST NOT merge `example.com/m/v2` into `example.com/m` as a
Version, and MUST NOT strip the suffix when deriving `moduleid` per
[Section 4.2](#42-resource-identity). The suffix, where present, MUST also be
reported in the `major_version_suffix` meta attribute so that consumers can
relate the major-version series of one module family without parsing paths.

The exception is a `v2`-or-higher version published from a repository that never
adopted the suffix; see `incompatible` in
[Section 6.7](#67-version-classification).

### 6.4. Module Deprecation

| xRegistry meta attribute | Type | Description |
|---|---|---|
| `deprecated_message` | `string` | The text following `Deprecated:` in the comment attached to the `module` directive. |

Go's deprecation channel is unusual: a module is marked deprecated not by a
directive, a proxy field or a registry flag, but by a **comment** immediately
preceding the `module` directive in `go.mod`:

```text
// Deprecated: use example.com/m/v2 instead.
module example.com/m
```

The Go toolchain parses this comment and surfaces it through `go list -m -u`.
A deprecation applies to the module, not to the version whose `go.mod` carries
it, and the toolchain reads it from the module's latest version. Implementations
MUST therefore take `deprecated_message` from the `go.mod` of the version named
by `latest_version`, and MUST record only the text after `Deprecated:`, with
surrounding whitespace trimmed.

The attribute is deliberately *not* named `deprecated`: the xRegistry core
already defines a `deprecated` object attribute, and reusing the name would
collide with it.

### 6.5. GOPROXY Endpoint Attributes

| xRegistry attribute | Type | GOPROXY endpoint | Description |
|---|---|---|---|
| `info_url` | `url` | `/{module}/@v/{version}.info` | Version metadata, including the commit timestamp. |
| `mod_url` | `url` | `/{module}/@v/{version}.mod` | The `go.mod` file for the version. |
| `zip_url` | `url` | `/{module}/@v/{version}.zip` | The module source archive. |

These URLs carry the escaped module path described in
[Section 4.3](#43-case-escaping), because that is what the GOPROXY protocol
requires.

Dependencies are not projected as a resolved dependency list. A module's
requirements live in its `go.mod`, retrievable through `mod_url` and projected
directive-by-directive in [Section 6.8](#68-gomod-directives); because Go uses
[minimal version selection][MVS], the `require` directives of a single module do
not by themselves describe the build graph, and presenting them as a resolved
dependency set would invite misinterpretation.

### 6.6. Checksum Attributes

| xRegistry attribute | Type | Description |
|---|---|---|
| `gomod_hash` | `string` | The `h1:` dirhash of the `go.mod` file. |
| `zip_hash` | `string` | The `h1:` dirhash of the module zip. |

Both values are the **`h1:` dirhash form used in `go.sum`** and recorded in the
checksum database, not an ad-hoc digest. The value MUST be carried verbatim,
including the `h1:` algorithm prefix, exactly as it appears in `go.sum`:

```text
example.com/m v1.2.3/go.mod h1:Kx0y8Z...=      →  gomod_hash
example.com/m v1.2.3       h1:9nQ1rT...=      →  zip_hash
```

`h1` denotes the base64-encoded SHA-256 of a canonically formatted listing of
the SHA-256 hashes of the artifact's files; it is not the SHA-256 of the zip or
of the `go.mod` bytes, and the two MUST NOT be confused.

These values are the integrity anchor for the version. Implementations MUST NOT
compute them locally and present them as though they came from the checksum
database; if the value was not obtained from the transparency log or from a
`go.sum` verified against it, the attribute MUST be omitted.

### 6.7. Version Classification

| xRegistry attribute | Type | Description |
|---|---|---|
| `pseudo_version` | `boolean` | Whether the version is a pseudo-version rather than a tagged release. |
| `pre_release` | `boolean` | Whether the version carries a SemVer pre-release segment. |
| `incompatible` | `boolean` | Whether the upstream version carries the `+incompatible` build-metadata suffix. |

A pseudo-version embeds a UTC timestamp in its second component. Implementations
SHOULD use that timestamp when ordering versions chronologically, since a
pseudo-version's SemVer precedence is deliberately low.

`+incompatible` marks a major version at or above `v2` that was published from a
repository whose module path does **not** carry the required `/vN` suffix. Go
accepts such a version under the unsuffixed module path, on the assumption that
the repository predates module support, and appends `+incompatible` as SemVer
build metadata to record that the module-path rule was not satisfied. The suffix
carries three consequences that implementations MUST respect:

1. The version belongs to the **unsuffixed** module path. `example.com/m` at
   `v2.0.0+incompatible` is a Version of the `example.com/m` Resource, and MUST
   NOT be moved to an `example.com/m/v2` Resource.
2. Go will not resolve an `+incompatible` version for a repository that contains
   a `go.mod` at the relevant tag; the two publication styles are mutually
   exclusive for a given major version.
3. `+` is not a legal xRegistry Entity ID character, so the `versionid` is
   `v2.0.0~incompatible` per [Section 4.4](#44-version-identity) while `name`
   retains `v2.0.0+incompatible`. `incompatible` is set to `true` so that
   consumers need not parse either string.

### 6.8. `go.mod` Directives

A version's `go.mod` is projected directive by directive. Every attribute in
this section describes **the `go.mod` of that Version**, and nothing else: it is
a faithful transcription, not a resolution.

| xRegistry attribute | Type | `go.mod` directive |
|---|---|---|
| `go_version` | `string` | `go` |
| `toolchain` | `string` | `toolchain` |
| `require` | `array` of `object` | `require` |
| `replace` | `array` of `object` | `replace` |
| `exclude` | `array` of `object` | `exclude` |
| `retract` | `array` of `object` | `retract` |
| `godebug` | `map` of `string` | `godebug` |
| `tool` | `array` of `string` | `tool` |
| `ignore` | `array` of `string` | `ignore` |

The `module` directive is not projected separately; it is the module path, and
is already carried by `name` and `modulepath`.

**`go_version`** records the language version named by the `go` directive, with
the leading `go` keyword removed, e.g. `1.21.0` for `go 1.21.0`. This is a
language-semantics selector, not merely a minimum toolchain: it governs which
language features and defaults apply when compiling the module's packages. A
`go.mod` with no `go` directive implies `1.16`; implementations MAY record the
implied value but MUST NOT invent a higher one.

**`toolchain`** records the `toolchain` directive, e.g. `go1.21.4` or `default`.
It names a *minimum toolchain* to be used when the invoking toolchain is older,
and is meaningful only in the main module.

**`require`** entries carry `path`, `version` and `indirect`. `indirect` is
`true` when the directive bears the `// indirect` comment, meaning the module is
in the build list but none of its packages are imported directly. These are
**minimum** versions consumed by minimal version selection, not pinned versions.

**`replace`** entries carry `old_path`, optional `old_version`, `new_path` and
optional `new_version`. `old_version` is absent when the directive replaces all
versions of the module; `new_version` is absent when the replacement target is a
local filesystem directory.

**`exclude`** entries carry `path` and `version` and remove a specific version
from consideration during version selection.

`replace`, `exclude`, `godebug` and `tool` are honoured **only when the module
is the main module** and are ignored when it is consumed as a dependency.
Implementations MUST project them regardless, because they describe the
version's `go.mod` accurately, but consumers MUST NOT treat them as constraints
imposed on downstream builds.

**`godebug`** is projected as a map from GODEBUG setting name to value, e.g.
`panicnil` → `1`.

**`tool`** lists package paths declared as tool dependencies of the main module.

**`ignore`** lists directory paths whose contents are excluded from the module's
file tree.

**`retract`** is described in [Section 6.9](#69-retraction).

### 6.9. Retraction

Retraction in Go is **not a flag on a version**. It is a `retract` directive,
declared in the `go.mod` of a *later* version of the same module, naming a
**range** of versions that should not be selected:

```text
retract v1.0.5                     // single version
retract [v1.1.0, v1.2.3]           // inclusive range
retract (
    v1.3.0                         // Contains a data race.
    [v1.4.0, v1.4.2]               // Published from the wrong branch.
)
```

Three properties follow, and they are why a boolean cannot express this:

1. Retraction is **range-valued**, not per-version. A single directive may
   retract versions that were never individually enumerated, including versions
   that do not exist.
2. Retraction is **declared elsewhere**. The `go.mod` of a retracted version is
   immutable and contains no record of its own retraction; a Version therefore
   *cannot know* that it is retracted. The information arrives only from a later
   version's `go.mod`, which a consumer must fetch separately.
3. Retraction can be **withdrawn** by publishing a further version that omits
   the directive, so the effective set is whatever the current highest
   non-retracted version declares — it is not cumulative history.

This extension models the two facts separately:

| Attribute | Scope | Type | Meaning |
|---|---|---|---|
| `retract` | Version | `array` of `object` | The `retract` directives *declared by* this Version's `go.mod`. |
| `retractions` | Resource meta | `array` of `object` | The *effective* retracted ranges for the module. |

Each `retract` entry carries `low`, `high` and optional `rationale`; `low`
equals `high` for a single-version retraction, and `rationale` is the comment
recorded with the directive. Entries in `retractions` carry the same fields plus
`declared_in`, the canonical Go version whose `go.mod` declared the range.

An implementation that populates `retractions` MUST compute it from the `go.mod`
of the module's highest non-retracted version, which is the same rule the Go
toolchain applies, and MUST set `declared_in` to that version. An implementation
that cannot determine the effective set MUST omit `retractions` rather than
approximate it; per-Version `retract` remains a faithful transcription in either
case.

A retracted version remains downloadable and MUST remain listed in the Versions
collection — retraction is advisory to version selection, not a deletion.
Implementations MUST NOT select a version covered by `retractions` as the
default Version when a version outside the retracted ranges exists.

## 7. Conformance

An implementation conforms to this specification when:

1. It serves a model equivalent to [`model.json`](model.json), and
2. it applies the identity mapping in [Section 4](#4-identity-mapping), and
3. every attribute it populates carries the meaning assigned in
   [Section 6](#6-resource-module).

An implementation MAY expose additional extension attributes. An implementation
MAY omit any attribute for which the upstream proxy supplies no value.

[xRegistry Core]: https://xregistry.io/xreg/xregistryspecs/core-v1/docs/spec.html
[Go modules]: https://go.dev/ref/mod
[GOPROXY]: https://go.dev/ref/mod#goproxy-protocol
[MVS]: https://go.dev/ref/mod#minimal-version-selection
