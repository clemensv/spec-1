# npm Package Registry Mapping - Version 1.0-rc1
<!-- words: bundledependencies devdependencies filecount homepage -->
<!-- words: installability installable linux nodescope nodescopeid -->
<!-- words: nodescopes nodescopescount nodescopesurl npmjs npmrc -->
<!-- words: optionaldependencies packageid packagescount packagesurl -->
<!-- words: packuments peerdependencies pgp replacedby shasum sourceurl -->
<!-- words: spdx subresource tarball unpackedsize unscoped xh -->

## Abstract

This specification defines an xRegistry extension that expresses the content of
the [npm][npm registry] package registry, and any registry that implements the
npm registry API, in terms of the xRegistry document format and API
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
- [5. Group: `nodescope`](#5-group-nodescope)
- [6. Resource: `package`](#6-resource-package)
  - [6.1. Attribute Mapping](#61-attribute-mapping)
  - [6.2. Dependency Cross-References](#62-dependency-cross-references)
  - [6.3. Distribution](#63-distribution)
  - [6.4. Installability Constraints](#64-installability-constraints)
- [7. Conformance](#7-conformance)

## 1. Overview

npm is the package registry for the Node.js ecosystem. A npm registry serves
package documents ("packuments") that carry package-level metadata together
with a map of published versions, each of which is an immutable release of the
package.

The npm data model maps onto xRegistry as follows: a scope is a Group, a
package is a Resource, and a published release is a Version of that Resource.
This specification records that mapping normatively so that clients can consume
npm metadata through a uniform xRegistry interface, and so that independent
implementations produce interoperable documents.

The Group is the scope rather than the registry host because the scope is the
only part of npm's model that partitions the name space: a scope exists
precisely so that two publishers can use the same package name without
conflict. The registry host does not participate in package identity — npm
packuments are registry-agnostic, and selecting a registry is client
configuration (`.npmrc`) rather than a property of the package — so a Group
keyed on the host would be a degenerate single-member container that partitions
nothing. Because most npm packages are unscoped and share one flat global name
space, the reserved scope `_` holds exactly those packages; see
[Section 4.1](#41-group-identity). The registry host is recorded, where it
matters, in the Group's `sourceurl` attribute.

This specification is descriptive of an existing ecosystem. It does not modify
npm, does not define a publishing protocol, and does not require an npm
registry to change. It defines how npm metadata is *projected* into xRegistry.

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

**npm registry**: A service implementing the npm registry HTTP API, such as
the public registry at `registry.npmjs.org`.

**package**: A named unit of distribution in the npm ecosystem. Package names
are lowercase and MAY be *scoped*, taking the form `@scope/name`.

**version**: An immutable, published release of a package, identified by a
[Semantic Versioning][semver] string.

**dist-tag**: A mutable, human-assigned alias (such as `latest` or `next`)
pointing at one published version.

## 3. Registry Model

The formal xRegistry extension model of the Node.js Package Registry resides in
the [model.json](model.json) file. It declares one Group type,
`nodescopes`, and one Resource type, `packages`.

The `package` Resource sets `hasdocument` to `false`. An npm package version is
described entirely by its metadata attributes; the distributable tarball is not
the xRegistry Resource document and is instead referenced, together with its
integrity data, by the REQUIRED `dist` attribute described in
[Section 6.3](#63-distribution).

For easy reference, the JSON serialization of a Node.js Package Registry
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

  "nodescopesurl": "<URL>",
  "nodescopescount": <UINTEGER>,
  "nodescopes": {
    "<KEY>": {                                  # nodescopeid, e.g. babel or _
      "nodescopeid": "<STRING>",                # xRegistry core attributes
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
        "<KEY>": {                              # packageid, e.g. express
          "packageid": "<STRING>",              # xRegistry core attributes
          "versionid": "<STRING>",              # the npm version, e.g. 4.18.2
          "self": "<URL>",
          "shortself": "<URL>", ?
          "xid": "<XID>",

          # Start of default Version's attributes
          "epoch": <UINTEGER>,
          "name": "<STRING>", ?                 # canonical npm package name
          "description": "<STRING>", ?
          "documentation": "<URL>", ?
          "labels": { "<STRING>": "<STRING>" * }, ?
          "createdat": "<TIMESTAMP>",
          "modifiedat": "<TIMESTAMP>",
          "ancestor": "<STRING>",

          # Start of package extension attributes
          "version": "<STRING>", ?              # same value as versionid
          "dist": {                             # REQUIRED
            "tarball": "<URL>",                 # REQUIRED
            "shasum": "<STRING>", ?
            "integrity": "<STRING>", ?
            "file_count": <UINTEGER>, ?
            "unpacked_size": <UINTEGER>, ?
            "npm_signature": "<STRING>" ?
          },
          "license": "<STRING>", ?
          "author": {                           # person object
            "name": "<STRING>", ?
            "email": "<STRING>", ?
            "url": "<URL>" ?
          }, ?
          "homepage": "<URL>", ?
          "repository": { <JSON-VALUE> }, ?     # e.g. { "type", "url" }
          "bugs": { <JSON-VALUE> }, ?
          "engines": { "<STRING>": "<STRING>" * }, ?
          "os": [ "<STRING>" * ], ?             # e.g. linux, !win32
          "cpu": [ "<STRING>" * ], ?            # e.g. x64, !arm
          "keywords": [ "<STRING>" * ], ?
          "maintainers": [ { <PERSON> } * ], ?
          "contributors": [ { <PERSON> } * ], ?
          "dist_tags": { "<STRING>": "<STRING>" * }, ?  # e.g. latest, next
          "deprecated_message": "<STRING>", ?

          "dependencies": [
            {
              "name": "<STRING>",               # dependency package name
              "version": "<STRING>", ?          # semver range, e.g. ^1.0.0
              "package": "<XID>" ?              # -> /nodescopes/packages
            } *
          ], ?
          "dev_dependencies": [ { ... } * ], ?  # same item shape as above
          "peer_dependencies": [ { ... } * ], ? # same item shape as above
          "optional_dependencies": [ { ... } * ], ? # same item shape as above
          "bundle_dependencies": [
            {
              "name": "<STRING>",               # bundled package name
              "package": "<XID>" ?              # -> /nodescopes/packages
            } *
          ], ?

          "replacedby": "<XID>", ?              # -> /nodescopes/packages
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

The `nodescopeid` MUST be the npm scope of the packages it contains, written
**without** the leading `@`. For example, the packages `@babel/core` and
`@babel/parser` both belong to the Group `babel`.

The leading `@` MUST be stripped rather than encoded. `@` is a valid xRegistry
Entity ID character but MUST NOT be the first character of an Entity ID, and the
`@` is a fixed sigil that carries no information, so removing it is lossless.

Unscoped packages belong to a single flat, global name space rather than to any
scope. They MUST be placed in the reserved Group whose `nodescopeid` is `_`.
`_` is a valid Entity ID starting character and is not a valid npm scope, so the
reserved Group cannot collide with a real scope. A Group with `nodescopeid` `_`
MUST NOT declare the `scope` attribute, since its members belong to no scope.

This mapping is total and collision-free: `@a/x` and `@b/x` are distinct
packages and land in distinct Groups, while the unscoped `x` is a third distinct
package in the reserved Group.

Scopes are permanent for a given package name. A package published as
`@scope/name` cannot later become unscoped, nor move to another scope, so a
package's Group \u2014 and therefore its `xid` \u2014 is stable for the lifetime of the
package.

### 4.2. Resource Identity

The `packageid` MUST be the npm package name with any scope prefix removed \u2014
that is, the portion after the `/` for a scoped package, and the whole name for
an unscoped package. For example, `@babel/core` yields the `packageid` `core`
within the Group `babel`, and `express` yields the `packageid` `express` within
the reserved Group `_`.

Splitting the name at the `/` is what makes the mapping work without encoding:
the `/` is the Group/Resource boundary and never appears in either component.
The remaining characters of an npm package name are all valid xRegistry Entity
ID characters. Percent-encoding MUST NOT be used, because `%` is itself not a
valid Entity ID character.

An npm package name cannot exceed 214 characters in total, so the unscoped
portion MAY exceed the xRegistry Entity ID limit of 128 characters. Where it
does, the `packageid` MUST be `xh~` followed by the lowercase hex SHA-256 of the
UTF-8 bytes of that unscoped portion. `xh~` is a reserved prefix and MUST NOT be
emitted otherwise.

The canonical, unmodified npm package name \u2014 including its `@scope/` prefix
where present \u2014 MUST be preserved in the `name` attribute regardless of the
Group placement and encoding applied.

Package names are case-sensitive for lookup, consistent with the xRegistry Core
[`<SINGULAR>id`][xRegistry singularid] rules. A request whose `packageid`
differs from the canonical name only by case MUST NOT be treated as an alias.

### 4.3. Version Identity

The `versionid` MUST be derived from the npm version string. Semantic Version
strings that contain build metadata (`+`) are not valid xRegistry Entity IDs.

A version containing build metadata MUST have each `+` replaced by `~`, giving
`1.0.0~20130313144700` for the upstream `1.0.0+20130313144700`. Versions without
build metadata are used verbatim. Percent-encoding MUST NOT be used, because `%`
is itself not a valid Entity ID character.

`~` is a valid Entity ID character and cannot occur in a Semantic Version, whose
grammar admits only ASCII alphanumerics, `.`, `-` and `+`, so the substitution
is collision-free while leaving the identifier readable.

The `versionid` is an identifier, not an encoding, and consumers MUST NOT
attempt to recover the upstream version from it. The exact upstream string MUST
be preserved in the `version` attribute, and consumers addressing the npm
registry MUST read `version`.

Published npm versions are immutable. Implementations MUST report published
versions as immutable Versions. The `latest` dist-tag determines the default
Version; because a publisher can move a dist-tag, the default Version is not
sticky.

### 4.4. Timestamps

The npm `time` object records a publication timestamp per version, plus
`created` and `modified` entries for the package as a whole. An implementation
MUST set the core `createdat` attribute of a Version to that version's `time`
entry, and the Resource's `createdat` and `modifiedat` to `time.created` and
`time.modified` respectively.

## 5. Group: `nodescope`

The Group (`<GROUP>`) name is `nodescope` (singular); the plural, used as
the collection name, is `nodescopes`. A `nodescope` represents one npm scope,
or — for the reserved Group `_` — the flat global name space of unscoped
packages.

| xRegistry attribute | Type | Description |
|---|---|---|
| `scope` | `string` | OPTIONAL. The npm scope this Group represents, without the leading `@`, e.g. `babel`. Its value is identical to the `nodescopeid`. It MUST be absent on the reserved Group `_`, whose members belong to no scope. |
| `sourceurl` | `url` | OPTIONAL. Base URL of the registry from which the scope was projected, e.g. `https://registry.npmjs.org`. This records provenance only; npm packuments are registry-agnostic and a package name denotes the same package whichever registry serves it. |

## 6. Resource: `package`

The Resource (`<RESOURCE>`) name is `package` (singular); the plural, used as
the collection name, is `packages`.

### 6.1. Attribute Mapping

The following table maps npm package metadata fields (as served by the npm
registry API, ultimately originating in `package.json`) to the extension
attributes declared in [`model.json`](model.json).

| xRegistry attribute | Type | npm source | Description |
|---|---|---|---|
| `name` | `string` | `name` | Canonical npm package name, including the scope for scoped packages. |
| `description` | `string` | `description` | The package summary. This is the xRegistry core `description` attribute; no extension attribute is defined for it. |
| `version` | `string` | `version` | The version this projection describes. |
| `dist` | `object` | `dist` | REQUIRED. Tarball location and integrity data, see [6.3](#63-distribution). |
| `license` | `string` | `license` | SPDX license expression under which the package is distributed. |
| `author` | `object` | `author` | Package author as a person object (`name`, `email`, `url`). |
| `homepage` | `url` | `homepage` | Project homepage URL. |
| `repository` | `object` | `repository` | Source repository descriptor (`type`, `url`). |
| `bugs` | `object` | `bugs` | Issue tracker descriptor. |
| `keywords` | `array` of `string` | `keywords` | Free-form descriptive keywords. |
| `maintainers` | `array` of `object` | `maintainers` | Accounts authorized to publish the package, as person objects. |
| `contributors` | `array` of `object` | `contributors` | Declared contributors, as person objects. |
| `engines` | `object` | `engines` | Runtime version constraints, principally `node`. |
| `os` | `array` of `string` | `os` | Permitted operating systems, see [6.4](#64-installability-constraints). |
| `cpu` | `array` of `string` | `cpu` | Permitted CPU architectures, see [6.4](#64-installability-constraints). |
| `dist_tags` | `object` | `dist-tags` | Mutable tag-to-version aliases as published by the registry. |
| `deprecated_message` | `string` | `deprecated` | Deprecation notice; presence indicates the package or version is deprecated. |
| `dependencies` | `array` of `object` | `dependencies` | Runtime dependencies, see [6.2](#62-dependency-cross-references). |
| `dev_dependencies` | `array` of `object` | `devDependencies` | Development-time dependencies. |
| `peer_dependencies` | `array` of `object` | `peerDependencies` | Peer dependencies. |
| `optional_dependencies` | `array` of `object` | `optionalDependencies` | Dependencies whose installation failure is not fatal. |
| `bundle_dependencies` | `array` of `object` | `bundleDependencies` | Dependencies bundled inside the published tarball. |
| `replacedby` | `xid` | — | Cross-reference to the `package` Resource that supersedes this one, when a replacement has been identified. |

xRegistry attribute names MUST consist only of the characters `[a-z0-9_]`, so
the camel-cased npm field names `devDependencies`, `peerDependencies`,
`optionalDependencies` and `bundleDependencies` cannot be used verbatim. They
are projected as `dev_dependencies`, `peer_dependencies`,
`optional_dependencies` and `bundle_dependencies` respectively; the same rule
applies to `fileCount` and `unpackedSize` within `dist`. The hyphen is likewise
outside the permitted set, so the upstream `dist-tags` and `dist.npm-signature`
field names are projected as `dist_tags` and `dist.npm_signature`. The rename
applies to the attribute name only; the *keys* within `dist_tags` are map keys,
not attribute names, and implementations MUST reproduce them verbatim from the
registry document, because clients match tag names against them.

npm's `deprecated` field is projected as `deprecated_message` because
`deprecated` is a spec-defined xRegistry attribute of type object. When the npm
field is present the implementation MUST also set the core `deprecated`
attribute, at minimum to `{}`, so that generic xRegistry clients observe the
deprecation without understanding this extension.

npm represents `dependencies`, `devDependencies`, `peerDependencies` and
`optionalDependencies` as JSON objects mapping a package name to a version
range, and `bundleDependencies` as a bare array of package names. This
specification projects all five as arrays of objects so that each entry can
additionally carry a resolved xRegistry cross-reference.

`author`, `maintainers` and `contributors` all describe people, and the npm
registry serves all three as objects carrying `name`, `email` and `url`. They
are therefore modelled with a single common shape. Where an upstream
`package.json` writes the author in the abbreviated string form
`Name <email> (url)`, the implementation MUST project the parsed components
into the corresponding sub-attributes.

### 6.2. Dependency Cross-References

Each entry of `dependencies`, `dev_dependencies`, `peer_dependencies` and
`optional_dependencies` has the following shape:

```yaml
{
  "name": "STRING",     # the dependency package name
  "version": "STRING",  # the npm version range, e.g. "^1.0.0"
  "package": "XID" ?    # xRegistry reference to the dependency
}
```

- `name` MUST be the npm name of the depended-upon package.
- `version` MUST be the version range exactly as declared upstream. It is a
  *range*, not a resolved version, and MUST NOT be rewritten.
- `package` is an `xid` targeting `/nodescopes/packages`. It MAY be omitted
  when the target cannot be resolved within this registry.

Each entry of `bundle_dependencies` has the same shape without `version`,
because the upstream `bundleDependencies` field is a list of names only and
carries no range; the bundled code is inside the tarball and its version is
whatever was bundled at publication time.

The presence of `package` allows a consumer to traverse the dependency graph
using xRegistry navigation rather than re-implementing npm range resolution.

### 6.3. Distribution

The npm registry guarantees that every published version document carries
`name`, `version` and `dist`. `dist` is the only part of the document that says
where the artifact can be obtained and how the bytes can be verified, so the
`dist` attribute is REQUIRED on every Version, as is its `tarball`
sub-attribute.

| Sub-attribute | Type | npm source | Description |
|---|---|---|---|
| `tarball` | `url` | `dist.tarball` | REQUIRED. URL of the published tarball for this version. |
| `shasum` | `string` | `dist.shasum` | Lowercase hex SHA-1 digest of the tarball. |
| `integrity` | `string` | `dist.integrity` | Subresource Integrity string, e.g. `sha512-…`. |
| `file_count` | `uinteger` | `dist.fileCount` | Number of files in the tarball. |
| `unpacked_size` | `uinteger` | `dist.unpackedSize` | Size in bytes of the tarball contents once unpacked. |
| `npm_signature` | `string` | `dist.npm-signature` | Detached PGP signature over the name, version and integrity value. |

`shasum` is present on every published version and `integrity` is present for
versions published by npm 5 and later; an implementation MUST project whichever
of the two the registry supplies, and MUST NOT compute a substitute value. A
consumer verifying a download SHOULD prefer `integrity` where both are present.

The `dist` values MUST be projected verbatim. In particular, `tarball` MUST NOT
be rewritten to point at a mirror or proxy, because `shasum`, `integrity` and
`npm_signature` are assertions about the bytes served from the recorded URL.

### 6.4. Installability Constraints

`os` and `cpu` declare the platforms on which a version can be installed. An
entry names a value of Node.js's `process.platform` or `process.arch`
respectively; an entry prefixed with `!` excludes that value instead of
admitting it. When either attribute is absent, the version places no constraint
on that dimension.

These attributes are projected verbatim, including the `!` prefix, and MUST NOT
be normalized into a different constraint syntax. Together with `engines`, they
are what a client needs in order to decide whether a version is installable on
a given host before fetching its tarball.

## 7. Conformance

An implementation conforms to this specification when:

1. It serves a model equivalent to [`model.json`](model.json), and
2. it applies the identity mapping in [Section 4](#4-identity-mapping), and
3. every attribute it populates carries the meaning assigned in
   [Section 6.1](#61-attribute-mapping).

An implementation MAY expose additional extension attributes. An implementation
MAY omit any attribute for which the upstream registry supplies no value.

[xRegistry Core]: https://xregistry.io/xreg/xregistryspecs/core-v1/docs/spec.html
[xRegistry singularid]: https://xregistry.io/xreg/xregistryspecs/core-v1/docs/spec.html#singularid-id-attribute
[npm registry]: https://docs.npmjs.com/cli/v10/using-npm/registry
[semver]: https://semver.org/
