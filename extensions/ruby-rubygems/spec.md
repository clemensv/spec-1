# RubyGems Registry Mapping - Version 1.0-rc1
<!-- words: changelog gemspec homepage jruby licenseref linux mfa nokogiri -->
<!-- words: packageid packagescount packagesurl prereqs rubygems -->
<!-- words: rubyregistries rubyregistriescount rubyregistriesurl -->
<!-- words: rubyregistry rubyregistryid rz sigstore sourceurl spdx wiki xh -->

## Abstract

This specification defines an xRegistry extension that expresses the content of
[RubyGems.org][RubyGems], and any registry implementing the RubyGems API, in
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
  - [4.3. Version Identity and Platform Builds](#43-version-identity-and-platform-builds)
  - [4.4. Timestamps](#44-timestamps)
- [5. Group: `rubyregistry`](#5-group-rubyregistry)
- [6. Resource: `package`](#6-resource-package)
  - [6.1. Gemspec Attributes](#61-gemspec-attributes)
  - [6.2. Version Attributes](#62-version-attributes)
  - [6.3. Resolution Constraints](#63-resolution-constraints)
  - [6.4. Dependencies](#64-dependencies)
  - [6.5. The `metadata` Hash and Declared URIs](#65-the-metadata-hash-and-declared-uris)
  - [6.6. Meta Attributes](#66-meta-attributes)
  - [6.7. Retrieval Cost and Availability](#67-retrieval-cost-and-availability)
- [7. Conformance](#7-conformance)

## 1. Overview

RubyGems is the package registry for the Ruby ecosystem. A *gem* is the unit of
distribution; its metadata originates in a gemspec and is served through the
RubyGems JSON API.

This specification maps that model into xRegistry: a gem registry is a Group, a
gem is a Resource, and a published gem release is a Version.

The distinguishing characteristic of RubyGems is that a single version number
can correspond to several published builds differing only by *platform* — for
example `nokogiri 1.19.4` exists as a pure-Ruby build, as a JRuby (`java`)
build, and as several precompiled native builds, eleven platforms in all under
one version number. Version identity must therefore incorporate the platform,
which [Section 4.3](#43-version-identity-and-platform-builds) addresses.

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

**gem**: A named unit of distribution in the Ruby ecosystem.

**platform**: The build target of a gem release. `ruby` denotes a pure-Ruby
build usable everywhere; other values such as `x86_64-linux` or
`arm64-darwin` denote precompiled native builds. `java` denotes a JRuby build.

**yank**: A registry operation removing a version from resolution while leaving
already-installed copies intact.

**requirement**: A RubyGems version constraint such as `>= 1.0, < 2.0` or
`~> 3.1`.

## 3. Registry Model

The formal xRegistry extension model of the Ruby Gem Registry resides in the
[model.json](model.json) file. It declares one Group type, `rubyregistries`,
and one Resource type, `packages`, with `maxversions` of `0`, `setversionid`
and `singleversionroot` `true`, and `versionmode` `createdat`. It constrains
the spec-defined `defaultversionsticky` attribute to `false`.

`versionmode` is `createdat` rather than `semver`: because platform builds share
a version number, SemVer precedence alone does not totally order the Versions,
whereas publication time does. `defaultversionsticky` is constrained to `false`
so that a newly published release advances the default Version.

For easy reference, the JSON serialization of a Ruby Gem Registry adheres to
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

  "rubyregistriesurl": "<URL>",
  "rubyregistriescount": <UINTEGER>,
  "rubyregistries": {
    "<KEY>": {                                  # rubyregistryid, rubygems
      "rubyregistryid": "<STRING>",             # xRegistry core attributes
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

      "sourceurl": "<URL>", ?                  # base URL of this gem source

      "packagesurl": "<URL>",
      "packagescount": <UINTEGER>,
      "packages": {
        "<KEY>": {                              # packageid, e.g. nokogiri
          "packageid": "<STRING>",              # xRegistry core attributes
          "versionid": "<STRING>",              # version, or version-platform
          "self": "<URL>",
          "shortself": "<URL>", ?
          "xid": "<XID>",

          # Start of default Version's attributes
          "epoch": <UINTEGER>,
          "name": "<STRING>", ?                 # canonical gem name
          "description": "<STRING>", ?          # gemspec description (long)
          "documentation": "<URL>", ?
          "labels": { "<STRING>": "<STRING>" * }, ?
          "createdat": "<TIMESTAMP>",
          "modifiedat": "<TIMESTAMP>",
          "ancestor": "<STRING>",

          # Start of package extension attributes
          "info": "<STRING>", ?                 # gemspec summary (one line)
          "version": "<STRING>", ?              # latest stable version
          "number": "<STRING>", ?               # normalized version, no '-'
          "platform": "<STRING>", ?             # e.g. ruby, java, x86_64-linux
          "full_name": "<STRING>", ?            # e.g. nokogiri-1.19.4-java
          "authors": "<STRING>", ?              # comma-separated
          "licenses": [ "<STRING>" * ], ?       # nullable; SPDX only advised
          "gem_uri": "<STRING>", ?              # direct .gem download URL
          "sha": "<STRING>", ?                  # SHA-256 of the .gem file
          "spec_sha": "<STRING>", ?             # SHA-256 of the .gemspec.rz
          "ruby_version": "<STRING>", ?         # required_ruby_version
          "rubygems_version": "<STRING>", ?     # required_rubygems_version
          "requirements": [ "<STRING>" * ], ?   # free-form external prereqs
          "prerelease": <BOOLEAN>, ?
          "yanked": <BOOLEAN>, ?                # MAY be absent, see 6.7
          "created_at": "<TIMESTAMP>", ?        # registry publication time
          "built_at": "<TIMESTAMP>", ?          # publisher-asserted build time
          "version_downloads": <UINTEGER>, ?    # downloads of latest version
          "downloads_count": <UINTEGER>, ?      # downloads of this version

          "homepage_uri": "<STRING>", ?         # per-release gemspec metadata
          "source_code_uri": "<STRING>", ?
          "changelog_uri": "<STRING>", ?
          "documentation_uri": "<STRING>", ?
          "bug_tracker_uri": "<STRING>", ?
          "metadata": { "<STRING>": "<STRING>" * }, ?  # open, verbatim hash

          "attestations": [
            { "media_type": "<STRING>", "bundle": { ... } } *
          ], ?

          "dependencies": {                     # split is significant
            "runtime": [
              { "name": "<STRING>", "requirements": "<STRING>" } *
            ], ?
            "development": [
              { "name": "<STRING>", "requirements": "<STRING>" } *
            ] ?
          }, ?                                  # MAY be absent, see 6.7
          # End of package extensions and default Version's attributes

          "metaurl": "<URL>",
          "meta": {
            # ... xRegistry core Meta attributes ...

            # Package-wide meta attributes
            "project_uri": "<STRING>", ?        # registry-synthesized URL
            "downloads": <UINTEGER>, ?          # total across all versions
            "reverse_dependencies": [ "<STRING>" * ] ?
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
xRegistry. The `rubyregistryid` names that projection. For gems projected from
the RubyGems metadata model the `rubyregistryid` MUST be `rubygems`.

The identifier is deliberately not a source, a host or an account. A registry
that serves gems from the public source, from a mirror, from an internal proxy
or from a private source uses the same `rubygems` Group, so that
`/rubyregistries/rubygems/packages/<packageid>` denotes the same gem wherever it
is served.

See [Section 4.1.1](#411-projection-identity-rules) for the rules that govern
this identifier.

#### 4.1.1. Projection Identity Rules

- The identifier MUST be stable across every deployment that serves the same
  projection, and MUST NOT vary by serving host, tenancy or access level. An
  implementation MUST NOT derive it from a DNS name, a URL authority or an
  account name. This is what allows one registry to shadow another: a gem
  served from an air-gapped mirror MUST present the same path as the same gem
  served from the public source.
- Where RubyGems introduces a metadata model that cannot be projected into the
  attributes defined in this specification without loss or contradiction, that
  model MUST be given a new Group identifier, for example `rubygems-v2`. Both
  Groups MAY then coexist in one registry, and a client selects the model it
  understands instead of being handed attributes whose meaning has silently
  changed.
- Where two parties project this ecosystem under incompatible interpretations,
  each MUST use a distinct Group identifier. A Group therefore identifies the
  ecosystem together with the reading of it that produced the entries, and two
  entries in the same Group are directly comparable.

Access control is a property of the registry deployment rather than of the
identifier. A registry that exposes only a private source's gems still exposes
them under `rubygems`, and MAY omit entries the caller is not entitled to see; a
caller MUST NOT infer from an entry's absence that it does not exist upstream.
Where entries drawn from different sources are served together, the `sourceurl`
attribute records which service each Group's entries were projected from.

### 4.2. Resource Identity

The `packageid` MUST be the gem name. RubyGems names are restricted to ASCII
letters, digits, `-`, `_` and `.`, all of which are valid xRegistry Entity ID
characters, so no encoding is required.

Gem names are case-sensitive for lookup, consistent with xRegistry Core Entity
ID rules. A `packageid` that differs from the canonical gem name only by case
MUST NOT be treated as an alias.

### 4.3. Version Identity and Platform Builds

RubyGems publishes a *(version, platform)* pair, not a bare version. The
`versionid` MUST therefore be derived as follows:

| Platform | `versionid` | Example |
|---|---|---|
| `ruby` | The version number alone | `1.19.4` |
| any other | `<version>-<platform>` | `1.19.4-x86_64-linux` |

The version component MUST be the normalized RubyGems version string, which is
the value `Gem::Version` yields and the value the registry API serves. That
normalization is what makes this mapping unambiguous. `Gem::Version` rewrites a
SemVer-style prerelease hyphen to `.pre.`, so the input `1.0.0-java` is stored
and served as `1.0.0.pre.java`. A published version number therefore never
contains `-`, whereas a composed `versionid` always does; the two forms cannot
be confused, and the first `-` always separates version from platform.

An implementation MUST NOT compose the `versionid` from an unnormalized version
string. Doing so reintroduces the collision this rule exists to prevent: the raw
pair *(`1.0.0-java`, `ruby`)* and the raw pair *(`1.0.0`, `java`)* would both
yield `1.0.0-java`, silently merging two distinct published builds.

Only `ruby` collapses to the bare version, because `ruby` is the single default
platform: the RubyGems compact index encodes a release as `VERSION[-PLATFORM]`
and omits the platform exactly when it is `ruby`. This specification follows
that rule so that identity is not invented here.

No other platform may be collapsed. In particular `java`, the JRuby build
platform, MUST NOT be collapsed: it is an ordinary non-default platform that
coexists with `ruby` under the same version number. `nokogiri 1.19.4`, for
example, is published for eleven platforms including both `ruby` and `java`, so
collapsing `java` would make `1.19.4/ruby` and `1.19.4/java` collide silently.

Platform names normally consist of ASCII letters, digits, `-`, `_` and `.`, all
of which are valid xRegistry Entity ID characters, so the composed identifier is
normally usable verbatim. Percent-encoding MUST NOT be used, because `%` is
itself not a valid Entity ID character.

Where the composed identifier would contain any other character, or would exceed
the xRegistry 128-character Entity ID limit, the `versionid` MUST instead be
`xh~` followed by the lowercase hex SHA-256 of the UTF-8 bytes of
`version + "/" + platform`. `/` is used as the separator inside the hashed
payload precisely because it cannot occur in a version number or a platform
name, which keeps distinct tuples distinct. `xh~` is a reserved prefix; an
implementation MUST NOT emit a `versionid` beginning with `xh~` in any other
circumstance.

The `versionid` is an identifier, not an encoding, and consumers MUST NOT
attempt to recover the upstream tuple from it. The raw components MUST be
preserved: `number` carries the normalized version string exactly as the
registry serves it, and `platform` carries the platform string exactly as
published. Consumers requiring the true upstream tuple — in particular to
address RubyGems.org itself — MUST read those attributes rather than parsing
`versionid`.

### 4.4. Timestamps

An implementation MUST set the core `createdat` attribute of a Version to the
RubyGems `created_at` value of that release, and `modifiedat` to the time of the
most recent change to the projected metadata.

## 5. Group: `rubyregistry`

The Group (`<GROUP>`) name is `rubyregistry` (singular); the plural, used as the
collection name, is `rubyregistries`. A `rubyregistry` represents one
projection of the RubyGems metadata model into xRegistry. Its identifier names
that projection rather than the service that serves it. See
[Section 4.1](#41-group-identity) for how the identifier is formed.

This extension defines the following Group-level extension attributes, in
addition to those inherited from [xRegistry Core][xRegistry Core]:

| xRegistry attribute | Type | Description |
|---|---|---|
| `sourceurl` | `url` | Base URL of the source these gems were projected from, for example `https://rubygems.org`. Provenance only. |

## 6. Resource: `package`

The Resource (`<RESOURCE>`) name is `package` (singular); the plural, used as
the collection name, is `packages`.

### 6.1. Gemspec Attributes

| xRegistry attribute | Type | RubyGems source | Description |
|---|---|---|---|
| `name` | `string` | `name` | The canonical gem name. |
| `info` | `string` | `info` | The gemspec **`summary`**: a one-line summary. The JSON API returns the summary under the name `info`; it is not the gemspec `description`. |
| `description` | `string` | `description` | The gemspec **`description`**: the long-form description. The API returns it separately from `info`, and the two are distinct fields. |
| `authors` | `string` | `authors` | Authors as a single comma-separated string, preserved in the upstream form. |
| `licenses` | `array` of `string` | `licenses` | The declared license list. The field is **nullable**: a gem may declare no licenses, in which case the attribute is absent. RubyGems **recommends** but does not enforce SPDX; each entry is a free-form short license name of at most 64 characters, and `LicenseRef-` values are permitted. Consumers MUST NOT assume an entry is a valid SPDX identifier. |
| `version` | `string` | `version` | The latest stable version of the gem. |
| `gem_uri` | `string` | `gem_uri` | Direct download URL for the `.gem` file. |
| `platform` | `string` | `platform` | Build platform of the release. |
| `full_name` | `string` | `full_name` | The published gem file base name, `<name>-<number>` for the default `ruby` platform and `<name>-<number>-<platform>` otherwise. |
| `sha` | `string` | `sha` | SHA-256 checksum of the `.gem` file. |
| `spec_sha` | `string` | `spec_sha` | SHA-256 checksum of the compiled gemspec (`.gemspec.rz`). |
| `requirements` | `array` of `string` | `requirements` | Free-form, human-readable statements of external non-gem prerequisites such as system libraries. Informational only; not machine-resolvable. |
| `attestations` | `array` of `object` | `attestations` | Sigstore attestations published with the release, each with a `media_type` and a verbatim `bundle`. |
| `version_downloads` | `integer` | `version_downloads` | Download count for this version. |
| `dependencies` | `object` | `dependencies` | Dependencies, see [6.4](#64-dependencies). |

### 6.2. Version Attributes

| xRegistry attribute | Type | Description |
|---|---|---|
| `number` | `string` | The normalized version string exactly as served by RubyGems, for example `1.0.0.pre.java`. Never contains `-`. |
| `prerelease` | `boolean` | Whether the version is a pre-release. |
| `created_at` | `timestamp` | RFC 3339 timestamp at which the registry published the version. |
| `built_at` | `timestamp` | RFC 3339 timestamp recorded in the gemspec at build time. It is asserted by the publisher and MAY differ from `created_at`. |
| `downloads_count` | `integer` | Download count for this specific version-and-platform build. |
| `yanked` | `boolean` | Whether the version has been yanked. MAY be absent; see [6.7](#67-retrieval-cost-and-availability). |

`created_at` is the ordering key for `versionmode: createdat` and MUST be
populated for every Version. `built_at` MUST NOT be used for ordering, since a
publisher controls it.

A yanked version MUST remain listed in the Versions collection and MUST NOT be
selected as the default Version when a non-yanked version exists.

### 6.3. Resolution Constraints

| xRegistry attribute | Type | RubyGems source | Description |
|---|---|---|---|
| `ruby_version` | `string` | `required_ruby_version` | The Ruby interpreter requirement, e.g. `>= 3.1.0`. |
| `rubygems_version` | `string` | `required_rubygems_version` | The RubyGems tooling requirement, e.g. `>= 3.0.0`. |

Both are per-release and both affect resolution: a consumer that ignores them
MAY select a release the target interpreter or tool chain cannot run. Like a
dependency requirement, each is a RubyGems requirement string that MUST be
preserved verbatim and MUST NOT be split or rewritten.

### 6.4. Dependencies

RubyGems separates dependencies by kind, and this specification preserves that
structure rather than flattening it:

```yaml
{
  "runtime": [
    { "name": "STRING", "requirements": "STRING" } *
  ],
  "development": [
    { "name": "STRING", "requirements": "STRING" } *
  ]
}
```

- `name` MUST be the gem name of the depended-upon gem.
- `requirements` MUST be the RubyGems requirement string exactly as declared,
  for example `>= 1.0, < 2.0`. A requirement can contain several
  comma-separated constraints; it MUST NOT be split or rewritten.

Runtime dependencies are installed with the gem; development dependencies are
installed only when working on the gem itself. Conflating them would cause a
consumer to over-install.

`dependencies` MAY be absent; see
[6.7](#67-retrieval-cost-and-availability).

### 6.5. The `metadata` Hash and Declared URIs

The gemspec `metadata` field is an **open, publisher-extensible string-to-string
hash**. RubyGems fixes no key set: it only constrains sizes, requiring each key
to be at most 128 bytes and each value at most 1024 bytes.

`metadata` is therefore modelled as a map of `string` to `string`, and an
implementation MUST copy **every** key through verbatim. Projecting a fixed
subset would silently discard keys that publishers do use in practice, among
them `funding_uri`, `wiki_uri`, `mailing_list_uri` and `rubygems_mfa_required`.

Five keys are additionally surfaced as named attributes for convenience:

| xRegistry attribute | Type | Description |
|---|---|---|
| `homepage_uri` | `string` | Project homepage URL. |
| `source_code_uri` | `string` | Source repository URL. |
| `changelog_uri` | `string` | Changelog URL. |
| `documentation_uri` | `string` | Documentation URL. |
| `bug_tracker_uri` | `string` | Issue tracker URL. |

These are **Version attributes, not Meta attributes**. Every one of them is
declared inside the gemspec of an individual release, so their values MAY differ
from release to release; the RubyGems documentation's own Rails example pins
`source_code_uri` to a tag-specific path such as `tree/v8.1.3.1`. Treating them
as package-wide would assert a stability the upstream data does not have.

These named attributes duplicate, and do not replace, the corresponding entries
in `metadata`. Where both are populated they MUST carry the same value.

`project_uri` is deliberately **not** listed here. It is not a gemspec metadata
key and is not declared by the publisher: the registry synthesizes it from the
gem name, as `https://rubygems.org/gems/<gem>` on RubyGems.org. It is therefore
a package-wide, registry-owned URL and is modelled as a Meta attribute in
[6.6](#66-meta-attributes).

### 6.6. Meta Attributes

The following are declared as Resource `metaattributes` because they describe
the gem as a whole rather than any single Version:

| xRegistry attribute | Type | Description |
|---|---|---|
| `owners` | `array` of `object` | The users who may push the gem, each with a `handle` and a `role` of `owner` or `maintainer`. |
| `project_uri` | `string` | The gem's page on the registry. Synthesized by the registry from the gem name, not declared by the publisher. |
| `downloads` | `integer` | Cumulative download count across all versions and platforms. |
| `reverse_dependencies` | `array` of `string` | Names of gems that declare a dependency on this gem. |

`owners` is taken from `GET /api/v1/gems/<gem>/owners.json`. It is deliberately
*not* mapped to the Group. A gem MAY have several owners, the set is mutable
through the ownership API, and ownership appears nowhere in the gem's own
metadata document. Ownership is therefore neither single-valued nor part of the
gem's identity, so it cannot partition the name space: gem names are flat and
globally unique on RubyGems.org regardless of who owns them. The same holds for
RubyGems Organizations, which may hold gems but do not appear in gem names.

`reverse_dependencies` is taken from
`GET /api/v1/gems/<gem>/reverse_dependencies.json`. It is an aggregate computed
over the whole current index rather than a property of any release, and it
changes when *other* gems are published, so it MUST NOT be cached as though it
were release metadata.

Placing these on the Meta entity avoids repeating a package-wide aggregate on
every Version, where it would appear to be a per-Version value.

### 6.7. Retrieval Cost and Availability

Not every attribute this specification declares can be obtained from the
endpoint that enumerates a gem's releases, and an implementation MUST NOT
present derived data as though it were free.

`GET /api/v1/versions/<gem>.json` returns one entry per (version, platform)
tuple but does **not** return `dependencies` and does **not** return a yanked
flag. Obtaining either for a given release requires a separate
`GET /api/v2/rubygems/<gem>/versions/<number>.json` request for that specific
tuple. The cost is one request per tuple: for `nokogiri`, whose release history
spans on the order of a thousand published tuples, faithfully populating these
two attributes costs on the order of a thousand additional requests for a single
gem.

The compact index (`/versions`, `/info/<gem>`) is likewise not a source for
`yanked`. It never reports a yanked release positively; a yanked release is
simply removed from the index. Absence from the compact index is not evidence of
a yank, because an unlisted release and a yanked release are indistinguishable
there.

Consequently `dependencies` and `yanked` are MAY-be-absent attributes. An
implementation MAY omit them rather than incur the per-release request cost, and
a consumer MUST NOT interpret an absent `yanked` as `false`, nor an absent
`dependencies` as an empty dependency set.

The remaining attributes in [6.1](#61-gemspec-attributes),
[6.2](#62-version-attributes), [6.3](#63-resolution-constraints) and
[6.5](#65-the-metadata-hash-and-declared-uris) are available from the
version-listing endpoint. `owners`, `reverse_dependencies` and `downloads`
each require their own gem-level request, but one per gem rather than one per
release.

## 7. Conformance

An implementation conforms to this specification when:

1. It serves a model equivalent to [`model.json`](model.json), and
2. it applies the identity mapping in [Section 4](#4-identity-mapping), and
3. every attribute it populates carries the meaning assigned in
   [Section 6](#6-resource-package).

An implementation MAY expose additional extension attributes. An implementation
MAY omit any attribute for which the upstream registry supplies no value.

[xRegistry Core]: https://xregistry.io/xreg/xregistryspecs/core-v1/docs/spec.html
[RubyGems]: https://rubygems.org/
