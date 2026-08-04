# NuGet Package Registry Mapping - Version 1.0-rc1
<!-- words: advisoryurl alternatepackage criticalbugs cvss dependencygroups -->
<!-- words: dotnetregistries dotnetregistriescount dotnetregistriesurl -->
<!-- words: dotnetregistry dotnetregistryid dotnettool homepage iconurl -->
<!-- words: licenseexpression licenseurl lowercased minclientversion -->
<!-- words: newtonsoft nuget nupkg nuspec oid packagecontent packageid -->
<!-- words: packagescount packagesurl packagetypes projecturl pypi readme -->
<!-- words: readmeurl repositorysignatures requirelicenseacceptance -->
<!-- words: sourceurl spdx -->
<!-- words: targetframework tfm tfms tolowerinvariant totaldownloads -->
<!-- words: unlisting -->

## Abstract

This specification defines an xRegistry extension that expresses the content of
[nuget.org][nuget.org], and any registry implementing the NuGet V3 API, in terms
of the xRegistry document format and API [specification][xRegistry Core].

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
- [5. Group: `dotnetregistry`](#5-group-dotnetregistry)
  - [5.1. Repository Signatures](#51-repository-signatures)
- [6. Resource: `package`](#6-resource-package)
  - [6.1. Attribute Mapping](#61-attribute-mapping)
  - [6.2. Package-Level Attributes](#62-package-level-attributes)
  - [6.3. Dependencies and Target Frameworks](#63-dependencies-and-target-frameworks)
  - [6.4. Listing State and Publication](#64-listing-state-and-publication)
  - [6.5. Deprecation](#65-deprecation)
  - [6.6. Vulnerabilities](#66-vulnerabilities)
  - [6.7. Absent Values](#67-absent-values)
- [7. Conformance](#7-conformance)

## 1. Overview

NuGet is the package registry for the .NET ecosystem. Package metadata
originates in a `.nuspec` manifest embedded in each package and is served
through the NuGet V3 registration and search APIs.

This specification maps that model into xRegistry: a NuGet source is a Group, a
package identity is a Resource, and a published package version is a Version.

The distinguishing feature of the NuGet dependency model is that dependencies
are declared per *target framework* group: the same package can require
different dependencies when consumed by `net8.0` than when consumed by
`netstandard2.0`. This specification preserves that dimension explicitly rather
than discarding it.

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

**package ID**: The name of a NuGet package. Package IDs are compared
case-insensitively by NuGet clients but are stored and displayed in the casing
chosen by the publisher.

**target framework moniker (TFM)**: An identifier such as `net8.0` or
`netstandard2.0` denoting a .NET platform a package supports.

**version range**: The NuGet [interval notation][version ranges] constraining a
dependency, for example `[1.0.0, 2.0.0)` or the shorthand `1.0.0` meaning
"1.0.0 or higher".

## 3. Registry Model

The formal xRegistry extension model of the .NET Package Registry resides in
the [model.json](model.json) file. It declares one Group type,
`dotnetregistries`, and one Resource type, `packages`.

The `package` Resource sets `hasdocument` to `false`. The distributable
`.nupkg` is therefore not served as the Resource document; it is referenced by
the `package_content` attribute, which carries the upstream `packageContent`
URL of the registration leaf. `package_content` is the only reference to the
artifact this projection defines, so an implementation that has the URL MUST
populate it.

For easy reference, the JSON serialization of a .NET Package Registry adheres
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

  "dotnetregistriesurl": "<URL>",
  "dotnetregistriescount": <UINTEGER>,
  "dotnetregistries": {
    "<KEY>": {                                  # dotnetregistryid, nuget
      "dotnetregistryid": "<STRING>",           # xRegistry core attributes
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

      "sourceurl": "<URL>", ?                  # V3 service index of this feed
      "all_repository_signed": <BOOLEAN>, ?
      "repository_signing_certificates": [
        {
          "subject": "<STRING>",
          "issuer": "<STRING>",
          "fingerprint_sha256": "<STRING>",
          "not_before": "<TIMESTAMP>",
          "not_after": "<TIMESTAMP>",
          "content_url": "<URL>"
        } *
      ], ?

      "packagesurl": "<URL>",
      "packagescount": <UINTEGER>,
      "packages": {
        "<KEY>": {                              # packageid, e.g. newtonsoft.json
          "packageid": "<STRING>",              # xRegistry core attributes
          "versionid": "<STRING>",              # NuGet version, "+" -> "~"
          "self": "<URL>",
          "shortself": "<URL>", ?
          "xid": "<XID>",

          # Start of default Version's attributes
          "epoch": <UINTEGER>,
          "name": "<STRING>", ?                 # package ID, owner's casing
          "description": "<STRING>", ?
          "documentation": "<URL>", ?
          "labels": { "<STRING>": "<STRING>" * }, ?
          "createdat": "<TIMESTAMP>",
          "modifiedat": "<TIMESTAMP>",
          "ancestor": "<STRING>",

          # Start of package extension attributes
          "version": "<STRING>", ?              # verbatim upstream version
          "title": "<STRING>", ?
          "authors": [ "<STRING>" * ], ?
          "summary": "<STRING>", ?
          "language": "<STRING>", ?
          "icon_url": "<URL>", ?
          "readme_url": "<URL>", ?
          "license_url": "<URL>", ?             # deprecated upstream
          "license_expression": "<STRING>", ?
          "require_license_acceptance": <BOOLEAN>, ?
          "project_url": "<URL>", ?
          "package_content": "<URL>", ?         # the .nupkg artifact
          "min_client_version": "<STRING>", ?
          "listed": <BOOLEAN>, ?
          "published": "<TIMESTAMP>", ?         # 1900 == unlisted sentinel
          "tags": [ "<STRING>" * ], ?

          "package_types": [                    # Dependency, DotnetTool, ...
            {
              "name": "<STRING>",
              "version": "<STRING>" ?
            } *
          ], ?

          "repository": {                       # build provenance
            "type": "<STRING>", ?
            "url": "<URL>", ?
            "branch": "<STRING>", ?
            "commit": "<STRING>" ?
          }, ?

          "deprecation": {                      # present only if deprecated
            "reasons": [ "<STRING>" * ], ?
            "message": "<STRING>", ?
            "alternate_package": {
              "id": "<STRING>", ?
              "range": "<STRING>", ?
              "package": "<XID>" ?             # -> /dotnetregistries/packages
            } ?
          }, ?

          "vulnerabilities": [
            {
              "advisory_url": "<URL>", ?
              "severity": <UINTEGER> ?          # 0 low .. 3 critical
            } *
          ], ?

          "dependencies": [                     # flattened across frameworks;
            {                                   #   "name" is NOT unique here
              "name": "<STRING>",
              "range": "<STRING>", ?            # a version range
              "target_framework": "<STRING>", ? # e.g. .NETStandard2.0, or any
              "resolved_version": "<STRING>", ? # only when resolved exactly
              "package": "<XID>" ?              # -> /dotnetregistries/packages
            } *
          ], ?
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

A Group is one **projection** of an ecosystem's package metadata into
xRegistry. The `dotnetregistryid` names that projection. For packages projected
from the NuGet V3 metadata model the `dotnetregistryid` MUST be `nuget`.

The identifier is deliberately not a feed, a host or an account. A registry that
serves NuGet packages from the public service, from a mirror, from an internal
proxy or from a private feed uses the same `nuget` Group, so that
`/dotnetregistries/nuget/packages/<packageid>` denotes the same package wherever
it is served.

See [Section 4.1.1](#411-projection-identity-rules) for the rules that govern
this identifier.

#### 4.1.1. Projection Identity Rules

- The identifier MUST be stable across every deployment that serves the same
  projection, and MUST NOT vary by serving host, tenancy or access level. An
  implementation MUST NOT derive it from a DNS name, a URL authority or an
  account name. This is what allows one registry to shadow another: a package
  served from an air-gapped mirror MUST present the same path as the same
  package served from the public service.
- Where NuGet introduces a metadata model that cannot be projected into the
  attributes defined in this specification without loss or contradiction, that
  model MUST be given a new Group identifier, for example `nuget-v4`. Both
  Groups MAY then coexist in one registry, and a client selects the model it
  understands instead of being handed attributes whose meaning has silently
  changed.
- Where two parties project this ecosystem under incompatible interpretations,
  each MUST use a distinct Group identifier. A Group therefore identifies the
  ecosystem together with the reading of it that produced the entries, and two
  entries in the same Group are directly comparable.

Access control is a property of the registry deployment rather than of the
identifier. A registry that exposes only a private feed's packages still exposes
them under `nuget`, and MAY omit entries the caller is not entitled to see; a
caller MUST NOT infer from an entry's absence that it does not exist upstream.
Where entries drawn from different feeds are served together, the `sourceurl`
attribute records which service each Group's entries were projected from.

### 4.2. Resource Identity

The `packageid` MUST be the NuGet package ID, lowercased. NuGet package IDs are
restricted to ASCII letters, digits, `.`, `-` and `_`, all of which are valid
xRegistry Entity ID characters, so no encoding is needed.

NuGet treats package IDs case-insensitively while xRegistry Entity ID lookup is
case-sensitive, so a canonical casing MUST be chosen. That casing MUST be the
lowercase form produced by `ToLowerInvariant`, which is the same normalization
the NuGet V3 API applies when it constructs registration and package content
URLs from `LOWER_ID`. A `packageid` of `newtonsoft.json` therefore addresses
the package whose owner publishes it as `Newtonsoft.Json`, and a
differently-cased request MUST NOT be silently aliased to it.

The casing published by the owner is not discarded: it MUST be preserved in the
core `name` attribute, which carries the package ID exactly as the owner
declared it.

### 4.3. Version Identity

The `versionid` MUST be derived from the package version string. NuGet versions
follow [SemVer 2.0.0][semver], extended with a fourth "revision" component.

`+` is not a valid xRegistry Entity ID character, so each `+` in a version
containing build metadata MUST be replaced by `~`, giving `1.0.0~build.5` for
the upstream `1.0.0+build.5`. Versions without build metadata are used verbatim.
Percent-encoding MUST NOT be used, because `%` is itself not a valid Entity ID
character.

`~` is a valid Entity ID character and cannot occur in a NuGet version string,
whose grammar admits only ASCII alphanumerics, `.`, `-` and `+`, so the
substitution is collision-free while leaving the identifier readable.

The `versionid` is an identifier, not an encoding, and consumers MUST NOT
attempt to recover the upstream version from it. The exact upstream string MUST
be preserved in the `version` attribute, and consumers addressing nuget.org
MUST read `version`.

Published NuGet versions are immutable. A version MAY be *unlisted*, which hides
it from search while leaving it downloadable; unlisting does not alter the
artifact and does not change the `versionid`. The listing state is carried by
the `listed` and `published` attributes described in
[Section 6.4](#64-listing-state-and-publication).

### 4.4. Timestamps

An implementation MUST set the core `createdat` attribute of a Version to the
NuGet `published` value for that version, and `modifiedat` to the time of the
most recent change to the projected metadata.

Where the source reports the year 1900 as the `published` value, that value is a
sentinel for "unlisted" rather than a date. An implementation MUST NOT copy the
sentinel into `createdat`; it MUST instead omit the sentinel from `createdat`,
surface it verbatim in the extension attribute `published`, and report the
listing state through `listed`. See
[Section 6.4](#64-listing-state-and-publication).

## 5. Group: `dotnetregistry`

The Group (`<GROUP>`) name is `dotnetregistry` (singular); the plural, used as
the collection name, is `dotnetregistries`. A `dotnetregistry` represents one
projection of the NuGet metadata model into xRegistry. Its identifier names that
projection rather than the service that serves it. See
[Section 4.1](#41-group-identity) for how the identifier is formed.

This extension defines the following Group-level extension attributes, in
addition to those inherited from [xRegistry Core][xRegistry Core]:

| xRegistry attribute | Type | Description |
|---|---|---|
| `sourceurl` | `url` | Base URL of the feed these packages were projected from, for example `https://api.nuget.org/v3/index.json`. Provenance only. |
| `all_repository_signed` | `boolean` | Whether every package the feed serves carries a repository signature. |
| `repository_signing_certificates` | `array` of `object` | The certificates the feed uses to repository-sign packages, see [5.1](#51-repository-signatures). |

### 5.1. Repository Signatures

NuGet distinguishes two signatures on a `.nupkg`. An *author* signature is
applied by the publisher before upload. A *repository* signature is applied by
the feed. The two answer different questions: the author signature attests who
built the package, the repository signature attests which feed accepted and
served it.

Only the repository signature is described by the V3 protocol, through the
[`RepositorySignatures`][RepositorySignatures] resource of the service index.
That resource is a property of the feed, not of any package, which is why it is
projected onto the Group and not onto a Resource or Version. Each entry has the
following shape:

```yaml
{
  "subject": "STRING",                 # subject distinguished name
  "issuer": "STRING",                  # issuer distinguished name
  "fingerprint_sha256": "STRING",      # lowercase hex SHA-256
  "not_before": "TIMESTAMP",
  "not_after": "TIMESTAMP",
  "content_url": "URL"                 # DER-encoded public certificate
}
```

The upstream `fingerprints` object is keyed by hash algorithm OID, and
`2.16.840.1.101.3.4.2.1` — SHA-256 — is the only key the protocol requires. An
attribute name MUST match `[a-z0-9_]`, so the OID cannot be carried as a key
here; the value is projected as `fingerprint_sha256` instead. An implementation
that encounters a further OID MUST NOT discard the SHA-256 value in favour of
it.

Certificates are appended to the upstream list as older ones expire, so the
array MAY contain entries whose validity period has passed; those remain
meaningful because packages signed under them are still served. Removal of a
certificate upstream invalidates the signatures made with it, so an
implementation MUST NOT retain an entry the feed has stopped advertising.

This specification defines **no** author signing certificate attribute. The V3
protocol exposes no author signature metadata at all: it is carried inside the
`.nupkg` and is verified by the client against the artifact. An implementation
MUST NOT synthesize an author certificate subject by opening the artifact and
reading its signature, because the resulting value would assert a verification
the registry never performed and a consumer could not distinguish it from one
the feed had vouched for. A consumer that requires author identity MUST fetch
`package_content` and verify the signature itself.

## 6. Resource: `package`

The Resource (`<RESOURCE>`) name is `package` (singular); the plural, used as
the collection name, is `packages`.

### 6.1. Attribute Mapping

| xRegistry attribute | Type | NuGet source | Description |
|---|---|---|---|
| `name` | `string` | `id` | The NuGet package ID, in the casing published by the owner. |
| `description` | `string` | `description` | Full package description. |
| `title` | `string` | `title` | Display title, where the publisher supplied one. |
| `summary` | `string` | `summary` | Short summary, where the publisher supplied one distinct from `description`. |
| `version` | `string` | `version` | The version this projection describes, verbatim. |
| `authors` | `array` of `string` | `authors` | Declared authors, see below. |
| `tags` | `array` of `string` | `tags` | Descriptive tags, see below. |
| `language` | `string` | `language` | Locale identifier, for example `en-US`. |
| `icon_url` | `url` | `iconUrl` | URL of the package icon. |
| `readme_url` | `url` | `readmeUrl` | URL of the rendered README document. |
| `license_url` | `url` | `licenseUrl` | URL of the license document. Deprecated upstream. |
| `license_expression` | `string` | `licenseExpression` | SPDX license expression declared by the package. |
| `require_license_acceptance` | `boolean` | `requireLicenseAcceptance` | Whether the license has to be accepted before installation. |
| `project_url` | `url` | `projectUrl` | Project homepage URL. |
| `package_content` | `url` | `packageContent` | URL of the `.nupkg` artifact for this version. |
| `min_client_version` | `string` | `minClientVersion` | Minimum NuGet client version needed. |
| `listed` | `boolean` | listing state | Whether the version is visible to search, see [6.4](#64-listing-state-and-publication). |
| `published` | `timestamp` | `published` | Upstream publication value, see [6.4](#64-listing-state-and-publication). |
| `package_types` | `array` of `object` | `packageTypes` | Declared package types, see below. |
| `repository` | `object` | `repository` | Source repository provenance, see below. |
| `deprecation` | `object` | `deprecation` | Deprecation record, see [6.5](#65-deprecation). |
| `vulnerabilities` | `array` of `object` | `vulnerabilities` | Known advisories, see [6.6](#66-vulnerabilities). |
| `dependencies` | `array` of `object` | `dependencyGroups` | Dependencies, see [6.3](#63-dependencies-and-target-frameworks). |

`name` and `description` are xRegistry Core attributes. `name` carries the
NuGet package ID and `description` the full package description; this extension
does not redefine them. Because `packageid` is lowercased
([Section 4.2](#42-resource-identity)), `name` is the only place the owner's
chosen casing survives, and it MUST NOT be lowercased.

The camel-cased NuGet field names cannot be used verbatim, because xRegistry
attribute names MUST match `[a-z0-9_]`. `iconUrl`, `readmeUrl`, `licenseUrl`,
`licenseExpression`, `requireLicenseAcceptance`, `projectUrl`,
`packageContent`, `minClientVersion`, `packageTypes`, `advisoryUrl`,
`alternatePackage` and `targetFramework` are therefore projected as `icon_url`,
`readme_url`, `license_url`, `license_expression`,
`require_license_acceptance`, `project_url`, `package_content`,
`min_client_version`, `package_types`, `advisory_url`, `alternate_package` and
`target_framework`. Snake case is applied uniformly, at every nesting depth, so
that no object mixes conventions.

`license_url` is deprecated upstream in favour of `license_expression`.
Implementations MAY populate `license_url` when the source supplies it, but
MUST NOT synthesize it from a license expression, and MUST NOT omit
`license_expression` when the source supplies one: the expression is the
authoritative license statement and the URL is the legacy fallback.

`authors` and `tags` are both returned by the NuGet API as either a single
string or an array of strings, and both are therefore projected as an `array`
of `string`. The apparent asymmetry between them is only in how a single string
is normalized:

- `tags` is space separated upstream and a NuGet tag cannot contain whitespace,
  so splitting a single string on whitespace is unambiguous and MUST be done.
- `authors` is comma separated by convention only, and NuGet defines no way to
  escape a comma occurring inside an author name such as `Contoso, Inc.`. A
  single string MUST therefore be carried as one array element verbatim and
  MUST NOT be split.

`package_types` carries the upstream `packageTypes` array; each entry has a
`name`, typically `Dependency`, `DotnetTool` or `Template`, and a `version`
that can be absent. NuGet treats a package that declares no package type as a
`Dependency` package, but an implementation MUST omit `package_types` rather
than synthesize that default.

`repository` carries the `.nuspec` `repository` element as an object with
`type`, `url`, `branch` and `commit` members, recording the source revision the
package was built from.

### 6.2. Package-Level Attributes

The following are `metaattributes`, because they describe the package as a
whole rather than any single version:

| xRegistry attribute | Type | NuGet source | Description |
|---|---|---|---|
| `owners` | `array` of `string` | `owners` | The nuget.org account names that own the package. |
| `total_downloads` | `uinteger` | `totalDownloads` | Cumulative download count across all versions, reported by the source. |
| `verified` | `boolean` | `verified` | Whether the source considers the package ID prefix reserved and verified. |

`owners` is deliberately *not* mapped to the Group. nuget.org does not derive
ownership from the `authors` metadata in the `.nuspec` file; it assigns
ownership to the account that published the package, a package MAY be co-owned
by several accounts, owners MAY be added and removed at any time, and a package
MAY at times have no active owner. Ownership is therefore neither single-valued
nor total, so it cannot partition the package name space. NuGet package IDs are
flat and globally unique regardless of who owns them, and ownership is recorded
here as provenance metadata only.

`total_downloads` and `verified` are registry-operator statistics, not package
manifest data. They MUST be omitted when the source does not supply them rather
than defaulted to `0` or
`false`, which would assert a fact not in evidence. The general form of this
rule is stated in [Section 6.7](#67-absent-values).

### 6.3. Dependencies and Target Frameworks

NuGet groups dependencies by target framework. This specification flattens those
groups into a single array in which each entry names its framework, so that the
per-framework information is retained without requiring nested collections.

Each entry of `dependencies` has the following shape:

```yaml
{
  "name": "STRING",                # dependency package ID
  "range": "STRING",               # NuGet version range
  "target_framework": "STRING",    # TFM, or "any" for the framework-agnostic group
  "package": "XID" ?,              # xRegistry reference to the dependency
  "resolved_version": "STRING" ?   # exact version, when resolvable
}
```

- `range` MUST be the declared range in NuGet interval notation, not a resolved
  version. It carries the upstream field name, which the NuGet V3 registration
  document also calls `range`. It is deliberately not called `version`: a
  dependency constraint and the enclosing Resource's `version` attribute are
  different kinds of value, and reusing the name invited them to be conflated.
  Keeping the upstream name follows the same rule these extensions apply
  elsewhere, as with the npm `dist-tags` field, whose upstream name likewise
  MUST NOT be renamed.
- `target_framework` MUST be the TFM of the dependency group. The literal `any`
  is a sentinel defined by this specification and is **not** an upstream value;
  NuGet represents the framework-agnostic group as an absent or empty
  `targetFramework`. Implementations MUST emit `any` for that group and MUST
  NOT emit an empty string, so that a consumer never has to distinguish
  "applies to every framework" from "the field was not populated". A consumer
  MUST NOT treat `any` as a TFM that can be matched against a project's target.
- A package that depends on the same package ID under two different TFMs
  produces two entries that differ in `target_framework`. Consumers MUST NOT
  assume `name` is unique within the array.
- `package` is an `xid` targeting `/dotnetregistries/packages`.
- `resolved_version` MUST be present only when the range was resolved to an
  exact published version.

Member names inside this object, and inside every other object this extension
defines, use snake case throughout: `target_framework` and `resolved_version`
follow the same convention as the single-word members `name`, `range` and
`package`, so the object does not mix naming styles.

### 6.4. Listing State and Publication

A NuGet version MAY be *unlisted*: it disappears from search results and from
the package's version list on the gallery, but remains downloadable at its
`package_content` URL for consumers that already reference it. Unlisting is the
closest NuGet equivalent of a removal and is the state a consumer needs to know
about in order to explain why a version cannot be discovered.

| xRegistry attribute | Type | NuGet source | Description |
|---|---|---|---|
| `listed` | `boolean` | listing state | `true` when the version is visible to search, `false` when it is unlisted. |
| `published` | `timestamp` | `published` | The upstream publication value, verbatim. |

nuget.org does not expose a `listed` field on the registration leaf. It signals
unlisting by reporting a `published` value in the year 1900, conventionally
`1900-01-01T00:00:00Z`. An implementation projecting nuget.org:

- MUST set `listed` to `false` when the upstream `published` year is 1900, and
  to `true` otherwise;
- MUST surface the upstream value verbatim in `published`, sentinel included,
  so that the derivation remains auditable;
- MUST NOT copy the sentinel into the core `createdat` attribute, which is a
  real timestamp, see [Section 4.4](#44-timestamps).

A source that publishes an explicit listing flag MUST use it in preference to
the sentinel. A source that supplies neither MUST omit `listed`; it MUST NOT be
defaulted to `true`.

### 6.5. Deprecation

NuGet allows a package owner to deprecate individual versions, giving a reason,
a message, and optionally a replacement package. This is a first-class upstream
channel, comparable to npm's deprecation field and to PyPI's `yanked` flag, and
it is projected as the `deprecation` object:

```yaml
{
  "reasons": [ "STRING" * ], ?     # Legacy | CriticalBugs | Other | ...
  "message": "STRING", ?           # owner-supplied free text
  "alternate_package": {           # suggested replacement
    "id": "STRING", ?
    "range": "STRING", ?           # NuGet interval notation, "*" = any
    "package": "XID" ?             # -> /dotnetregistries/packages
  } ?
}
```

- The **presence** of `deprecation` is the deprecation signal. It MUST be
  omitted for a version that is not deprecated, and MUST NOT be emitted as an
  empty object, which would assert a deprecation the source did not report.
- `reasons` carries the upstream reason codes. nuget.org defines `Legacy`,
  `CriticalBugs` and `Other`, but the set is open: a value outside it MUST be
  carried verbatim rather than discarded or remapped.
- `alternate_package.range` uses the upstream field name, as in
  [Section 6.3](#63-dependencies-and-target-frameworks). The upstream wildcard
  `*` means any version of the replacement.
- `alternate_package.package` is an `xid` targeting
  `/dotnetregistries/packages` and MAY be populated when the replacement is
  present in the same registry.

The attribute is named `deprecation` rather than `deprecated` because
[xRegistry Core][xRegistry Core] already defines a `deprecated` object on
entities, and an extension MUST NOT collide with it.

### 6.6. Vulnerabilities

nuget.org reports known security advisories per version on the registration
leaf. They are projected as the `vulnerabilities` array:

```yaml
{
  "advisory_url": "URL", ?         # advisory describing the vulnerability
  "severity": UINTEGER ?           # 0 low, 1 moderate, 2 high, 3 critical
}
```

- `severity` is transmitted upstream as a numeric string on the nuget.org scale
  and is projected as a `uinteger` on that same scale. Implementations MUST NOT
  rescale it to another vocabulary; a consumer that needs CVSS or another
  severity model MUST obtain it from the advisory identified by
  `advisory_url`.
- `vulnerabilities` MUST be omitted when the source supplies no vulnerability
  data. An empty array asserts that the version is known to carry no
  advisories, and MUST be emitted only when the source makes that assertion.
  Absence of data and absence of advisories are different facts.

### 6.7. Absent Values

Every count, timestamp, boolean and collection this specification defines is
OPTIONAL. When the source does not supply a value, an implementation MUST omit
the attribute rather than emit a type-appropriate zero value — `0` for a count,
`false` or `true` for a boolean, an empty array for a collection — which would
assert a fact not in evidence.

This applies at least to `total_downloads`, `verified`,
`require_license_acceptance`, `listed`, `published`, `package_types`,
`repository`, `deprecation` and `vulnerabilities`, and to any further attribute
a profile of this specification adds.

## 7. Conformance

An implementation conforms to this specification when:

1. It serves a model equivalent to [`model.json`](model.json), and
2. it applies the identity mapping in [Section 4](#4-identity-mapping), and
3. every attribute it populates carries the meaning assigned in
   [Section 6](#6-resource-package).

An implementation MAY expose additional extension attributes. An implementation
MAY omit any attribute for which the upstream source supplies no value.

[xRegistry Core]: https://xregistry.io/xreg/xregistryspecs/core-v1/docs/spec.html
[nuget.org]: https://www.nuget.org/
[version ranges]: https://learn.microsoft.com/en-us/nuget/concepts/package-versioning#version-ranges
[semver]: https://semver.org/
[RepositorySignatures]: https://learn.microsoft.com/en-us/nuget/api/repository-signatures-resource
