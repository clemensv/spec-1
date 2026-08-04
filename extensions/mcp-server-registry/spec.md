# Model Context Protocol Server Registry Mapping - Version 1.0-rc1
<!-- words: additionalproperties containerregistries dnx dotnetregistries -->
<!-- words: environmentvariables filepath homepage islatest isrepeated -->
<!-- words: issecret lifecycles lowercasing mcp mcpb mcpprovider -->
<!-- words: mcpproviderid mcpproviders mcpproviderscount mcpprovidersurl -->
<!-- words: mimetype modelcontextprotocol namespace nodescopes npx nuget -->
<!-- words: packagearguments packagexid publishedat pypi pythonregistries -->
<!-- words: registrybaseurl registrytype remotes runtimearguments -->
<!-- words: runtimehint serverid servername serverscount serversurl sse -->
<!-- words: statuschangedat statusmessage stdio streamable subfolder -->
<!-- words: templated updatedat uvx valuehint website websiteurl xh -->

## Abstract

This specification defines an xRegistry extension that expresses the content of
a [Model Context Protocol][MCP] (MCP) server registry, as described by the
[`server.json` schema][server.json], in terms of the xRegistry document format
and API [specification][xRegistry Core].

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
  - [4.4. Attribute Name Adaptation](#44-attribute-name-adaptation)
  - [4.5. Timestamps](#45-timestamps)
- [5. Group: `mcpprovider`](#5-group-mcpprovider)
- [6. Resource: `server`](#6-resource-server)
  - [6.1. Descriptive Attributes](#61-descriptive-attributes)
  - [6.2. Packages](#62-packages)
  - [6.3. Cross-Registry Package References](#63-cross-registry-package-references)
  - [6.4. Input Descriptors](#64-input-descriptors)
  - [6.5. Transports and Remotes](#65-transports-and-remotes)
  - [6.6. Registry-Managed Metadata](#66-registry-managed-metadata)
  - [6.7. Publisher-Provided Metadata](#67-publisher-provided-metadata)
  - [6.8. Runtime Capabilities Are Out of Scope](#68-runtime-capabilities-are-out-of-scope)
- [7. Conformance](#7-conformance)

## 1. Overview

The Model Context Protocol defines how an AI application connects to external
tools, prompts and data sources. An MCP *server registry* catalogues available
servers, describing for each how to obtain it, how to launch it, what
configuration it requires, and where it is hosted.

This maps onto xRegistry as a provider Group containing `server` Resources whose
Versions are published server releases.

Two characteristics distinguish this extension from the package-registry
extensions. First, an MCP server entry is not itself a package: it *points at*
packages in other registries — npm, PyPI, OCI, NuGet — and this specification
projects those pointers as typed xRegistry cross-references, so that an MCP
catalogue federated with package registries becomes navigable end to end.
Second, a large part of the entry is a *launch contract*: arguments,
environment variables and headers, each with a declared format, requirement and
secrecy classification.

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

**MCP server**: A program exposing tools, prompts and resources over the Model
Context Protocol.

**transport**: The channel over which MCP messages flow — `stdio`,
`streamable-http` or `sse`.

**runtime hint**: An indication of the launcher expected to run the package,
such as `npx`, `uvx`, `docker` or `dnx`.

**input**: A value the operator has to supply at launch — a command-line argument,
an environment variable or an HTTP header.

## 3. Registry Model

The formal xRegistry extension model of the MCP Server Registry resides in the
[model.json](model.json) file. It declares one Group type, `mcpproviders`, and
one Resource type, `servers`, with `hasdocument` `false`, `maxversions` of `0`,
`setversionid` `true`, and `singleversionroot` `false`.

`maxversions` is `0`, meaning unlimited. An MCP registry is an archival record
of what was published; truncating it would silently discard entries that a
consumer might still be pinned to.

This extension does not constrain `defaultversionsticky`. The publisher
designates which release is current, so a server implementation is expected to
leave the spec-defined `defaultversionsticky` attribute at its default of
`true` and set the default Version explicitly.

The model also declares `metaattributes` on the `servers` Resource, carrying
the registry-managed lifecycle fields described in
[6.6](#66-registry-managed-metadata). They are placed on `meta` rather than on
the Version because the registry, not the publisher, writes them.

For easy reference, the JSON serialization of an MCP Server Registry adheres to
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

  "mcpprovidersurl": "<URL>",
  "mcpproviderscount": <UINTEGER>,
  "mcpproviders": {
    "<KEY>": {                                  # mcpproviderid = namespace
      "mcpproviderid": "<STRING>",              # xRegistry core attributes
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

      "serversurl": "<URL>",
      "serverscount": <UINTEGER>,
      "servers": {
        "<KEY>": {                              # serverid = server name part
          "serverid": "<STRING>",               # xRegistry core attributes
          "versionid": "<STRING>",              # SemVer, "+" encoded
          "self": "<URL>",
          "shortself": "<URL>", ?
          "xid": "<XID>",

          # Start of default Version's attributes
          "epoch": <UINTEGER>,
          "description": "<STRING>",             # REQUIRED; max 100 chars
          "documentation": "<URL>", ?
          "labels": { "<STRING>": "<STRING>" * }, ?
          "createdat": "<TIMESTAMP>",
          "modifiedat": "<TIMESTAMP>",
          "ancestor": "<STRING>",

          # Start of server extension attributes
          "schemaurl": "<URL>", ?               # renamed from "$schema"
          "name": "<STRING>",                   # reverse-DNS, one "/"
          "title": "<STRING>", ?                # max 100 chars
          "version": "<STRING>",                # SemVer; max 255 chars
          "website_url": "<URL>", ?
          "icons": [
            {
              "src": "<URL>",                   # https only; max 255 chars
              "mime_type": "<STRING>", ?
              "sizes": [ "<STRING>" * ], ?      # "<w>x<h>" or "any"
              "theme": "<STRING>" ?             # light | dark
            } *
          ], ?
          "repository": {
            "url": "<URL>",
            "source": "<STRING>",
            "id": "<STRING>", ?
            "subfolder": "<STRING>" ?
          }, ?

          "packages": [
            {
              "registry_type": "<STRING>",      # npm|pypi|oci|nuget|mcpb
              "registry_base_url": "<URL>", ?
              "identifier": "<STRING>",         # package name, or a URL
              "version": "<STRING>",            # exact; never a range
              "file_sha256": "<STRING>", ?      # 64 lowercase hex chars
              "runtime_hint": "<STRING>", ?     # npx | uvx | docker | dnx

              # Set by "registry_type" via ifvalues; see section 6.3
              "packagexid": "<XID>", ?          # or "<URI>" when mcpb

              "transport": {
                "type": "<STRING>",             # stdio|streamable-http|sse
                "url": "<URL>", ?               # omit for stdio
                "headers": [ <INPUT> * ] ?      # omit for stdio
              },
              "runtime_arguments": [ <INPUT> * ], ?  # passed to the launcher
              "package_arguments": [ <INPUT> * ], ?  # passed to the server
              "environment_variables": [ <INPUT> * ] ?
            } *
          ], ?

          "remotes": [                          # hosted, not launched
            {
              "type": "<STRING>",               # streamable-http | sse
              "url": "<URL>",                   # MAY be an RFC 6570 template
              "headers": [ <INPUT> * ], ?
              "variables": { "<STRING>": <VARIABLE> * } ?
            } *
          ], ?

          "publisher_meta": { "<STRING>": <JSON-VALUE> * }, ?
          # End of server extensions and default Version's attributes

          "metaurl": "<URL>",
          "meta": { ... }, ?                    # see section 6.6
          "versionsurl": "<URL>",
          "versionscount": <UINTEGER>,
          "versions": { ... } ?
        } *
      } ?
    } *
  } ?
}
```

`<INPUT>` above stands for the common input descriptor shape shared by
`runtime_arguments`, `package_arguments`, `environment_variables` and transport
`headers`:

```yaml
{
  "name": "<STRING>", ?         # flag or variable name
  "type": "<STRING>", ?         # positional | named   (arguments only)
  "value_hint": "<STRING>", ?   # identifier for a positional argument
  "description": "<STRING>", ?
  "is_required": <BOOLEAN>, ?
  "is_repeated": <BOOLEAN>, ?   # arguments only
  "is_secret": <BOOLEAN>, ?     # MUST NOT be logged, cached or displayed
  "default": "<STRING>", ?
  "format": "<STRING>", ?       # string | number | boolean | filepath
  "value": "<STRING>", ?        # supports variable substitution
  "placeholder": "<STRING>", ?
  "choices": [ "<STRING>" * ], ?
  "variables": { "<STRING>": <VARIABLE> * } ?
}
```

`<VARIABLE>` is the same descriptor with the argument-only and name-carrying
fields removed, since a substitution variable is keyed by its map key:

```yaml
{
  "description": "<STRING>", ?
  "is_required": <BOOLEAN>, ?
  "is_secret": <BOOLEAN>, ?
  "default": "<STRING>", ?
  "format": "<STRING>", ?       # string | number | boolean | filepath
  "value": "<STRING>", ?
  "choices": [ "<STRING>" * ] ?
}
```

## 4. Identity Mapping

### 4.1. Group Identity

The `mcpproviderid` MUST identify the provider publishing the servers. MCP
server names are in reverse-DNS form with exactly one `/` separating the
namespace from the server name; the namespace is the natural provider identity.

### 4.2. Resource Identity

The `serverid` MUST be derived from the portion of the MCP server name that
follows the single `/` separator, which is the server name within its
namespace. The namespace preceding the `/` becomes the `mcpproviderid`. This
splits the upstream name at its one structural separator and requires no
escaping, because neither part can itself contain a `/`.

Where the resulting `serverid` would exceed 128 characters, or contains a
character outside the xRegistry Entity ID character set, the `serverid` MUST
instead be `xh~` followed by the lowercase hex SHA-256 of the UTF-8 bytes of
that portion of the name. `xh~` is a reserved prefix; an implementation MUST NOT
emit a `serverid` beginning with `xh~` in any other circumstance.
Percent-encoding MUST NOT be used, because `%` is itself not a valid Entity ID
character.

The `serverid` is an identifier, not an encoding, and consumers MUST NOT attempt
to recover the server name from it. The canonical, fully qualified upstream name
MUST be preserved verbatim in the `name` attribute, which is the authoritative
form. Consumers MUST use `name`, not the reconstructed
`mcpproviderid`/`serverid` pair, when matching against `server.json` documents.

### 4.3. Version Identity

The `versionid` MUST be derived from the server's `version`, which the
`server.json` schema requires to be a Semantic Version.

`+` is not a valid xRegistry Entity ID character, so each `+` in a version
containing build metadata MUST be replaced by `~`, giving `1.0.0~build.5` for
the upstream `1.0.0+build.5`. Versions without build metadata are used verbatim.
Percent-encoding MUST NOT be used, because `%` is itself not a valid Entity ID
character.

`~` is a valid Entity ID character and cannot occur in a Semantic Version, whose
grammar admits only ASCII alphanumerics, `.`, `-` and `+`, so the substitution
is collision-free while leaving the identifier readable.

The `versionid` is an identifier, not an encoding, and consumers MUST NOT
attempt to recover the upstream version from it. The exact upstream string MUST
be preserved in the `version` attribute, and consumers matching against
`server.json` documents MUST read `version`.

### 4.4. Attribute Name Adaptation

xRegistry attribute names MUST match `[a-z][a-z0-9_]*` (or the extended set
`[a-z0-9][a-z0-9_:.\-]*`). Neither admits uppercase letters or `$`, so the
`server.json` field names cannot be carried over verbatim.

The `$schema` field is renamed to `schemaurl`. Every camel-cased field name is
converted to `snake_case` by lowercasing each uppercase letter and inserting an
underscore before it. The transformation is mechanical and reversible, so an
implementation can round-trip between the two spellings without a lookup table.

| `server.json` field | xRegistry attribute |
|---|---|
| `$schema` | `schemaurl` |
| `websiteUrl` | `website_url` |
| `registryType` | `registry_type` |
| `registryBaseUrl` | `registry_base_url` |
| `fileSha256` | `file_sha256` |
| `runtimeHint` | `runtime_hint` |
| `runtimeArguments` | `runtime_arguments` |
| `packageArguments` | `package_arguments` |
| `environmentVariables` | `environment_variables` |
| `valueHint` | `value_hint` |
| `isRequired` | `is_required` |
| `isRepeated` | `is_repeated` |
| `isSecret` | `is_secret` |
| `mimeType` | `mime_type` |
| `statusMessage` | `status_message` |
| `statusChangedAt` | `status_changed_at` |
| `publishedAt` | `published_at` |
| `updatedAt` | `updated_at` |
| `isLatest` | `is_latest` |
| `_meta` | `publisher_meta` |

All values are unchanged by this renaming. The final row is not a case
conversion: `_` is not a legal leading character for an xRegistry attribute
name, so the publisher-provided `_meta` block is carried under an explicit
name. See [6.7](#67-publisher-provided-metadata).

### 4.5. Timestamps

The `server.json` document carries no publication timestamp of its own. An
implementation MUST set the core `createdat` attribute of a Version to the time
at which the registry first observed that server version, and `modifiedat` to
the time of the most recent change to the projected metadata. Where the source
registry exposes `_meta.io.modelcontextprotocol.registry/official.publishedAt`
and `.updatedAt`, those values MUST be used for `createdat` and `modifiedat`
respectively. The same two values are also projected verbatim onto the
Resource's `meta` object as `published_at` and `updated_at`; see
[6.6](#66-registry-managed-metadata).

## 5. Group: `mcpprovider`

The Group (`<GROUP>`) name is `mcpprovider` (singular); the plural, used as the
collection name, is `mcpproviders`. An `mcpprovider` represents one provider
namespace of MCP servers.

This extension defines no Group-level extension attributes beyond those
inherited from [xRegistry Core][xRegistry Core].

## 6. Resource: `server`

The Resource (`<RESOURCE>`) name is `server` (singular); the plural, used as the
collection name, is `servers`.

### 6.1. Descriptive Attributes

| xRegistry attribute | Type | `server.json` field | REQUIRED | Description |
|---|---|---|---|---|
| `schemaurl` | `url` | `$schema` | no | URI of the `server.json` schema version the entry conforms to. |
| `name` | `string` | `name` | yes | Reverse-DNS server name containing exactly one `/`. Max 200 characters. |
| `title` | `string` | `title` | no | Human-readable display name. Max 100 characters. |
| `description` | `string` | `description` | yes | Server overview. Max 100 characters. |
| `version` | `string` | `version` | yes | Semantic version of the server release. Max 255 characters. |
| `icons` | `array` of `object` | `icons` | no | Sized icon set: `src`, `mime_type`, `sizes`, `theme`. |
| `website_url` | `url` | `websiteUrl` | no | Homepage or documentation URL. |
| `repository` | `object` | `repository` | no | Source location: `url`, `source`, `id`, `subfolder`. |
| `packages` | `array` of `object` | `packages` | no | Obtainable artifacts, see [6.2](#62-packages). |
| `remotes` | `array` of `object` | `remotes` | no | Hosted endpoints, see [6.5](#65-transports-and-remotes). |
| `publisher_meta` | `map` of `any` | `_meta` | no | Publisher-supplied metadata, see [6.7](#67-publisher-provided-metadata). |

The REQUIRED column reflects the upstream `server.json` schema. `name`,
`description` and `version` are mandatory there and are therefore declared
`required` in [`model.json`](model.json), overriding the OPTIONAL default that
[xRegistry Core][xRegistry Core] gives `name` and `description`.

The length limits stated above are upstream constraints. xRegistry attribute
definitions have no vocabulary for string length, so they are recorded in the
attribute descriptions and MUST be enforced by an implementation projecting
into or out of `server.json`.

Within `repository`, `url` and `source` are REQUIRED whenever `repository` is
present; `id` and `subfolder` are OPTIONAL.

`icons` entries carry `sizes` values that are each either `<width>x<height>` in
decimal digits or the literal `any`, and a `theme` of `light` or `dark`,
allowing a consumer to select an icon appropriate to its display context. `src`
is REQUIRED, MUST be an HTTPS URL, and MUST NOT exceed 255 characters. Note
that `sizes` is an array: an icon resource MAY declare several sizes.

### 6.2. Packages

Each entry of `packages` describes one way to obtain and run the server:

```yaml
{
  "registry_type": "STRING",     # REQUIRED; npm|pypi|oci|nuget|mcpb
  "registry_base_url": "URL" ?,  # base URL of the registry
  "identifier": "STRING",        # REQUIRED; package name, or download URL
  "version": "STRING",           # an exact version, never a range
  "file_sha256": "STRING" ?,     # SHA-256 of the package file
  "runtime_hint": "STRING" ?,    # npx | uvx | docker | dnx
  "packagexid": "XID" ?,         # cross-reference, see 6.3
  "transport": { ... },          # REQUIRED; see 6.5
  "runtime_arguments": [ ... ],  # see 6.4
  "package_arguments": [ ... ],  # see 6.4
  "environment_variables": [ ... ]
}
```

`registry_type`, `identifier` and `transport` are REQUIRED. A package entry
that does not say what kind of registry it names, which artifact it names, or
how the launched process is reached is not actionable, and upstream rejects it.

`version` MUST be an exact version, not a range, and MUST NOT be the literal
string `latest`. An MCP registry entry describes a specific tested combination
of server and package; a range or a floating alias would make the entry
non-reproducible. xRegistry attribute definitions cannot express either
prohibition, so it is recorded in the attribute description in
[`model.json`](model.json) and MUST be enforced by the implementation.

`file_sha256`, when present, MUST be exactly 64 lowercase hexadecimal
characters. It is the integrity anchor for a directly downloaded artifact.

`runtime_arguments` are passed to the *launcher* — `docker run` flags, for
example — while `package_arguments` are passed to the server binary itself. They
MUST NOT be merged: they occupy different positions on the command line.

### 6.3. Cross-Registry Package References

`registry_type` determines the meaning of `packagexid` through the model's
`ifvalues` construct, giving each registry type a correctly targeted
cross-reference:

| `registry_type` | `packagexid` type | Target |
|---|---|---|
| `npm` | `xid` | `/nodescopes/packages` |
| `pypi` | `xid` | `/pythonregistries/packages` |
| `oci` | `xid` | `/containerregistries/images` |
| `nuget` | `xid` | `/dotnetregistries/packages` |
| `mcpb` | `uri` | — (a location, not a registry entry) |

The four `xid` targets correspond to the Group and Resource types defined by the
npm, PyPI, OCI and NuGet extensions in this repository. Where an xRegistry
deployment federates those extensions with this one, `packagexid` resolves to a
live Resource and the MCP catalogue becomes navigable into the package graph.

`mcpb` is typed `uri` rather than `xid` because an MCP bundle has no
corresponding package-registry extension; it is referenced by location.

Implementations MAY omit `packagexid` when the referenced package is not present
in the same xRegistry deployment. `identifier` remains authoritative in all
cases.

### 6.4. Input Descriptors

`runtime_arguments`, `package_arguments`, `environment_variables` and transport
`headers` all use a common descriptor shape. This uniformity is deliberate: an
operator-supplied value has the same handling requirements regardless of the
channel through which it reaches the server.

```yaml
{
  "name": "STRING" ?,         # flag or variable name
  "type": "STRING" ?,         # positional | named   (arguments only)
  "value_hint": "STRING" ?,   # identifier for a positional argument
  "description": "STRING" ?,
  "is_required": BOOLEAN ?,
  "is_repeated": BOOLEAN ?,   # arguments only
  "is_secret": BOOLEAN ?,
  "default": "STRING" ?,
  "format": "STRING" ?,       # string | number | boolean | filepath
  "value": "STRING" ?,        # value, supporting variable substitution
  "placeholder": "STRING" ?,
  "choices": [ "STRING" * ],
  "variables": { "STRING": VARIABLE * }   # substitution bindings, by name
}
```

- `is_secret` marks a value that MUST NOT be logged, cached, or displayed.
  Consumers MUST honour it.
- `format` of `filepath` indicates the value denotes a filesystem path, which a
  consumer MAY need to translate when the server runs in a container.
- `choices` enumerates permitted values; when present, a consumer SHOULD offer
  only those values.
- `variables` supplies the substitution bindings referenced by `value`. It is a
  map keyed by variable name whose values are themselves input descriptors, so
  a substitution variable carries the same `description`, `is_required`,
  `is_secret`, `format`, `default`, `value` and `choices` semantics as the
  descriptor that references it. It is not a free-form JSON blob. The nesting
  terminates: a substitution variable does not itself carry `variables`.
- `type` distinguishes a `positional` argument, whose order matters, from a
  `named` flag. `is_repeated` indicates the argument MAY appear more than once.

### 6.5. Transports and Remotes

A `transport` object within a `packages` entry describes how a locally launched
server is reached:

```yaml
{
  "type": "STRING",     # stdio | streamable-http | sse
  "url": "URL" ?,       # needed for streamable-http and sse
  "headers": [ ... ]    # input descriptors, see 6.4
}
```

`url` and `headers` are meaningless for `stdio`, where the server communicates
over its standard streams, and MUST be omitted in that case. `transport` itself
is REQUIRED within a `packages` entry.

A `remotes` entry describes a server that is *hosted* rather than launched:

```yaml
{
  "type": "STRING",     # streamable-http | sse
  "url": "URL",         # MAY be an RFC 6570 template
  "headers": [ ... ],   # input descriptors, see 6.4
  "variables": { "STRING": VARIABLE * }
}
```

`remotes` therefore permits only network transports; `stdio` is not a valid
value. A server entry MAY carry both `packages` and `remotes`, offering the
consumer a choice between running it locally and using a hosted instance.

`variables` supplies the bindings for a templated `url`, using the same
descriptor shape as [6.4](#64-input-descriptors). A multi-tenant service is
described as `https://{tenant_id}.example.com/mcp` with a `tenant_id` entry in
`variables` marked `is_required`; without `variables` such an endpoint cannot
be resolved by the consumer.

Headers frequently carry credentials; such headers MUST set `is_secret` to
`true`.

### 6.6. Registry-Managed Metadata

The upstream API returns two distinct `_meta` blocks, and this specification
keeps them apart because they have different authors and different lifecycles.

The response-level `_meta` block keyed
`io.modelcontextprotocol.registry/official` is written by the registry, not by
the publisher. It is projected onto the Resource's `meta` object through the
model's `metaattributes`:

| xRegistry attribute | Type | Upstream field | Description |
|---|---|---|---|
| `status` | `string` | `status` | `active`, `deprecated` or `deleted`. |
| `status_message` | `string` | `statusMessage` | Explanation of `status`. Max 500 characters. |
| `status_changed_at` | `timestamp` | `statusChangedAt` | When `status` last changed. |
| `published_at` | `timestamp` | `publishedAt` | First publication of the default Version. |
| `updated_at` | `timestamp` | `updatedAt` | Last update of the default Version. |
| `is_latest` | `boolean` | `isLatest` | Whether the default Version is the registry's latest. |

The upstream block declares `additionalProperties: false` and defines exactly
these six properties; an implementation MUST NOT invent further ones. In
particular, the `serverId` and `versionId` fields of earlier v0 iterations are
retired: the current API addresses a server by `{serverName}` and `{version}`,
which this extension projects as the `mcpproviderid`/`serverid` pair and the
`versionid` respectively.

These attributes are registry-managed. A publisher MUST NOT set them, and an
implementation MUST NOT accept them from a `server.json` document.

Note that a name such as `status` MUST NOT be declared as a Version attribute
merely because it appears in the same HTTP response as the server object;
placing it on `meta` is what records that the registry, not the publisher, owns
it.

### 6.7. Publisher-Provided Metadata

The `_meta` block *inside* the server object is publisher data and is therefore
Version data. Upstream reserves the key
`io.modelcontextprotocol.registry/publisher-provided` for it, limits it to
4 KB, and silently discards every other key on publish. This specification
projects that one key, and only that key, as the Version attribute
`publisher_meta`, an open map of arbitrary JSON values.

The attribute is named `publisher_meta` rather than `_meta` because `_` is not
a legal leading character for an xRegistry attribute name.

An implementation MUST NOT merge `publisher_meta` with the registry-managed
attributes of [6.6](#66-registry-managed-metadata). The two blocks are
separately authored: collapsing them would let a publisher appear to assert a
lifecycle `status`, or make registry timestamps look publisher-supplied.

### 6.8. Runtime Capabilities Are Out of Scope

An MCP server's tools, prompts and resources are protocol concepts. A client
learns them by connecting to a running server and performing capability
negotiation. They are not fields of `server.json` and no registry endpoint
returns them.

This specification therefore defines no `tools`, `prompts` or `resources`
attributes. Declaring them would assert that a projection of a registry can
populate them, which it cannot; a consumer reading such attributes would have
no way to tell a stale or fabricated catalogue from a real one.

An implementation that wishes to publish a capability catalogue MUST obtain it
out of band, MUST treat it as advisory rather than authoritative, and MUST
carry it in its own extension attributes — never as a projection of the MCP
server registry.

## 7. Conformance

An implementation conforms to this specification when:

1. It serves a model equivalent to [`model.json`](model.json), and
2. it applies the identity mapping in [Section 4](#4-identity-mapping), and
3. every attribute it populates carries the meaning assigned in
   [Section 6](#6-resource-server).

An implementation MAY expose additional extension attributes. An implementation
MAY omit any attribute for which the upstream registry supplies no value.

[xRegistry Core]: https://xregistry.io/xreg/xregistryspecs/core-v1/docs/spec.html
[MCP]: https://modelcontextprotocol.io/
[server.json]: https://github.com/modelcontextprotocol/registry
