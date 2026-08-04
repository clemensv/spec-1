# Maven Repository Mapping - Version 1.0-rc1
<!-- words: activebydefault artifactid boms classpath dependencymanagement -->
<!-- words: developerconnection gav homepage issuemanagement javanamespace -->
<!-- words: javanamespaceid javanamespaces javanamespacescount -->
<!-- words: javanamespacesurl jdk junit metaattribute namespace namespaces -->
<!-- words: openpgp packageid packagescount packagesurl pgp poms -->
<!-- words: relativepath scm sonatype sourceurl spdx systempath timestamped -->
<!-- words: versionranges xh -->

## Abstract

This specification defines an xRegistry extension that expresses the content of
[Maven Central][Maven Central] and any repository implementing the Maven 2
repository layout in terms of the xRegistry document format and API
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
  - [4.4. Snapshot Versions](#44-snapshot-versions)
  - [4.5. Attribute Name Adaptation](#45-attribute-name-adaptation)
  - [4.6. Timestamps](#46-timestamps)
- [5. Group: `javanamespace`](#5-group-javanamespace)
- [6. Resource: `package`](#6-resource-package)
  - [6.1. Coordinate Attributes](#61-coordinate-attributes)
  - [6.2. POM Inheritance and the Effective POM](#62-pom-inheritance-and-the-effective-pom)
  - [6.3. Project Metadata](#63-project-metadata)
  - [6.4. Build Structure](#64-build-structure)
  - [6.5. Integrity: Checksums and Signatures](#65-integrity-checksums-and-signatures)
  - [6.6. Dependencies](#66-dependencies)
  - [6.7. Dependency Management](#67-dependency-management)
- [7. Conformance](#7-conformance)

## 1. Overview

The Maven ecosystem identifies every artifact by a coordinate tuple. The
minimal, universally present part of that tuple is `groupId:artifactId:version`,
commonly abbreviated as *GAV*. Artifact metadata is published as a Project
Object Model (POM) document alongside the artifact itself.

This specification maps that model into xRegistry: a `groupId` is a Group, an
`artifactId` within that `groupId` is a Resource, and a released GAV is a
Version. The POM of each release supplies the Version's attributes.

The Group is the `groupId` rather than the repository because the `groupId` is
the only part of the coordinate that identifies a *publisher*. Publishing rights
to a `groupId` are granted only after the publisher proves control of the
corresponding DNS domain or code-hosting account, so a `groupId` names a
verified organization uniquely across Maven Central. A repository, by contrast,
does not participate in artifact identity at all: the same GAV resolves to the
same artifact through Maven Central or through any mirror, and repository
selection is build configuration rather than a property of the artifact. A Group
keyed on the repository would therefore be a degenerate single-member container
that partitions nothing. The repository is recorded, where it matters, in the
Group's `sourceurl` attribute.

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

**groupId**: A reverse-DNS namespace owned by the publisher, such as
`org.junit.jupiter`.

**artifactId**: The name of a single artifact within a `groupId`.

**GAV**: The `groupId:artifactId:version` coordinate identifying one released
artifact.

**POM**: The Project Object Model document describing an artifact, its
metadata, and its dependencies.

**effective POM**: The POM that Maven actually builds with, obtained by merging
a POM with the chain of its ancestor POMs and the built-in super-POM, applying
`dependencyManagement`, interpolating properties, and applying active profiles.

**scope**: The Maven classification determining when a dependency is on the
classpath — `compile`, `provided`, `runtime`, `test`, `system` or `import`.

**snapshot**: A version whose string ends in `-SNAPSHOT`. Snapshot versions are
mutable: the same coordinate is republished as development proceeds.

## 3. Registry Model

The formal xRegistry extension model of the Java Package Registry resides in
the [model.json](model.json) file. It declares one Group type,
`javanamespaces`, and one Resource type, `packages`.

The `package` Resource sets `hasdocument` to `false`. A Maven release publishes
several files — the main artifact, the POM, and any classified artifacts
such as `sources` and `javadoc` — so there is no single Resource document.

For easy reference, the JSON serialization of a Java Package Registry adheres
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

  "javanamespacesurl": "<URL>",
  "javanamespacescount": <UINTEGER>,
  "javanamespaces": {
    "<KEY>": {                                  # javanamespaceid, e.g. org.slf4j
      "javanamespaceid": "<STRING>",            # xRegistry core attributes
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

      "group_id": "<STRING>",                   # same value as javanamespaceid
      "sourceurl": "<URL>", ?                   # repository this was read from

      "packagesurl": "<URL>",
      "packagescount": <UINTEGER>,
      "packages": {
        "<KEY>": {                              # packageid, the artifact_id
          "packageid": "<STRING>",              # xRegistry core attributes
          "versionid": "<STRING>",              # the Maven version
          "self": "<URL>",
          "shortself": "<URL>", ?
          "xid": "<XID>",

          # Start of default Version's attributes
          "epoch": <UINTEGER>,
          "name": "<STRING>", ?                 # POM <name>
          "description": "<STRING>", ?          # POM <description>
          "documentation": "<URL>", ?
          "labels": { "<STRING>": "<STRING>" * }, ?
          "createdat": "<TIMESTAMP>",
          "modifiedat": "<TIMESTAMP>",
          "ancestor": "<STRING>",

          # Start of package extension attributes
          "version": "<STRING>", ?              # same value as versionid
          "packaging": "<STRING>", ?            # e.g. jar, war, pom
          "classifier": "<STRING>", ?           # classifier of the main file
          "classifiers": [ "<STRING>" * ], ?    # e.g. sources, javadoc
          "snapshot": <BOOLEAN>, ?              # true if -SNAPSHOT
          "pom_resolution": "<STRING>", ?       # raw | effective
          "homepage": "<URL>", ?                # POM <url>

          "parent": {                           # POM <parent>
            "group_id": "<STRING>", ?
            "artifact_id": "<STRING>", ?
            "version": "<STRING>", ?
            "relative_path": "<STRING>", ?
            "package": "<XID>" ?               # -> /javanamespaces/packages
          }, ?
          "modules": [ "<STRING>" * ], ?        # POM <modules>, directory names
          "properties": { "<STRING>": "<STRING>" * }, ?  # POM <properties>
          "profiles": [                         # POM <profiles>
            {
              "id": "<STRING>", ?
              "active_by_default": <BOOLEAN>, ?
              "activation_jdk": "<STRING>", ?
              "activation_os": "<STRING>", ?
              "activation_property": "<STRING>", ?
              "activation_file": "<STRING>", ?
              "applied": <BOOLEAN> ?
            } *
          ], ?

          "checksums": [                        # .sha1 / .md5 sidecars
            {
              "filename": "<STRING>",
              "classifier": "<STRING>", ?
              "extension": "<STRING>", ?
              "url": "<URL>", ?
              "size": <UINTEGER>, ?
              "sha1": "<STRING>", ?
              "md5": "<STRING>", ?
              "sha256": "<STRING>", ?
              "sha512": "<STRING>" ?
            } *
          ], ?
          "signatures": [                       # .asc detached signatures
            {
              "filename": "<STRING>",
              "url": "<URL>", ?
              "format": "<STRING>", ?           # pgp
              "key_id": "<STRING>", ?
              "verified": <BOOLEAN> ?
            } *
          ], ?

          "organization": {
            "name": "<STRING>", ?
            "url": "<URL>" ?
          }, ?
          "developers": [
            {
              "id": "<STRING>", ?
              "name": "<STRING>", ?
              "email": "<STRING>", ?
              "url": "<URL>" ?
            } *
          ], ?
          "licenses": [                         # a POM MAY declare several
            {
              "name": "<STRING>", ?
              "url": "<URL>", ?
              "distribution": "<STRING>", ?     # repo | manual | other
              "comments": "<STRING>" ?
            } *
          ], ?
          "scm": {
            "url": "<URL>", ?
            "connection": "<STRING>", ?
            "developer_connection": "<STRING>" ?
          }, ?
          "issue_management": {
            "system": "<STRING>", ?
            "url": "<URL>" ?
          }, ?

          "dependencies": [
            {
              "group_id": "<STRING>",
              "artifact_id": "<STRING>",
              "version": "<STRING>", ?         # as declared: exact or a range
              "classifier": "<STRING>", ?
              "type": "<STRING>", ?            # defaults to jar
              "scope": "<STRING>", ?           # compile, test, provided, ...
              "is_optional": <BOOLEAN>, ?
              "system_path": "<STRING>", ?     # only with scope system
              "exclusions": [
                {
                  "group_id": "<STRING>", ?    # MAY be *
                  "artifact_id": "<STRING>" ?  # MAY be *
                } *
              ], ?
              "resolved_version": "<STRING>", ? # only when resolved exactly
              "managed": <BOOLEAN>, ?          # value came from dependencyManagement
              "package": "<XID>" ?             # -> /javanamespaces/packages
            } *
          ], ?
          "dependency_management": [            # POM <dependencyManagement>
            {
              "group_id": "<STRING>",
              "artifact_id": "<STRING>",
              "version": "<STRING>", ?
              "classifier": "<STRING>", ?
              "type": "<STRING>", ?            # pom + scope import = BOM
              "scope": "<STRING>", ?
              "is_optional": <BOOLEAN>, ?
              "system_path": "<STRING>", ?
              "exclusions": [
                {
                  "group_id": "<STRING>", ?
                  "artifact_id": "<STRING>" ?
                } *
              ], ?
              "package": "<XID>" ?             # -> /javanamespaces/packages
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

The `javanamespaceid` MUST be the Maven `groupId` verbatim, for example
`org.junit.jupiter`.

A `groupId` is directly usable as an xRegistry Entity ID: it is constrained to
ASCII letters, digits, `-`, `_` and `.`, all of which are valid Entity ID
characters, and it always begins with a letter. No encoding is needed.

A `groupId` MAY exceed the 128-character Entity ID limit only in pathological
cases. An implementation that encounters such a `groupId` MUST NOT truncate it;
it MUST instead omit the namespace and report the omission, because a truncated
namespace would collide with other namespaces sharing the same prefix.

### 4.2. Resource Identity

The `packageid` MUST be the Maven `artifactId` verbatim, for example
`junit-jupiter-api`. The full coordinate is recovered by combining the
enclosing `javanamespaceid` with the `packageid`.

An `artifactId` is unique within its `groupId` by construction, so the pair
(Group, Resource) is collision-free and reproduces the Maven coordinate exactly.
The `artifactId` is additionally preserved in the `artifact_id` meta attribute,
and consumers addressing Maven Central itself MUST read `artifact_id` rather
than the `packageid`.

Maven `artifactId`s are case-sensitive, whereas an xRegistry `<SINGULAR>id` MUST
be unique *case-insensitively* within its parent. Two `artifactId`s in one
`groupId` differing only in case therefore cannot both be represented verbatim.
Such a collision is rare but MUST be handled deterministically rather than by
silently dropping an artifact: the implementation MUST retain the verbatim form
for the lexicographically smallest `artifactId` and MUST assign every other
colliding `artifactId` a `packageid` of `xh~` followed by the lowercase hex
SHA-256 of its UTF-8 bytes. `xh~` is a reserved prefix and MUST NOT be emitted
otherwise. The same rule applies to a `groupId` colliding case-insensitively
with another within the Registry. Percent-encoding MUST NOT be used anywhere,
because `%` is itself not a valid Entity ID character.

### 4.3. Version Identity

The `versionid` MUST be the Maven version string of the release.

Maven does not constrain version syntax as tightly as Semantic Versioning does.
Where a version string contains a character outside the xRegistry Entity ID
character set, or exceeds 128 characters, the `versionid` MUST instead be `xh~`
followed by the lowercase hex SHA-256 of the UTF-8 bytes of that string. The
`versionid` is an identifier, not an encoding, and consumers MUST NOT attempt to
recover the upstream version from it; the exact string MUST be preserved in the
`version` attribute, which consumers addressing Maven Central MUST read.

A Maven version identifies a *set* of files sharing one GAV coordinate, not a
single file. The classifier and packaging distinguish those files. They are
therefore projected as the `packaging`, `classifier` and `classifiers`
attributes of the Version rather than as separate Versions, because they are
alternative renderings of the same release and are always published together.
`classifier` names the classifier of the version's own primary artifact, which
is absent in the ordinary case; `classifiers` lists the classifiers of the
additional files published beside it.

### 4.4. Snapshot Versions

Maven distinguishes *release* versions from *snapshot* versions, the latter
carrying the `-SNAPSHOT` suffix. A snapshot coordinate is republished as
development proceeds: the artifact bytes, the POM, the checksums and the
signatures behind one snapshot GAV all change over time, and the repository
disambiguates the successive uploads only through the timestamped filenames it
records in `maven-metadata.xml`.

This contradicts the xRegistry assumption that a Version is a stable, citable
point in a Resource's history. Therefore:

- An implementation SHOULD expose only release versions.
- An implementation that exposes snapshot versions MUST set `snapshot` to
  `true` on them, and MUST NOT represent or describe them as immutable.
- An implementation MUST NOT treat a `checksums` or `signatures` value recorded
  for a snapshot version as a durable integrity anchor, because a later upload
  to the same coordinate invalidates it. It MUST re-read those values whenever
  it refreshes the Version.
- An implementation MUST NOT project the individual timestamped builds of one
  snapshot coordinate as separate Versions, since they do not have distinct
  Maven versions.

A release version, by contrast, is immutable on Maven Central by policy: once
published, its files are never replaced. An implementation MAY rely on that
immutability for release versions.

### 4.5. Attribute Name Adaptation

xRegistry attribute names MUST match `[a-z0-9_]`, which does not admit
uppercase letters. The camel-cased POM element names are therefore projected as
`snake_case`:

| POM element | xRegistry attribute |
|---|---|
| `groupId` | `group_id` |
| `artifactId` | `artifact_id` |
| `developerConnection` | `developer_connection` |
| `issueManagement` | `issue_management` |
| `relativePath` | `relative_path` |
| `systemPath` | `system_path` |
| `dependencyManagement` | `dependency_management` |
| `activeByDefault` | `active_by_default` |

All values are unchanged by this renaming.

### 4.6. Timestamps

An implementation MUST set the core `createdat` attribute of a Version to the
publication time of that release, which Maven Central reports as the
`timestamp` field of its search API, and `modifiedat` to the time of the most
recent change to the projected metadata.

## 5. Group: `javanamespace`

The Group (`<GROUP>`) name is `javanamespace` (singular); the plural, used as
the collection name, is `javanamespaces`. A `javanamespace` represents one
verified Maven `groupId` — that is, one publishing organization.

| xRegistry attribute | Type | Description |
|---|---|---|
| `group_id` | `string` | REQUIRED. The `groupId` this namespace represents. Its value is normally identical to the `javanamespaceid` and is repeated as an attribute so that clients that hold a Group document need not consult the path. The two differ when the `javanamespaceid` has been hashed to resolve a case-insensitive collision, in which case this attribute is the only place the verbatim `groupId` appears. |
| `sourceurl` | `url` | OPTIONAL. Base URL of the repository from which the namespace was projected, e.g. `https://repo.maven.apache.org/maven2`. This records provenance only; the same `groupId` denotes the same publisher whichever mirror serves it. |

## 6. Resource: `package`

The Resource (`<RESOURCE>`) name is `package` (singular); the plural, used as
the collection name, is `packages`.

### 6.1. Coordinate Attributes

`artifact_id` is a `metaattribute`: it *is* the Resource identity, so it is
constant across every Version and describing it per-Version would misrepresent
it as version-varying data. The `groupId` half of the coordinate is not a
Resource attribute at all — it is the enclosing Group.

| xRegistry attribute | Type | POM element | Description |
|---|---|---|---|
| `group_id` | `string` | `project/groupId` | REQUIRED. The Maven `groupId`, verbatim. Normally identical to the `javanamespaceid`, but not when that identifier has been hashed to resolve a case-insensitive collision, so a consumer addressing Maven Central MUST read this attribute rather than the enclosing Group identifier. |
| `artifact_id` | `string` | `project/artifactId` | REQUIRED. The Maven artifact identifier, verbatim. Authoritative; the `packageid` MAY be a hash where two `artifactId`s collide case-insensitively. |

The following are Version attributes, because they vary per release:

| xRegistry attribute | Type | POM element | Description |
|---|---|---|---|
| `version` | `string` | `project/version` | The version of this release. |
| `packaging` | `string` | `project/packaging` | Artifact packaging type, e.g. `jar`, `war`, `pom`, `bundle`. |
| `classifier` | `string` | — | Classifier of this version's primary artifact, when the project itself is published under one. Absent in the ordinary case. |
| `classifiers` | `array` of `string` | — | Classifiers of the additional files published beside the primary artifact, e.g. `sources`, `javadoc`. |
| `snapshot` | `boolean` | — | `true` when `version` ends in `-SNAPSHOT`. See [4.4](#44-snapshot-versions). |

### 6.2. POM Inheritance and the Effective POM

A POM is not a self-contained document. It MAY declare a `project/parent`, and
Maven builds with the *effective POM*, obtained by merging the POM with the
chain of its ancestors and the built-in super-POM, applying
`dependencyManagement`, interpolating `${...}` properties, and applying active
profiles. Very few real POMs are complete without this: an inherited POM
routinely omits its own `groupId`, `version`, `licenses`, `organization`, `scm`
and dependency versions, all of which come from a parent.

Consequently the projected attributes of a Version are ambiguous unless the
implementation states which POM they came from. It MUST do so:

- An implementation that populates any attribute derived from the POM MUST
  populate `pom_resolution`.
- `pom_resolution` is `raw` when every projected value was read from the POM of
  this version exactly as published, with no inheritance, no
  `dependencyManagement` application, no property interpolation and no profile
  applied.
- `pom_resolution` is `effective` when the implementation computed the effective
  POM and projected values from it.
- An implementation MUST NOT mix the two within one Version. If it can compute
  the effective POM for only part of the document, it MUST report `raw`.
- An implementation reporting `raw` MUST NOT synthesize an inherited value: an
  absent element MUST be projected as an absent attribute, not as the parent's
  value.
- An implementation reporting `effective` MUST still populate `parent`, so that
  a consumer can tell that inheritance occurred and can locate its source.
- An implementation reporting `effective` SHOULD set `applied` on each entry of
  `profiles` it activated, because profile activation depends on the build
  environment and a consumer cannot otherwise reproduce the result.

Since `pom_resolution` need not be constant across a Resource's
Versions, a consumer MUST read it per Version.

`parent` carries the POM `project/parent` element:

| Field | Type | POM element | Description |
|---|---|---|---|
| `group_id` | `string` | `parent/groupId` | The parent's `groupId`. |
| `artifact_id` | `string` | `parent/artifactId` | The parent's `artifactId`. |
| `version` | `string` | `parent/version` | The parent's version. Maven does not permit a version range here, so this value is always exact. |
| `relative_path` | `string` | `parent/relativePath` | A filesystem hint used only during a local build. It has no meaning for an artifact resolved from a repository; it is recorded verbatim and MUST NOT be dereferenced. |
| `package` | `xid` | — | Reference to the parent's package, targeting `/javanamespaces/packages`. |

`package` MUST be present only when the parent's package exists in this
Registry. Its absence does not imply that the parent does not exist upstream.

### 6.3. Project Metadata

`name` and `description` are xRegistry Core attributes carrying the POM
`project/name` and `project/description` values; this extension does not
redefine them.

| xRegistry attribute | Type | POM element | Description |
|---|---|---|---|
| `homepage` | `url` | `project/url` | Project homepage URL. |
| `organization` | `object` | `project/organization` | Publishing organization: `name`, `url`. |
| `developers` | `array` of `object` | `project/developers` | Declared developers: `id`, `name`, `email`, `url`. |
| `licenses` | `array` of `object` | `project/licenses` | Declared licenses: `name`, `url`, `distribution`, `comments`. A POM MAY declare several. |
| `scm` | `object` | `project/scm` | Source control descriptor: `url`, `connection`, `developer_connection`. |
| `issue_management` | `object` | `project/issueManagement` | Issue tracker descriptor: `system`, `url`. |
| `dependencies` | `array` of `object` | `project/dependencies` | Declared dependencies, see [6.6](#66-dependencies). |
| `dependency_management` | `array` of `object` | `project/dependencyManagement` | Managed dependency declarations, see [6.7](#67-dependency-management). |

`licenses` is an array because the POM permits multiple `<license>` elements.
Implementations MUST NOT collapse it to a single SPDX expression, since the POM
does not define the boolean relationship between multiple licenses.

`licenses[].distribution` carries the POM `license/distribution` element, which
states how the artifact can legally be distributed. Maven documents the values
`repo` — the artifact can be downloaded from a Maven repository — and `manual`
— the user has to obtain the artifact by hand. The element is not restricted to
those two values, so an implementation MUST preserve any other value verbatim
and MUST NOT reject or normalize it. `distribution` MUST NOT be inferred: an
absent element MUST be projected as an absent field, because `repo` is not a
default and asserting it would make a legal claim the publisher did not make.

`licenses[].comments` carries the POM `license/comments` element verbatim.

### 6.4. Build Structure

| xRegistry attribute | Type | POM element | Description |
|---|---|---|---|
| `modules` | `array` of `string` | `project/modules` | Relative directory names of the child modules of an aggregator project. |
| `properties` | `map` of `string` | `project/properties` | POM properties as a name-to-value map. |
| `profiles` | `array` of `object` | `project/profiles` | Conditionally applied POM fragments. |

`modules` entries are build-time directory paths, not coordinates. An
implementation MUST NOT interpret a module name as an `artifactId`, because the
two coincide only by convention. A POM declaring `modules` normally has
`packaging` of `pom` and publishes no primary artifact.

`properties` values are recorded verbatim and MAY themselves contain unresolved
`${...}` placeholders. When `pom_resolution` is `effective`, `properties` MUST
still carry the declared values, not their interpolated results; the
interpolated results appear in the attributes that consumed them.

`profiles` records the declared profiles and a rendering of their activation
conditions. The content of a profile is NOT reflected in the other attributes of
the Version unless `pom_resolution` is `effective` *and* the corresponding
profile entry has `applied` set to `true`. Profile activation depends on the JDK,
operating system, properties and files present at build time, so two
implementations MAY legitimately compute different effective POMs from the same
published POM; `applied` is what makes that difference visible.

### 6.5. Integrity: Checksums and Signatures

Every file published to Maven Central is accompanied by sidecar files carrying
its digests and its detached signature. These are the only integrity anchors the
repository provides, and they cover *file bytes*, not this metadata projection.

`checksums` is an array with one entry per published file of the version — the
primary artifact, the POM, and each classified file:

| Field | Type | Description |
|---|---|---|
| `filename` | `string` | Name of the covered file, e.g. `commons-lang3-3.14.0.jar`. |
| `classifier` | `string` | Classifier of the covered file, if any. |
| `extension` | `string` | Extension of the covered file, e.g. `jar`, `pom`, `module`. |
| `url` | `url` | Absolute URL of the covered file. |
| `size` | `uinteger` | Size of the covered file in bytes. |
| `sha1` | `string` | Digest from the `.sha1` sidecar. |
| `md5` | `string` | Digest from the `.md5` sidecar. |
| `sha256` | `string` | Digest from the `.sha256` sidecar, when published. |
| `sha512` | `string` | Digest from the `.sha512` sidecar, when published. |

- Digest values MUST be lowercase hexadecimal with no whitespace, prefix or
  separator, regardless of how the sidecar file formats them.
- An implementation MUST record a digest only when it obtained it from the
  repository or computed it over the file bytes it served. It MUST NOT record a
  digest reported by any third party.
- Maven Central requires `.sha1` and `.md5` for every published file, so both
  SHOULD be present. `sha256` and `sha512` MUST be omitted when no corresponding
  sidecar is published rather than computed silently — unless the implementation
  computed them over the bytes itself, in which case it MAY record them.
- MD5 and SHA-1 are not collision-resistant. A consumer MUST NOT rely on `md5`
  or `sha1` alone as a security control; they are transfer-integrity checks.

`signatures` is an array with one entry per `.asc` detached OpenPGP signature:

| Field | Type | Description |
|---|---|---|
| `filename` | `string` | Name of the signed file. |
| `url` | `url` | Absolute URL of the `.asc` detached signature file. |
| `format` | `string` | Signature format. Maven Central publishes ASCII-armored OpenPGP signatures, denoted `pgp`. Open value set. |
| `key_id` | `string` | OpenPGP key identifier or fingerprint of the signing key, when read from the signature packet. |
| `verified` | `boolean` | See below. |

- Maven Central requires a `.asc` signature for every published file, including
  the POM, so an entry SHOULD exist for each entry of `checksums`.
- `verified` MUST be set to `true` only when the implementation itself verified
  the signature against the file bytes and against a key it trusts. An absent or
  `false` `verified` means "not verified by this implementation"; it MUST NOT be
  read as "invalid".
- Presence of a signature attests only that the publisher held the key. It is
  not an attestation of the artifact's provenance, contents or fitness, and an
  implementation MUST NOT present it as one.

See [4.4](#44-snapshot-versions) for the restriction on relying on either
attribute for snapshot versions.

### 6.6. Dependencies

Each entry of `dependencies` has the following shape:

```yaml
{
  "group_id": "STRING",
  "artifact_id": "STRING",
  "version": "STRING",             # version or version range as declared
  "classifier": "STRING" ?,
  "type": "STRING" ?,              # defaults to jar
  "scope": "STRING",               # compile | provided | runtime | test | system | import
  "is_optional": BOOLEAN ?,
  "system_path": "STRING" ?,       # only with scope system
  "exclusions": [
    { "group_id": "STRING" ?, "artifact_id": "STRING" ? } *
  ] ?,
  "managed": BOOLEAN ?,            # value came from dependencyManagement
  "package": "XID" ?,              # xRegistry reference to the dependency
  "resolved_version": "STRING" ?   # exact version, when resolvable
}
```

- `version` MUST carry the declared value, which MAY be a [version
  range][version ranges] such as `[1.0,2.0)` or a property placeholder that the
  implementation was unable to interpolate. It MUST NOT be rewritten into a
  resolved value; see below.
- `package` is an `xid` targeting `/javanamespaces/packages`. It MUST reference
  the Resource, and MUST be present only when that Resource exists in this
  Registry.
- `is_optional` mirrors the POM `optional` element; a dependency so marked is
  not transitively propagated by Maven.
- `system_path` mirrors the POM `<systemPath>` element, which is valid only when
  `scope` is `system`. It is an absolute path on the publisher's build machine,
  is meaningless to any other consumer, and MUST NOT be dereferenced. It is
  recorded only for fidelity.
- `exclusions` mirrors the POM `<exclusions>` element: transitive dependencies
  removed from the graph rooted at this dependency. Maven permits `*` in either
  field, and `*:*` excludes all transitive dependencies. An implementation MUST
  preserve the wildcard verbatim and MUST NOT expand it, because the expansion
  depends on the resolved graph and is not a property of the declaration.
- `managed` MUST be `true` when the effective value of `version`, `scope` or
  `exclusions` came from a `dependencyManagement` declaration — in this POM or
  in an inherited one — rather than from the dependency element itself. It is
  meaningful only when `pom_resolution` is `effective`.

**Version ranges versus resolved versions.** A Maven dependency version is a
*constraint*, not necessarily an identity. It MAY be an exact version such as
`3.14.0`, a range such as `[1.0,2.0)`, `(,1.0]` or `[1.5,]`, a soft pin that a
nearer declaration can override, or an uninterpolated `${...}` placeholder.
Resolving a constraint to a version requires the full repository metadata and
the whole dependency graph, and the result MAY change as new versions are
published. Therefore:

- `version` MUST always carry the constraint exactly as declared.
- `resolved_version` MUST carry an exact, published version string, and MUST be
  present only when the implementation actually performed the resolution against
  the repository. Its absence means "not resolved by this implementation"; it
  never means "no version satisfies the constraint".
- An implementation MUST NOT copy `version` into `resolved_version` merely
  because `version` happens to be an exact string. `resolved_version` asserts
  that the version exists upstream; `version` asserts nothing.
- A `resolved_version` derived from a range is a snapshot of a resolution
  performed at one moment. An implementation SHOULD refresh it, and a consumer
  MUST NOT treat it as a permanent property of the dependency declaration.
- When `package` points at a Resource and `resolved_version` is present, the two
  MUST be consistent: `resolved_version` MUST name a Version of that Resource.

### 6.7. Dependency Management

`dependency_management` carries the POM
`project/dependencyManagement/dependencies` element. Its entries have the same
shape as `dependencies` entries minus `resolved_version`, `managed` and
`package`'s dependency semantics:

```yaml
{
  "group_id": "STRING",
  "artifact_id": "STRING",
  "version": "STRING" ?,
  "classifier": "STRING" ?,
  "type": "STRING" ?,              # pom, together with scope import, is a BOM
  "scope": "STRING" ?,             # compile | provided | runtime | test | system | import
  "is_optional": BOOLEAN ?,
  "system_path": "STRING" ?,
  "exclusions": [
    { "group_id": "STRING" ?, "artifact_id": "STRING" ? } *
  ] ?,
  "package": "XID" ?
}
```

- An entry of `dependency_management` does NOT add a dependency to the project.
  It supplies default `version`, `scope`, `exclusions` and `is_optional` values
  for matching declarations in this POM and in every POM that inherits from it. An
  implementation MUST NOT merge `dependency_management` entries into
  `dependencies`, and a consumer MUST NOT read them as dependencies.
- An entry with `type` of `pom` and `scope` of `import` is a *BOM import*: it
  imports the whole `dependencyManagement` section of the named POM rather than
  managing that one artifact. This is how aggregated version sets such as
  platform BOMs are consumed, and an implementation MUST preserve such an entry
  rather than expanding it inline, since the imported set MAY be large and is a
  property of the imported POM, not of this one.
- `dependency_management` MUST be projected even when `pom_resolution` is
  `raw`, because it is a literal element of the POM.
- `package` MUST be present only when the managed Resource exists in this
  Registry.


## 7. Conformance

An implementation conforms to this specification when:

1. It serves a model equivalent to [`model.json`](model.json), and
2. it applies the identity mapping in [Section 4](#4-identity-mapping), and
3. every attribute it populates carries the meaning assigned in
   [Section 6](#6-resource-package), and
4. it populates `pom_resolution` whenever it populates any POM-derived
   attribute, as [Section 6.2](#62-pom-inheritance-and-the-effective-pom) requires.

An implementation MAY expose additional extension attributes. An implementation
MAY omit any attribute for which the POM supplies no value.

[xRegistry Core]: https://xregistry.io/xreg/xregistryspecs/core-v1/docs/spec.html
[Maven Central]: https://central.sonatype.com/
[version ranges]: https://maven.apache.org/enforcer/enforcer-rules/versionRanges.html
