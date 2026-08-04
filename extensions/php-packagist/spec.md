# Composer / Packagist Registry Mapping - Version 1.0-rc1
<!-- words: autoload classmap composerregistries composerregistriescount -->
<!-- words: composerregistriesurl composerregistry composerregistryid -->
<!-- words: currentversion executables favers getcomposer gpl homepage irc -->
<!-- words: laravel licenseref namespace packageid packagepath -->
<!-- words: packagescount packagesurl packagist patreon php prebuilt psr -->
<!-- words: readme rss shasum sourcereference spdx symfony tidelift -->
<!-- words: untruncated vcs versionnormalized wiki xh -->

## Abstract

This specification defines an xRegistry extension that expresses the content of
[Packagist][Packagist], and any registry serving [Composer][Composer] package
metadata, in terms of the xRegistry document format and API
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
  - [4.4. Branch Alias Version Identity](#44-branch-alias-version-identity)
  - [4.5. Timestamps](#45-timestamps)
- [5. Group: `composerregistry`](#5-group-composerregistry)
- [6. Resource: `package`](#6-resource-package)
  - [6.1. Manifest Attributes](#61-manifest-attributes)
  - [6.2. Dependency Relations](#62-dependency-relations)
  - [6.3. Distribution and Source](#63-distribution-and-source)
  - [6.4. Autoloading, Binaries and Scripts](#64-autoloading-binaries-and-scripts)
  - [6.5. Support and Funding](#65-support-and-funding)
  - [6.6. Mutability](#66-mutability)
  - [6.7. Meta Attributes](#67-meta-attributes)
- [7. Conformance](#7-conformance)

## 1. Overview

Composer is the dependency manager for PHP, and Packagist is its principal
package repository. Every Composer package is named `vendor/package`, giving the
ecosystem a natural two-level namespace that maps directly onto xRegistry Groups
and Resources.

Composer's version model is unusual in two respects, both of which this
specification addresses explicitly. First, Composer packages expose *six*
distinct dependency-like relations — `require`, `require-dev`, `conflict`,
`replace`, `provide` and `suggest` — which express different graph semantics and
cannot be collapsed into one dependency list. Second, alongside immutable tagged
releases, Composer exposes mutable *branch aliases* such as `dev-main` that
track a moving VCS reference.

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

**vendor**: The first component of a Composer package name; the publishing
organization or individual.

**branch alias**: A Composer version of the form `dev-<branch>` that resolves to
the current tip of a VCS branch and therefore changes over time.

**virtual package**: A package name that is not published but is *provided* by
one or more real packages, used to express interface implementations.

**abandoned**: A Packagist marker declaring a package unmaintained, optionally
naming a replacement.

## 3. Registry Model

The formal xRegistry extension model of the Composer Package Registry resides in
the [model.json](model.json) file. It declares one Group type,
`composerregistries`, and one Resource type, `packages`, with `maxversions` of
`0`, `setversionid` and `singleversionroot` `true`, and `versionmode`
`createdat`. It constrains the spec-defined `defaultversionsticky` attribute to
`false`.

`versionmode` is `createdat`: Composer versions include non-SemVer branch
aliases, so publication time is the only total ordering available across the
whole Version set.

For easy reference, the JSON serialization of a Composer Package Registry
adheres to this form:

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

  "composerregistriesurl": "<URL>",
  "composerregistriescount": <UINTEGER>,
  "composerregistries": {
    "<KEY>": {                                  # composerregistryid = vendor
      "composerregistryid": "<STRING>",         # xRegistry core attributes
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

      # Group extension attribute
      "vendor": "<STRING>",                     # e.g. symfony

      "packagesurl": "<URL>",
      "packagescount": <UINTEGER>,
      "packages": {
        "<KEY>": {                              # packageid = basename, console
          "packageid": "<STRING>",              # xRegistry core attributes
          "versionid": "<STRING>",              # version, or <alias>:<ref>
          "self": "<URL>",
          "shortself": "<URL>", ?
          "xid": "<XID>",

          # Start of default Version's attributes
          "epoch": <UINTEGER>,
          "name": "<STRING>", ?                 # canonical vendor/package
          "description": "<STRING>", ?
          "documentation": "<URL>", ?
          "labels": { "<STRING>": "<STRING>" * }, ?
          "createdat": "<TIMESTAMP>",
          "modifiedat": "<TIMESTAMP>",
          "ancestor": "<STRING>",

          # Start of package extension attributes
          "vendor": "<STRING>", ?               # equal to the group ID
          "packagepath": "<STRING>", ?          # canonical vendor/package
          "type": "<STRING>", ?                 # library, project, ...
          "license": [ "<STRING>" * ], ?
          "homepage": "<STRING>", ?
          "repository": "<STRING>", ?           # VCS URL
          "keywords": [ "<STRING>" * ], ?
          "authors": [
            {
              "name": "<STRING>", ?
              "email": "<STRING>", ?
              "homepage": "<STRING>", ?
              "role": "<STRING>" ?
            } *
          ], ?
          "abandoned": <ANY>, ?                 # false, true, or replacement name

          "version": "<STRING>", ?              # normalized, e.g. 1.0.0, dev-main
          "versionnormalized": "<STRING>", ?    # Composer-normalized form
          "time": "<TIMESTAMP>", ?
          "immutable": <BOOLEAN>, ?             # true for tags, false for dev-*
          "sourcereference": "<STRING>", ?      # commit SHA or branch built from

          # Dependency relations: package name -> Composer constraint expression
          "require": { "<STRING>": "<STRING>" * }, ?
          "require_dev": { "<STRING>": "<STRING>" * }, ?
          "conflict": { "<STRING>": "<STRING>" * }, ?
          "replace": { "<STRING>": "<STRING>" * }, ?
          "provide": { "<STRING>": "<STRING>" * }, ?
          "suggest": { "<STRING>": "<STRING>" * }, ?   # values are free text

          "dist": {
            "url": "<STRING>", ?
            "type": "<STRING>", ?               # e.g. zip
            "shasum": "<STRING>", ?
            "reference": "<STRING>" ?
          }, ?
          "source": {
            "url": "<STRING>", ?
            "type": "<STRING>", ?               # e.g. git
            "reference": "<STRING>" ?           # no shasum: see 6.3
          }, ?

          "autoload": <ANY>, ?
          "autoload_dev": <ANY>, ?
          "bin": [ "<STRING>" * ], ?
          "scripts": <ANY>, ?                   # event -> string or [string]
          "support": {
            "email": "<STRING>", ?
            "issues": "<STRING>", ?
            "forum": "<STRING>", ?
            "wiki": "<STRING>", ?
            "irc": "<STRING>", ?
            "chat": "<STRING>", ?
            "source": "<STRING>", ?
            "docs": "<STRING>", ?
            "rss": "<STRING>", ?
            "security": "<STRING>" ?
          }, ?
          "funding": [
            {
              "type": "<STRING>", ?
              "url": "<STRING>" ?
            } *
          ], ?
          "extra": <ANY>, ?
          # End of package extensions and default Version's attributes

          "metaurl": "<URL>",
          "meta": {
            # ... xRegistry core Meta attributes ...

            # Package-wide meta attributes
            "downloads": {
              "total": <UINTEGER>, ?
              "monthly": <UINTEGER>, ?
              "daily": <UINTEGER> ?
            }, ?
            "favers": <UINTEGER>, ?
            "currentversion": "<STRING>", ?     # raw version shown on the Resource
            "readme": "<STRING>", ?
            "default_branch": "<STRING>" ?
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

The six dependency relations are kept separate. They express different
assertions — a requirement, a development-only requirement, an incompatibility,
a substitution, a virtual capability, and a suggestion — and are each typed as a
`map` of `string`, mirroring the upstream shape exactly. The map *values* are
not decomposed: Composer's constraint grammar (`||`, `,`, `!`, stability flags)
is richer than a decomposed representation would preserve.

## 4. Identity Mapping

### 4.1. Group Identity

The `composerregistryid` MUST be the Composer vendor name. The vendor is
additionally preserved in the Group-level `vendor` attribute.

Composer package names contain exactly one `/`, so this partitioning is total
and unambiguous. Packagist canonicalizes vendor names to lowercase.

### 4.2. Resource Identity

The `packageid` MUST be the package basename — the component after the `/`.

| Composer package | `composerregistryid` | `packageid` | Path |
|---|---|---|---|
| `symfony/console` | `symfony` | `console` | `/composerregistries/symfony/packages/console` |
| `laravel/framework` | `laravel` | `framework` | `/composerregistries/laravel/packages/framework` |

Both identifiers are slash-free by construction. The full canonical name MUST be
preserved in `name` and `packagepath`.

xRegistry Entity ID lookup is case-sensitive. A differently-cased identifier
MUST NOT be aliased to the canonical package.

### 4.3. Version Identity

For a tagged release, the `versionid` MUST be derived from the Composer version
string. Where that string is already a valid xRegistry Entity ID it MUST be used
unchanged.

Otherwise — that is, when the version carries `+` build metadata — each `+` MUST
be replaced by `~`, giving `1.0.0~20130313144700` for the upstream
`1.0.0+20130313144700`. Percent-encoding MUST NOT be used, because `%` is itself
not a valid Entity ID character. If the resulting identifier would exceed the
128-character limit, the `versionid` MUST instead be `xh~` followed by the
lowercase hex SHA-256 of the UTF-8 bytes of the raw version string. `xh~` is a
reserved prefix; an implementation MUST NOT emit a `versionid` beginning with
`xh~` in any other circumstance.

`~` is a valid Entity ID character and cannot occur in a Composer version
string, so the substitution is collision-free while leaving the identifier
readable.

The `versionid` is an identifier, not an encoding, and consumers MUST NOT
attempt to recover the upstream version from it. The raw upstream value MUST be
preserved in `version`, and the Composer-normalized form in
`versionnormalized`; consumers addressing Packagist itself MUST read `version`.

Tagged releases are immutable; `immutable` MUST be `true` for them.

### 4.4. Branch Alias Version Identity

A `dev-*` branch alias does not identify fixed content: the same alias resolves
to different commits over time. Its identity therefore has to incorporate both the
alias and the source reference it currently denotes.

The `versionid` for a branch alias MUST be constructed as:

```text
<alias>:<full-source-reference>
```

where `<alias>` is the raw alias with each `/` replaced by `~`, and
`<full-source-reference>` is the complete, untruncated source reference. For the
alias `dev-feature/login` at commit `a1b2c3d4...`, this gives
`dev-feature~login:a1b2c3d4...`.

Both `:` and `~` are valid xRegistry Entity ID characters, and Git forbids both
in a reference name, so neither can occur inside `<alias>` or
`<full-source-reference>` and the construction is collision-free. It does not
depend on truncating the commit reference, so two branches whose names coincide
after substitution, or two commits sharing a short prefix, remain distinct.
Percent-encoding MUST NOT be used, because `%` is itself not a valid Entity ID
character.

If that identifier would exceed the xRegistry 128-character Entity ID limit, the
identifier MUST instead be `xh~` followed by the lowercase hex SHA-256 of the
UTF-8 bytes of `alias + "/" + full-source-reference`.

The `versionid` is an identifier, not an encoding, and consumers MUST NOT
attempt to recover the alias or reference from it. In all cases the raw alias
MUST remain available in `version` and the full reference in `sourcereference`,
so no information is lost.

`immutable` MUST be `false` for branch aliases.

Older, truncated dev-version identifiers are not aliases of these identifiers.
Consumers holding stale identifiers MUST rediscover the Versions collection.

### 4.5. Timestamps

An implementation MUST set the core `createdat` attribute of a Version to the
Packagist `time` value of that release, and `modifiedat` to the time of the most
recent change to the projected metadata. For a branch alias, `modifiedat` MUST
advance whenever the alias resolves to a different source reference.

## 5. Group: `composerregistry`

The Group (`<GROUP>`) name is `composerregistry` (singular); the plural, used as
the collection name, is `composerregistries`. A `composerregistry` represents
one Composer vendor namespace.

| Group attribute | Type | Description |
|---|---|---|
| `vendor` | `string` | The canonical Composer vendor name; equal to the `composerregistryid`. |

## 6. Resource: `package`

The Resource (`<RESOURCE>`) name is `package` (singular); the plural, used as
the collection name, is `packages`.

### 6.1. Manifest Attributes

| xRegistry attribute | Type | `composer.json` field | Description |
|---|---|---|---|
| `name` | `string` | `name` | Canonical `vendor/package` name. |
| `vendor` | `string` | — | The vendor component. |
| `packagepath` | `string` | — | The canonical `vendor/package` path on the registry. |
| `description` | `string` | `description` | Short description of the package. |
| `type` | `string` | `type` | Composer package type, e.g. `library`, `project`, `symfony-bundle`. Determines installer behaviour. |
| `license` | `array` of `string` | `license` | Declared licenses. Composer permits an array, so this is not collapsed to a single expression. See below. |
| `homepage` | `string` | `homepage` | Project homepage URL. |
| `repository` | `string` | — | VCS repository URL. |
| `keywords` | `array` of `string` | `keywords` | Descriptive keywords. |
| `authors` | `array` of `object` | `authors` | Authors: `name`, `email`, `homepage`, `role`. |
| `abandoned` | `any` | `abandoned` | `false`, `true`, or the name of a suggested replacement package. |
| `extra` | `any` | `extra` | Arbitrary publisher-defined data. |
| `version` | `string` | `version` | Raw upstream version string. |
| `versionnormalized` | `string` | — | The Composer-normalized version string. |
| `time` | `timestamp` | `time` | RFC 3339 release timestamp of the version. |

Composer RECOMMENDS that each entry of `license` be an [SPDX][SPDX] license
identifier, such as `MIT`, `Apache-2.0` or `GPL-3.0-or-later`, and publishers
SHOULD emit them in that form. Multiple entries denote a disjunctive choice: the
consumer MAY select any one of them. Values that are not SPDX identifiers do
occur — most commonly `proprietary`, and custom identifiers carrying the SPDX
`LicenseRef-` prefix — and an implementation MUST preserve them verbatim rather
than discarding or normalizing them. This specification does not define a
license expression grammar; a value MUST be treated as an opaque identifier.

`abandoned` is typed `any` because Composer overloads it: a boolean means "no
replacement named", a string names the replacement. Coercing it to a boolean
would discard the replacement, and coercing it to a string would fabricate one.

### 6.2. Dependency Relations

Composer defines six relations. They are retained as separate attributes
because each has different resolver semantics:

| xRegistry attribute | Type | Semantics |
|---|---|---|
| `require` | `map` of `string` | Packages that MUST be installed alongside this one. |
| `require_dev` | `map` of `string` | Packages needed only when developing this package. |
| `conflict` | `map` of `string` | Versions of other packages that MUST NOT be installed alongside this one. |
| `replace` | `map` of `string` | Packages this one replaces; installing this satisfies those names. |
| `provide` | `map` of `string` | Virtual package names this package implements. |
| `suggest` | `map` of `string` | Packages suggested to the consumer but not installed. |

Five of the six carry the upstream `composer.json` field name verbatim.
`require-dev` cannot, because xRegistry attribute names are restricted to
`[a-z0-9_]`, so it is projected as `require_dev`. The rename is confined to the
attribute name; the map keys and values are untouched.

Each is a `map` whose keys are package names. This is the exact upstream shape,
so the attributes are structurally typed rather than opaque. The map *values*
are `string` and MUST be preserved verbatim: for the first five relations they
are Composer version constraint expressions, which support boolean operators
(`||`, `,`), stability suffixes and range operators; decomposing them into a
structured form would either lose the boolean structure or require this
specification to define a constraint grammar it does not own. `replace` values
MAY additionally be the literal `self.version`. `suggest` is the one exception
to the value semantics: its values are free-text explanations addressed to a
human, not constraints, and MUST NOT be parsed as such.

### 6.3. Distribution and Source

```yaml
"dist": {
  "url": "STRING",        # download URL of the packaged archive
  "type": "STRING",       # archive type, e.g. "zip"
  "shasum": "STRING",     # checksum of the archive
  "reference": "STRING"   # VCS reference the archive was built from
},
"source": {
  "url": "STRING",        # VCS repository URL
  "type": "STRING",       # VCS type, e.g. "git"
  "reference": "STRING"   # commit reference
}
```

`dist` describes the prebuilt archive Composer prefers to download; `source`
describes the VCS checkout used when `--prefer-source` is requested. They can
point at different hosts and MUST NOT be conflated.

The two objects are deliberately *not* symmetric. `dist` carries a `shasum`
over the archive bytes; `source` has no `shasum`, because Composer publishes
none — a VCS checkout is identified by its `reference`, which is already a
content-addressed commit identifier for Git. An implementation MUST NOT
synthesize a `source.shasum`.

`sourcereference` additionally carries the full VCS reference as a top-level
attribute, in lowercase form. It is REQUIRED for branch aliases, where it is the
only value distinguishing one materialization of the alias from another.

### 6.4. Autoloading, Binaries and Scripts

| xRegistry attribute | Type | `composer.json` field | Description |
|---|---|---|---|
| `autoload` | `any` | `autoload` | Autoload rules in the upstream representation. |
| `autoload_dev` | `any` | `autoload-dev` | Autoload rules applied only when developing this package, e.g. for the test suite. |
| `bin` | `array` of `string` | `bin` | Package-relative paths to executables Composer links into the vendor binary directory. |
| `scripts` | `any` | `scripts` | Event hooks, keyed by Composer event name. |

`autoload` and `autoload_dev` are typed `any` and are structured identically to
each other. Both are genuinely union-typed: under `psr-4` and `psr-0` a
namespace prefix maps either to a single path string or to an array of path
strings, while `classmap`, `files` and `exclude-from-classmap` are arrays. A
single structural type cannot describe this without loss.

`scripts` is typed `any` for the same reason: the value of an event key is
either one callable or command string, or an array of them.

`bin` is a plain array of strings upstream and is typed accordingly.

### 6.5. Support and Funding

| xRegistry attribute | Type | `composer.json` field | Description |
|---|---|---|---|
| `support` | `object` | `support` | Support channels: `email`, `issues`, `forum`, `wiki`, `irc`, `chat`, `source`, `docs`, `rss`, `security`. |
| `funding` | `array` of `object` | `funding` | Funding channels, each with `type` (e.g. `github`, `patreon`, `tidelift`, `other`) and `url`. |

`support.email` is an email address and every other `support` member is a URL;
both are typed `string` because Composer applies no scheme restriction beyond
`irc`, which is conventionally an `irc://` URL. Unknown `support` members MAY be
present upstream and MAY be dropped.

### 6.6. Mutability

The `immutable` attribute is a `boolean` reporting whether the Version's content
is fixed. It MUST be `true` for tagged releases and `false` for `dev-*` branch
aliases. Consumers MUST NOT cache a Version with `immutable` set to `false` as
though it were content-addressed.

### 6.7. Meta Attributes

The following are declared as Resource `metaattributes` because they describe
the package as a whole:

| xRegistry attribute | Type | Description |
|---|---|---|
| `downloads` | `object` | Download statistics: `total`, `monthly`, `daily`, each `uinteger`. |
| `favers` | `uinteger` | Number of users who have marked the package as a favorite. |
| `currentversion` | `string` | The raw Composer version selected for display on the Resource. |
| `readme` | `string` | The rendered package README as published by Packagist. |
| `default_branch` | `string` | The VCS branch Packagist treats as the package default, e.g. `main`. |

Download counts and favorite counts are cardinalities and can never be
negative, so they are typed `uinteger` rather than `integer`.

`readme` and `default_branch` are Resource-level rather than Version-level:
Packagist publishes exactly one of each per package, not one per release.
`default_branch` names the branch whose `dev-` alias is the package's moving
head; it is a branch name, not a `versionid`.

## 7. Conformance

An implementation conforms to this specification when:

1. It serves a model equivalent to [`model.json`](model.json), and
2. it applies the identity mapping in [Section 4](#4-identity-mapping), and
3. every attribute it populates carries the meaning assigned in
   [Section 6](#6-resource-package).

An implementation MAY expose additional extension attributes. An implementation
MAY omit any attribute for which the upstream registry supplies no value.

[xRegistry Core]: https://xregistry.io/xreg/xregistryspecs/core-v1/docs/spec.html
[Packagist]: https://packagist.org/
[Composer]: https://getcomposer.org/
[SPDX]: https://spdx.org/licenses/
