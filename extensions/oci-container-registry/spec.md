# OCI Container Registry Mapping - Version 1.0-rc1
<!-- words: artifacttype containerregistries containerregistriescount -->
<!-- words: containerregistriesurl containerregistry containerregistryid -->
<!-- words: dockerhub entrypoint ghcr goarch imageid imagescount imagesurl -->
<!-- words: linux mcr mediatype namespace nuget opencontainers punycode -->
<!-- words: pypi repoints rootfs sbom sboms sigterm sourceurl xh -->

## Abstract

This specification defines an xRegistry extension that expresses the content of
an [OCI Distribution][OCI Distribution] container registry in terms of the
xRegistry document format and API [specification][xRegistry Core].

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
  - [4.1.1. Registry Identity Rules](#411-registry-identity-rules)
  - [4.2. Resource Identity](#42-resource-identity)
  - [4.3. Version Identity](#43-version-identity)
  - [4.4. Timestamps](#44-timestamps)
  - [4.5. Tag Listing and Pagination](#45-tag-listing-and-pagination)
- [5. Group: `containerregistry`](#5-group-containerregistry)
- [6. Resource: `image`](#6-resource-image)
  - [6.1. Location Attributes](#61-location-attributes)
  - [6.2. Manifest Metadata](#62-manifest-metadata)
  - [6.3. Multi-Platform Images](#63-multi-platform-images)
  - [6.4. OCI Annotations and Labels](#64-oci-annotations-and-labels)
  - [6.5. Runtime Configuration](#65-runtime-configuration)
  - [6.6. Layers and Build History](#66-layers-and-build-history)
  - [6.7. Registry Statistics](#67-registry-statistics)
  - [6.8. Image-Level Attributes](#68-image-level-attributes)
  - [6.9. Referrers and Attached Artifacts](#69-referrers-and-attached-artifacts)
- [7. Conformance](#7-conformance)

## 1. Overview

An OCI registry stores content-addressed *blobs* organized into *repositories*
and addressed by *manifests*. A manifest may describe a single-platform image or
be an *index* referencing several platform-specific manifests.

This specification maps that model into xRegistry: a registry endpoint is a
Group, a repository is a Resource, and a tag is a Version.

The central modelling decision concerns the relationship between tags and
digests. In OCI, the digest is the true identity of an image — it is the hash of
the manifest — while a tag is a mutable pointer. This specification uses the tag
as the `versionid` because tags are what users reference, and records the digest
as an attribute, which preserves the content identity without pretending that
tags are immutable.

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

**repository**: A named collection of related manifests and blobs within a
registry, such as `library/nginx`.

**manifest**: A JSON document describing an image: its configuration blob and
its ordered layer blobs.

**image index**: A manifest listing other manifests, each annotated with the
platform it targets. Also called a manifest list.

**digest**: The content hash of a manifest or blob, of the form
`sha256:<hex>`. It is the immutable identity of the content.

**tag**: A mutable human-readable label pointing at a manifest within a
repository.

## 3. Registry Model

The formal xRegistry extension model of the Container Image Registry resides in
the [model.json](model.json) file. It declares one Group type,
`containerregistries`, and one Resource type, `images`, with `maxversions` of
`0`, and `setversionid` `true`.

The `image` Resource sets `hasdocument` to `false`: the image content is a set
of content-addressed blobs retrieved through the OCI Distribution API, not a
single xRegistry document.

This extension does not constrain `defaultversionsticky`, leaving the
spec-defined attribute at its default of `true`, because the choice of which tag
represents the image — conventionally `latest`, but not necessarily — is a
deliberate selection rather than an ordering result. Tags have no intrinsic
order.

For easy reference, the JSON serialization of a Container Image Registry
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

  "containerregistriesurl": "<URL>",
  "containerregistriescount": <UINTEGER>,
  "containerregistries": {
    "<KEY>": {                                  # containerregistryid, ghcr.io
      "containerregistryid": "<STRING>",        # xRegistry core attributes
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

      "sourceurl": "<URL>", ?                  # Distribution API root

      "imagesurl": "<URL>",
      "imagescount": <UINTEGER>,
      "images": {
        "<KEY>": {                              # imageid, encoded repo name
          "imageid": "<STRING>",                # xRegistry core attributes
          "versionid": "<STRING>",              # the tag; MUTABLE, see 4.3
          "self": "<URL>",
          "shortself": "<URL>", ?
          "xid": "<XID>",

          # Start of default Version's attributes
          "epoch": <UINTEGER>,
          "name": "<STRING>",                   # full repository name, see 4.2
          "description": "<STRING>", ?
          "documentation": "<URL>", ?
          "labels": { "<STRING>": "<STRING>" * }, ?
          "createdat": "<TIMESTAMP>",
          "modifiedat": "<TIMESTAMP>",
          "ancestor": "<STRING>",

          # Start of image extension attributes
          "urls": {
            "pull": "<STRING>", ?
            "manifest": "<STRING>", ?
            "config": "<STRING>" ?
          }, ?
          "annotations": {                      # complete, unfiltered
            "<STRING>": "<STRING>" *
          }, ?
          "config_labels": {                    # config-blob Labels
            "<STRING>": "<STRING>" *
          }, ?
          "pushed": "<TIMESTAMP>", ?
          "vulnerabilities": <ANY>, ?           # scanner's own format

          "artifact_type": "<STRING>", ?        # OCI artifactType
          "subject": {                          # OCI subject descriptor
            "digest": "<STRING>",
            "mediatype": "<STRING>", ?
            "size": <UINTEGER> ?
          }, ?
          "config": {                           # config descriptor
            "digest": "<STRING>",
            "mediatype": "<STRING>", ?
            "size": <UINTEGER> ?
          }, ?
          "referrers": [                        # see 6.9
            {
              "digest": "<STRING>",
              "mediatype": "<STRING>", ?
              "size": <UINTEGER>, ?
              "artifact_type": "<STRING>", ?
              "annotations": { "<STRING>": "<STRING>" * } ?
            } *
          ], ?

          "layers": [                           # ordered base -> topmost
            {
              "digest": "<STRING>",
              "size": <UINTEGER>, ?
              "mediatype": "<STRING>" ?
            } *
          ], ?

          "metadata": {
            "digest": "<STRING>", ?             # manifest digest, sha256:...
            "manifest_mediatype": "<STRING>", ?
            "schema_version": <UINTEGER>, ?     # MUST be 2
            "size_bytes": <UINTEGER>, ?
            "layers_count": <UINTEGER>, ?

            "is_multi_platform": <BOOLEAN>, ?
            "architecture": "<STRING>", ?       # omit when multi-platform
            "os": "<STRING>", ?                 # omit when multi-platform
            "variant": "<STRING>", ?
            "os_version": "<STRING>", ?
            "os_features": [ "<STRING>" * ], ?
            "available_platforms": [
              {
                "architecture": "<STRING>",
                "os": "<STRING>",
                "variant": "<STRING>", ?
                "digest": "<STRING>",           # platform manifest digest
                "size": <UINTEGER>, ?
                "mediatype": "<STRING>" ?
              } *
            ], ?

            "oci_labels": {                     # org.opencontainers.image.*
              "title": "<STRING>", ?            #   with the prefix stripped
              "description": "<STRING>", ?
              "version": "<STRING>", ?
              "created": "<TIMESTAMP>", ?
              "revision": "<STRING>", ?
              "source": "<STRING>", ?
              "url": "<URI>", ?
              "documentation": "<STRING>", ?
              "licenses": "<STRING>", ?
              "vendor": "<STRING>", ?
              "authors": "<STRING>", ?
              "ref_name": "<STRING>", ?
              "base_digest": "<STRING>", ?
              "base_name": "<STRING>" ?
            }, ?

            # Runtime configuration defaults
            "entrypoint": [ "<STRING>" * ], ?
            "cmd": [ "<STRING>" * ], ?
            "environment": [ "<STRING>" * ], ?  # NAME=value strings
            "working_dir": "<STRING>", ?
            "user": "<STRING>", ?
            "stop_signal": "<STRING>", ?
            "author": "<STRING>", ?
            "exposed_ports": [ "<STRING>" * ], ?  # e.g. 8080/tcp
            "volumes": [ "<STRING>" * ], ?
            "rootfs_diff_ids": [ "<STRING>" * ], ?  # uncompressed layer digests

            "build_history": [
              {
                "step": <UINTEGER>,
                "created": "<TIMESTAMP>", ?
                "created_by": "<STRING>", ?
                "empty_layer": <BOOLEAN>, ?
                "author": "<STRING>", ?
                "comment": "<STRING>" ?
              } *
            ] ?
          }, ?
          # End of image extensions and default Version's attributes

          "metaurl": "<URL>",
          "meta": {                             # see 6.8
            "registry": "<STRING>", ?           # registry actually fetched from
            "namespace": "<STRING>", ?          # org component of the repo name
            "repository": "<STRING>", ?         # repo component of the repo name
            "deprecated_message": "<STRING>", ? # registry-proprietary
            "pulled": <UINTEGER>, ?             # registry-proprietary
            "starred": <UINTEGER>, ?            # registry-proprietary
            ...
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

A Group is the **registry component of an image reference**. The
`containerregistryid` MUST be the lowercase registry name exactly as it appears
in the prefix of a fully qualified image reference — `docker.io`, `ghcr.io`,
`quay.io`, `mcr.microsoft.com`, or `registry.contoso.example` for a private
registry.

This extension differs from the package-registry extensions in this respect, and
the difference is not accidental. A NuGet package ID or a PyPI project name is a
global name that denotes the same artifact whoever serves it, so those Groups
name a projection rather than a host. An OCI repository name is not global: it
is only meaningful relative to a registry, and `library/nginx` on two registries
is two unrelated repositories. The registry name is therefore part of the
artifact's own identity rather than an address at which it happens to be served,
and it belongs in the identity path.

A short label such as `dockerhub` or `ghcr` MUST NOT be used, because it is not
the name by which the registry is addressed and two deployments would be free to
choose different labels for the same registry.

See [Section 4.1.1](#411-registry-identity-rules) for the rules that govern this
identifier.

#### 4.1.1. Registry Identity Rules

- The name MUST be recorded in its lowercase form, and an internationalized
  name MUST be recorded as its A-label (Punycode) form, because an Entity ID
  is restricted to ASCII and is compared case-insensitively for uniqueness.
- A non-default port, where one is part of the registry name, MUST be appended
  as `:<port>`. `:` is a valid Entity ID character.
- The identifier is the name used in image references, not necessarily the host
  that serves the Distribution API. `docker.io` is the name for an API served
  at `registry-1.docker.io`. The API root SHOULD be recorded in the Group's
  `sourceurl` attribute as provenance, and MUST NOT be reconstructed from the
  identifier.
- The legacy alias `index.docker.io` and the bare form implied by an unqualified
  reference such as `nginx` MUST both be recorded as `docker.io`, which is the
  canonical name.
- A mirror or pull-through cache that re-serves another registry's images MUST
  record them under the Group of the registry named in the image reference, not
  under its own name. A cache serving `docker.io/library/nginx` presents it at
  `/containerregistries/docker.io/images/library~nginx`, so that a registry
  fronting the cache and a registry fronting Docker Hub produce the same path
  for the same image and one MAY shadow the other. Images the mirror itself
  originates, which are referenced by its own name, belong to its own Group.

Because the registry name is part of the reference, the same `imageid` under two
`containerregistryid` values denotes two unrelated repositories and MUST NOT be
conflated.

Access control is a property of the registry deployment rather than of the
identifier. A server MAY omit Groups or entries the caller is not entitled to
see; a caller MUST NOT infer from an absence that the registry or repository
does not exist. The `registry` meta attribute on a Resource records the registry
that image was fetched from, which for a mirrored image is the mirror rather
than the named registry; where it is present it MUST be consistent with the
service that actually served the content.

### 4.2. Resource Identity

The `imageid` MUST be derived from the OCI repository name.

OCI repository names are lowercase and consist of path components separated by
`/`, which is not a valid xRegistry Entity ID character. Percent-encoding MUST
NOT be used, because `%` is itself not a valid Entity ID character.

An implementation MUST derive the `imageid` as follows:

- Each `/` MUST be replaced by `~`. `~` is a valid Entity ID character and is
  not permitted in an OCI repository name, whose components are restricted to
  lowercase alphanumerics separated by `.`, `_` or `-`, so the substitution is
  collision-free and leaves the identifier readable.
- Where the result would exceed 128 characters, the `imageid` MUST instead be
  `xh~` followed by the lowercase hex SHA-256 of the UTF-8 bytes of the complete
  repository name. `xh~` is a reserved prefix; an implementation MUST NOT emit
  an `imageid` beginning with `xh~` in any other circumstance.

The `imageid` is an identifier, not an encoding, and consumers MUST NOT attempt
to recover the repository name from it.

An implementation MUST set the xRegistry Core `name` attribute to the complete
OCI repository name, verbatim and unaltered, including its `/` separators — for
example `library/nginx`. `name` is the authoritative statement of what the image
is called in the registry; the `imageid` is only an addressing key derived from
it. A consumer that needs the repository name, whether to construct a pull
reference, to call the OCI Distribution API, or to display the image, MUST read
`name` and MUST NOT reconstruct it from the `imageid`. This holds even when the
`imageid` appears reversible, because the `xh~` form is not, and a consumer
cannot in general tell from the `imageid` alone which form was used.

The namespace and repository components MUST additionally be preserved
separately in the `namespace` and `repository` meta attributes, which partition
the same value for consumers that address the two components independently.

### 4.3. Version Identity

The `versionid` MUST be the OCI tag. OCI tags are restricted to
`[a-zA-Z0-9_][a-zA-Z0-9._-]{0,127}`, all of which are valid xRegistry Entity ID
characters within the permitted length, so no encoding is required.

A tag is mutable: pushing to an existing tag repoints it at a new manifest
without changing the tag. Implementations MUST NOT report a tag Version as
immutable. The `metadata.digest` attribute carries the manifest digest that the
tag denoted at the time the projection was made, and it is that digest — not the
tag — that identifies fixed content.

Consumers requiring reproducibility MUST pin to `metadata.digest`.

### 4.4. Timestamps

An implementation MUST set the core `createdat` attribute of a Version to the
time at which the tag was first pushed, and `modifiedat` to the time of the most
recent push to that tag. `pushed` records the same push time in the registry's
own representation and is retained for fidelity with registry APIs that report
it.

### 4.5. Tag Listing and Pagination

The Versions of an `image` are discovered from the OCI tag listing endpoint,
`GET /v2/<name>/tags/list`, which is paginated. An implementation MUST follow
that pagination to completion before it reports an `image` as fully projected.

The OCI distribution specification defines the paging controls as follows:

- `n` is a query parameter limiting the number of tags returned in one
  response. A registry MAY return fewer tags than requested, and MAY impose its
  own maximum.
- `last` is a query parameter naming the tag after which the next page begins.
- A `Link` header of relation type `next`, as defined by
  [RFC 8288](https://www.rfc-editor.org/rfc/rfc8288), is returned when further
  results exist. The header value is the URL of the next page.

An implementation MUST treat the presence of a `Link: <...>; rel="next"` header
as authoritative and MUST request the URL it carries rather than constructing
the next request itself, because the registry MAY encode opaque continuation
state in that URL. An implementation MUST stop when a response carries no such
header.

Tags within a page are returned in lexical order, which is not a meaningful
ordering of image releases. An implementation MUST NOT infer version ordering
from tag listing order; see [4.3](#43-version-identity).

xRegistry pagination of the resulting `versions` collection is governed by the
xRegistry pagination specification and is independent of the OCI paging above.

## 5. Group: `containerregistry`

The Group (`<GROUP>`) name is `containerregistry` (singular); the plural, used
as the collection name, is `containerregistries`. A `containerregistry`
represents one OCI registry as it is named in an image reference, which is part
of the identity of the images it holds. See
[Section 4.1](#41-group-identity) for how the identifier is formed.

This extension defines the following Group-level extension attributes, in
addition to those inherited from [xRegistry Core][xRegistry Core]:

| xRegistry attribute | Type | Description |
|---|---|---|
| `sourceurl` | `url` | Base URL of the Distribution API these images were projected from, for example `https://registry-1.docker.io/v2/`. Provenance only. |

## 6. Resource: `image`

The Resource (`<RESOURCE>`) name is `image` (singular); the plural, used as the
collection name, is `images`.

### 6.1. Location Attributes

| xRegistry attribute | Type | Description |
|---|---|---|
| `urls` | `object` | Related URLs: `pull`, `manifest`, `config`. |

`name` and `description` are xRegistry Core attributes; this extension does not
redefine them, but it does constrain the value of `name`, which MUST carry the
complete OCI repository name — see [4.2](#42-resource-identity).

The registry endpoint, namespace and repository name are properties of the
image as a whole and do not vary between tags, so they are `metaattributes`
rather than Version attributes — see [6.8](#68-image-level-attributes). Together
with the tag they reconstruct the full pull reference, which `urls.pull` also
states directly.

### 6.2. Manifest Metadata

The `metadata` attribute carries manifest-derived facts:

| Sub-attribute | Type | Description |
|---|---|---|
| `digest` | `string` | Content digest of the image manifest. |
| `manifest_mediatype` | `string` | Media type of the manifest. An open enumeration listing the Docker and OCI manifest and index media types; other values are permitted. |
| `schema_version` | `uinteger` | Manifest schema version. The OCI image manifest and image index both fix this at `2`, so the value MUST be `2` for any OCI manifest, and the attribute MUST be omitted rather than defaulted when the source manifest does not carry it. |
| `architecture` | `string` | Target CPU architecture, e.g. `amd64`, `arm64`. An open enumeration over the Go `GOARCH` values. |
| `os` | `string` | Target operating system, e.g. `linux`, `windows`. An open enumeration over the Go `GOOS` values. |
| `variant` | `string` | CPU variant qualifying `architecture`, e.g. `v8`. |
| `os_version` | `string` | Operating system version the image requires, as used by Windows images. |
| `os_features` | `array` of `string` | Operating system features the image requires. |
| `size_bytes` | `uinteger` | Total size of the image in bytes. |
| `layers_count` | `uinteger` | Number of layers. |
| `is_multi_platform` | `boolean` | Whether the manifest is an index rather than a single-platform manifest. |
| `available_platforms` | `array` of `object` | Platform entries, see [6.3](#63-multi-platform-images). |

The `architecture`, `os` and `manifest_mediatype` enumerations are open: a value
not present in the enumeration MUST be served verbatim rather than dropped or
replaced, because the OCI specifications permit registrars to define further
values.

When `is_multi_platform` is `true`, `architecture` and `os` describe no single
artifact and MUST be omitted; the per-platform values are in
`available_platforms`. Populating them for an index would misrepresent the
image as single-platform.

The following top-level attributes project the remaining manifest fields:

| xRegistry attribute | Type | Description |
|---|---|---|
| `artifact_type` | `string` | The manifest's `artifactType`, identifying a non-image artifact such as an SBOM or a signature. |
| `config` | `object` | The manifest's `config` descriptor: `digest`, `mediatype`, `size`. |
| `subject` | `object` | The manifest's `subject` descriptor, identifying the manifest this one refers to: `digest`, `mediatype`, `size`. |

`subject` is what makes a manifest a *referrer* — an attestation, signature or
SBOM attached to another image. Without it, such artifacts cannot be related
back to their subject. The reverse direction of the same relationship is the
`referrers` attribute, described in [6.9](#69-referrers-and-attached-artifacts).

`artifact_type` is the discriminator that distinguishes a non-image artifact
from an image. When the manifest declares `artifactType`, that value MUST be
projected verbatim. When it does not, the OCI image specification directs a
consumer to fall back to the `config.mediaType` of the manifest; an
implementation MAY apply that fallback but MUST NOT record the fallback value in
`artifact_type`, because doing so would report a field the manifest does not
contain.

### 6.3. Multi-Platform Images

Each entry of `metadata.available_platforms` has the following shape:

```yaml
{
  "architecture": "STRING",  # e.g. "arm64"
  "os": "STRING",            # e.g. "linux"
  "variant": "STRING" ?,     # e.g. "v8"
  "digest": "STRING",        # the platform-specific manifest digest
  "size": UINTEGER,
  "mediatype": "STRING"
}
```

`digest` here is the digest of the platform-specific *manifest*, distinct from
`metadata.digest`, which is the digest of the index. A client selecting a
platform resolves the index digest to the platform digest and pulls that.

### 6.4. OCI Annotations and Labels

| xRegistry attribute | Type | Description |
|---|---|---|
| `annotations` | `map` of `string` | OCI annotations applied to the manifest, keyed by annotation name. |
| `config_labels` | `map` of `string` | The `Labels` map of the image configuration blob, keyed by label name. |
| `metadata.oci_labels` | `object` | The standard `org.opencontainers.image.*` values, projected under short names. |

Annotations and labels are distinct and MUST NOT be merged:

- `annotations` come from the manifest or index. They are not part of the
  content the config digest covers, so a registry or a tool MAY add, change or
  remove them without rebuilding the image.
- `config_labels` come from the `config.Labels` map inside the image
  configuration blob. That blob is content-addressed, so changing a label
  changes the config digest and therefore produces a different image.

The attribute is named `config_labels` rather than `labels` because xRegistry
Core already defines `labels` on every entity; reusing that name would shadow the
Core attribute.

The same key MAY appear in both maps with different values. An implementation
MUST report both values as it found them and MUST NOT reconcile them.

`metadata.oci_labels` maps the [predefined annotation keys][OCI annotations] to
attribute names by stripping the `org.opencontainers.image.` prefix:

| Sub-attribute | Annotation key |
|---|---|
| `title` | `org.opencontainers.image.title` |
| `description` | `org.opencontainers.image.description` |
| `version` | `org.opencontainers.image.version` |
| `created` | `org.opencontainers.image.created` |
| `revision` | `org.opencontainers.image.revision` |
| `source` | `org.opencontainers.image.source` |
| `url` | `org.opencontainers.image.url` |
| `documentation` | `org.opencontainers.image.documentation` |
| `licenses` | `org.opencontainers.image.licenses` |
| `vendor` | `org.opencontainers.image.vendor` |
| `authors` | `org.opencontainers.image.authors` |
| `ref_name` | `org.opencontainers.image.ref.name` |
| `base_digest` | `org.opencontainers.image.base.digest` |
| `base_name` | `org.opencontainers.image.base.name` |

`annotations` retains the complete, unfiltered annotation map, including
non-standard keys. `oci_labels` is a convenience projection of the standard
subset and MUST NOT be the only place a standard annotation appears.

### 6.5. Runtime Configuration

The following `metadata` sub-attributes project the image configuration blob's
`config` section — the defaults a runtime applies when starting a container:

| Sub-attribute | Type | Description |
|---|---|---|
| `entrypoint` | `array` of `string` | The container entrypoint. |
| `cmd` | `array` of `string` | Default arguments, appended to the entrypoint. |
| `environment` | `array` of `string` | Environment variables as `NAME=value` strings, in the OCI representation. |
| `working_dir` | `string` | Default working directory. |
| `user` | `string` | Default user. |
| `exposed_ports` | `array` of `string` | Ports declared as exposed, e.g. `8080/tcp`. |
| `volumes` | `array` of `string` | Declared volume mount points. |
| `stop_signal` | `string` | The signal a runtime sends to stop the container, e.g. `SIGTERM`. |
| `author` | `string` | The image configuration's `author` field: the person or entity responsible for the image. |

`author` is a field of the image configuration and is distinct from
`metadata.oci_labels.authors`, which projects the
`org.opencontainers.image.authors` annotation. Either MAY be present without the
other, and they MUST NOT be conflated.

`entrypoint` and `cmd` are separate because a runtime concatenates them; merging
them would lose the boundary that `docker run <image> <args>` overrides.

`environment` retains the `NAME=value` string form rather than being converted
to a map, because the OCI image configuration permits repeated names and defines
last-wins semantics that a map would silently apply.

### 6.6. Layers and Build History

```yaml
"layers": [
  {
    "digest": "STRING",     # blob digest of the layer
    "size": UINTEGER,       # compressed size in bytes
    "mediatype": "STRING"   # e.g. application/vnd.oci.image.layer.v1.tar+gzip
  } *
],
"build_history": [
  {
    "step": UINTEGER,           # ordinal position in the build
    "created": "TIMESTAMP",     # timestamp of the step
    "created_by": "STRING",     # the command that produced the step
    "empty_layer": BOOLEAN,     # whether the step produced no layer
    "author": "STRING" ?,       # author of the step
    "comment": "STRING" ?
  } *
],
"metadata": {
  "rootfs_diff_ids": [ "STRING" * ]   # uncompressed layer digests, base first
}
```

`layers` MUST be ordered from base to topmost, matching the manifest order;
layer order is semantically significant because upper layers mask lower ones.

`metadata.rootfs_diff_ids` projects `rootfs.diff_ids` of the image
configuration. The OCI image specification requires the field on every image
configuration, and requires the companion `rootfs.type` to be `layers`; because
that companion admits exactly one value it carries no information and is not
projected.

`rootfs_diff_ids` is not a duplicate of `layers`. A `layers` digest addresses
the layer blob as stored, which is normally compressed, whereas a `diff_ids`
entry is the digest of the uncompressed tar archive. The two therefore differ
for any compressed layer. `diff_ids` is also the basis of the ImageID: the
ImageID is the digest of the configuration blob, and the configuration blob
commits to the filesystem exclusively through `diff_ids`.

Both arrays MUST be ordered base-first, and entries at the same index MUST
describe the same layer. Entries of `build_history` with `empty_layer` set to
`true` have no corresponding entry in either array.

`build_history` entries with `empty_layer` set to `true` correspond to metadata
instructions that changed configuration without adding filesystem content.
The number of history entries therefore does not equal `metadata.layers_count`.

### 6.7. Registry Statistics

| xRegistry attribute | Type | Description |
|---|---|---|
| `pushed` | `timestamp` | Time at which the tag was pushed. |
| `vulnerabilities` | `any` | Security scan results, in the scanner's own representation. |

`pulled` and `starred` count activity against the image as a whole rather than
against any single tag, and are therefore `metaattributes` — see
[6.8](#68-image-level-attributes).

`pulled` and `starred` are registry-proprietary. Neither the OCI distribution
specification nor the OCI image specification defines a pull count or a star
count, and no OCI API returns them; they originate in the proprietary APIs of
individual registry operators such as Docker Hub. Both attributes are therefore
OPTIONAL. An implementation MUST omit them when the upstream registry does not
publish them, and MUST NOT substitute `0` or any other placeholder. A consumer
MUST NOT require them and MUST NOT treat their absence as an error or as an
indication of zero activity.

`vulnerabilities` is typed `any` because scan result formats differ between
registry operators; this specification does not define a normalized schema.

### 6.8. Image-Level Attributes

The following are `metaattributes` of the `image` Resource, because they
describe the image as a whole and do not vary between tags:

| Meta attribute | Type | Description |
|---|---|---|
| `registry` | `string` | The registry this image was actually fetched from. Provenance only. |
| `namespace` | `string` | The namespace or organization component of the repository name. |
| `repository` | `string` | The repository component of the repository name. |
| `pulled` | `uinteger` | Number of times the image has been pulled, across all tags. Registry-proprietary and OPTIONAL. |
| `starred` | `uinteger` | Number of stars or favorites. Registry-proprietary and OPTIONAL. |
| `deprecated_message` | `string` | Free-text deprecation notice, when the registry publishes one. Registry-proprietary and OPTIONAL. |

`pulled`, `starred` and `deprecated_message` are registry-proprietary: none of
them is defined by the OCI distribution specification or the OCI image
specification, and none is obtainable from a conformant OCI registry API. They
are all OPTIONAL. A conformant implementation that projects a registry exposing
only the OCI APIs will populate none of them, and that is not a defect.

xRegistry Core defines `deprecated` as an object with `effective`, `removal`,
`alternative` and `documentation` members and no free-text member. The registry's
notice is therefore carried in `deprecated_message` rather than redefining the
Core attribute. An implementation that populates `deprecated_message` MUST also
set the Core `deprecated` object, so that a consumer which understands only Core
still observes the deprecation.

### 6.9. Referrers and Attached Artifacts

A manifest that carries a `subject` descriptor is *attached* to the manifest
that descriptor names. Signatures, SBOMs and attestations are all modelled this
way: they are ordinary manifests, stored in the same repository, whose `subject`
points at the image they describe. The relationship is the foundation of the
supply-chain metadata model, and without it those artifacts appear in a registry
projection as unrelated, untagged manifests.

The relationship is navigable in both directions:

| Direction | Attribute | Source |
|---|---|---|
| artifact → subject | `subject` | The manifest's own `subject` field. |
| subject → artifacts | `referrers` | `GET /v2/<name>/referrers/<digest>`. |

`GET /v2/<name>/referrers/<digest>` returns an image index whose `manifests`
array holds one descriptor per manifest referring to `<digest>`. An
implementation that populates `referrers` MUST derive it from that endpoint,
using `metadata.digest` as `<digest>`, and MUST project each returned descriptor
as follows:

| `referrers` entry | Descriptor field |
|---|---|
| `digest` | `digest` |
| `mediatype` | `mediaType` |
| `size` | `size` |
| `artifact_type` | `artifactType` |
| `annotations` | `annotations` |

The referrers endpoint accepts an `artifactType` query parameter. When it is
used, the registry filters the response and MUST signal that it did so with an
`OCI-Filters-Applied: artifactType` response header. An implementation MUST NOT
populate `referrers` from a filtered response, because a filtered response is
not the complete referrer set and a consumer cannot distinguish the two from the
projection alone.

The referrers endpoint is paginated on the same terms as the tag listing; see
[4.5](#45-tag-listing-and-pagination). An implementation MUST follow the `Link`
header to completion before populating `referrers`.

A registry MAY answer the referrers endpoint with `404 Not Found`, which
indicates that it does not implement the referrers API rather than that no
referrers exist. An implementation MUST omit `referrers` in that case, and MUST
NOT emit an empty array, because an empty array asserts that the image has no
attached artifacts. A registry that does implement the API returns `200 OK` with
an empty `manifests` array when there are genuinely no referrers, and an
implementation MUST then emit an empty `referrers` array.

`referrers` is a projection of a relationship that the registry computes, not
content of the manifest, and it changes whenever an artifact is attached to or
removed from the image. A consumer MUST treat it as accurate only as of the
projection time recorded in `modifiedat`.

## 7. Conformance

An implementation conforms to this specification when:

1. It serves a model equivalent to [`model.json`](model.json), and
2. it applies the identity mapping in [Section 4](#4-identity-mapping), and
3. every attribute it populates carries the meaning assigned in
   [Section 6](#6-resource-image).

An implementation MAY expose additional extension attributes. An implementation
MAY omit any attribute for which the upstream registry supplies no value.

[xRegistry Core]: https://xregistry.io/xreg/xregistryspecs/core-v1/docs/spec.html
[OCI Distribution]: https://github.com/opencontainers/distribution-spec/blob/main/spec.md
[OCI annotations]: https://github.com/opencontainers/image-spec/blob/main/annotations.md
