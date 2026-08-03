# Terraform Registry Mapping - Version 1.0-rc1
<!-- words: azurerm gpg hashicorp hostname installable linux moduleid -->
<!-- words: modulescount modulesurl namespace namespaces plugin providerid -->
<!-- words: providerscount providersurl readme shasum shasums sourceurl -->
<!-- words: terraform terraformregistries terraformregistriescount -->
<!-- words: terraformregistriesurl terraformregistry terraformregistryid -->
<!-- words: unlisting vpc xh -->

## Abstract

This specification defines an xRegistry extension that expresses the content of
a [Terraform Registry][Terraform Registry] — its providers and modules — in
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
  - [4.2. Provider Resource Identity](#42-provider-resource-identity)
  - [4.3. Module Resource Identity](#43-module-resource-identity)
  - [4.4. Version Identity](#44-version-identity)
  - [4.5. Registry Host Scope](#45-registry-host-scope)
- [5. Group: `terraformregistry`](#5-group-terraformregistry)
  - [5.1. Service Discovery](#51-service-discovery)
  - [5.2. Independence of the Two Collections](#52-independence-of-the-two-collections)
- [6. Resource: `provider`](#6-resource-provider)
  - [6.1. Identity and Protocol Attributes](#61-identity-and-protocol-attributes)
  - [6.2. Platform Distributions](#62-platform-distributions)
  - [6.3. Signing Keys](#63-signing-keys)
  - [6.4. Meta Attributes](#64-meta-attributes)
- [7. Resource: `module`](#7-resource-module)
  - [7.1. Attribute Mapping](#71-attribute-mapping)
  - [7.2. Retrieving the Module Package](#72-retrieving-the-module-package)
  - [7.3. Module Interface Contract](#73-module-interface-contract)
  - [7.4. Meta Attributes](#74-meta-attributes)
  - [7.5. Timestamps](#75-timestamps)
- [8. Conformance](#8-conformance)

## 1. Overview

The Terraform Registry distributes two distinct artifact kinds. *Providers* are
compiled plugin binaries implementing a Terraform plugin protocol, published per
operating system and architecture. *Modules* are reusable Terraform
configurations, published as source.

Their identities differ: a provider is addressed as `namespace/type`, while a
module is addressed as `namespace/name/provider` — a three-part address in which
the final component names the provider system the module targets, so that
`terraform-aws-modules/vpc/aws` and a hypothetical `.../vpc/azurerm` are
different modules.

This specification maps both onto a single Group type — the namespace — with two
Resource types beneath it. Versions are provider or module releases.

The two Resource types are backed by two separate wire protocols — the *provider
registry protocol* and the *module registry protocol* — which a host advertises
independently through service discovery. Sharing a Group is a statement about
the shared `hostname/namespace/...` address prefix and the shared namespace
definition only; it is not a claim that the two are served by one API. See
[Section 5.2](#52-independence-of-the-two-collections).

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

**namespace**: The publishing organization or user on a registry host, such as
`hashicorp`.

**source address**: The canonical reference used in Terraform configuration:
`namespace/type` for a provider, `namespace/name/provider` for a module. It is
not a URL, and it is distinct from the module's *repository URL*, which the
module registry protocol returns in its `source` field.

**service discovery**: The mechanism by which a registry host advertises, at
`/.well-known/terraform.json`, the base URLs of the protocols it implements
under the identifiers `providers.v1` and `modules.v1`.

**plugin protocol version**: The version of the Terraform plugin wire protocol a
provider implements, such as `5.0` or `6.0`.

**tier**: The public registry's classification of a provider's support
relationship — `official`, `partner` or `community`. It is a public-registry
user-interface extension, not part of the provider registry protocol.

## 3. Registry Model

The formal xRegistry extension model of the Terraform Registry resides in the
[model.json](model.json) file. It declares one Group type,
`terraformregistries`, and two Resource types, `providers` and `modules`.

Both Resource types set `hasdocument` to `false`, `maxversions` to `0` and
`singleversionroot` to `true`, and constrain the spec-defined
`defaultversionsticky` attribute to `false`.

`versionmode` is `semver` because the Terraform Registry requires published
versions to be Semantic Versions and returns them unordered; SemVer precedence
is the authoritative ordering.

For easy reference, the JSON serialization of a Terraform Registry adheres to
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

  "terraformregistriesurl": "<URL>",
  "terraformregistriescount": <UINTEGER>,
  "terraformregistries": {
    "<KEY>": {                                  # terraformregistryid = namespace
      "terraformregistryid": "<STRING>",        # xRegistry core attributes
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

      # Group extension attributes
      "namespace": "<STRING>",                  # e.g. hashicorp
      "sourceurl": "<URL>",                     # e.g. https://registry.terraform.io
      "providers_v1": "<STRING>", ?             # providers.v1 discovery value
      "modules_v1": "<STRING>", ?               # modules.v1 discovery value

      "providersurl": "<URL>",
      "providerscount": <UINTEGER>,
      "providers": {
        "<KEY>": {                              # providerid = type, e.g. aws
          "providerid": "<STRING>",             # xRegistry core attributes
          "versionid": "<STRING>",              # the released SemVer version
          "self": "<URL>",
          "shortself": "<URL>", ?
          "xid": "<XID>",

          # Start of default Version's attributes
          "epoch": <UINTEGER>,
          "name": "<STRING>", ?
          "description": "<STRING>", ?
          "documentation": "<URL>", ?
          "labels": { "<STRING>": "<STRING>" * }, ?
          "createdat": "<TIMESTAMP>",
          "modifiedat": "<TIMESTAMP>",
          "ancestor": "<STRING>",

          # Start of provider extension attributes
          "namespace": "<STRING>", ?
          "type": "<STRING>", ?                 # e.g. aws
          "source": "<STRING>", ?               # canonical namespace/type
          "sourceurl": "<URL>", ?
          "published_at": "<TIMESTAMP>", ?      # public-registry extension
          "protocols": [ "<STRING>" * ], ?      # release-level, e.g. 5.0

          "platforms": [
            {
              "os": "<STRING>",                 # from List Available Versions
              "arch": "<STRING>",               # from List Available Versions
              # every field below requires a Find a Provider Package request
              "protocols": [ "<STRING>" * ], ?  # package-level, not release
              "filename": "<STRING>", ?
              "download_url": "<URI>", ?
              "shasums_url": "<URI>", ?
              "shasums_signature_url": "<URI>", ?
              "shasum": "<STRING>", ?
              "signing_keys": {
                "gpg_public_keys": [
                  {
                    "key_id": "<STRING>",
                    "ascii_armor": "<STRING>", ?
                    "trust_signature": "<STRING>", ? # countersignature
                    "source": "<STRING>", ?
                    "source_url": "<URI>" ?
                  } *
                ] ?
              } ?
            } *
          ], ?
          # End of provider extensions and default Version's attributes

          "metaurl": "<URL>",
          "meta": {
            # ... xRegistry core Meta attributes ...

            # Provider-wide meta attributes.
            # All of the following are OPTIONAL public-registry UI extensions
            # and are not part of the provider registry protocol.
            "downloads": <UINTEGER>, ?
            "tier": "<STRING>", ?               # official | partner | community
            "logo_url": "<URI>", ?
            "categories": [ "<STRING>" * ], ?
            "featured": <BOOLEAN>, ?
            "unlisted": <BOOLEAN>, ?            # hidden from listings only
            "warning": "<STRING>", ?
            "aliases": [ "<STRING>" * ] ?
          }, ?
          "versionsurl": "<URL>",
          "versionscount": <UINTEGER>,
          "versions": { ... } ?
        } *
      }, ?

      "modulesurl": "<URL>",
      "modulescount": <UINTEGER>,
      "modules": {
        "<KEY>": {                              # moduleid = name~provider
          "moduleid": "<STRING>",               # xRegistry core attributes
          "versionid": "<STRING>",              # the released SemVer version
          "self": "<URL>",
          "shortself": "<URL>", ?
          "xid": "<XID>",

          # Start of default Version's attributes
          "epoch": <UINTEGER>,
          "name": "<STRING>", ?                 # the module name, e.g. vpc
          "description": "<STRING>", ?
          "documentation": "<URL>", ?
          "labels": { "<STRING>": "<STRING>" * }, ?
          "createdat": "<TIMESTAMP>",
          "modifiedat": "<TIMESTAMP>",
          "ancestor": "<STRING>",

          # Start of module extension attributes
          "id": "<STRING>", ?                   # namespace/name/system/version
          "namespace": "<STRING>", ?
          "provider": "<STRING>", ?             # identity, not a dependency
          "source_address": "<STRING>", ?       # namespace/name/provider
          "source": "<URI>", ?                  # repository URL, upstream field
          "sourceurl": "<URL>", ?
          "download_url": "<URI>", ?            # from X-Terraform-Get
          "published_at": "<TIMESTAMP>", ?
          "providers": [ "<STRING>" * ], ?      # sibling provider systems
          "versions": [ "<STRING>" * ], ?       # all published versions

          "root": {                             # module interface contract
            "path": "<STRING>", ?
            "name": "<STRING>", ?
            "readme": "<STRING>", ?
            "empty": <BOOLEAN>, ?
            "inputs": [
              {
                "name": "<STRING>",
                "type": "<STRING>", ?
                "description": "<STRING>", ?
                "default": "<STRING>", ?        # JSON-encoded default
                "required": <BOOLEAN> ?
              } *
            ], ?
            "outputs": [
              { "name": "<STRING>", "description": "<STRING>" ? } *
            ], ?
            "dependencies": [
              {
                "name": "<STRING>",
                "source": "<STRING>", ?
                "version": "<STRING>" ?
              } *
            ], ?
            "provider_dependencies": [
              {
                "name": "<STRING>",
                "namespace": "<STRING>", ?
                "source": "<STRING>", ?
                "version": "<STRING>" ?
              } *
            ], ?
            "resources": [
              { "name": "<STRING>", "type": "<STRING>" ? } *
            ] ?
          }, ?

          "submodules": [ { ... } * ], ?        # same shape as "root"
          # End of module extensions and default Version's attributes

          "metaurl": "<URL>",
          "meta": {
            # ... xRegistry core Meta attributes ...

            # Module-wide meta attributes.
            # All of the following are OPTIONAL public-registry UI extensions
            # and are not part of the module registry protocol.
            "owner": "<STRING>", ?              # source repo owner
            "downloads": <UINTEGER>, ?
            "verified": <BOOLEAN>, ?
            "trusted": <BOOLEAN> ?              # about the publisher
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

The `terraformregistryid` MUST be the Terraform namespace, for example
`hashicorp` or `terraform-aws-modules`. It is additionally preserved in the
Group-level `namespace` attribute.

### 4.2. Provider Resource Identity

The `providerid` MUST be the provider type — the component after the namespace.

| Terraform source | `terraformregistryid` | `providerid` |
|---|---|---|
| `hashicorp/aws` | `hashicorp` | `aws` |

The canonical address MUST be preserved in the `source` attribute, and the
components in `namespace` and `type`.

An implementation MUST additionally set the xRegistry Core `name` attribute to
the provider type, verbatim. `name` is the authoritative statement of what the
provider is called; the `providerid` is only an addressing key derived from it.
A consumer addressing the Terraform Registry MUST read `name`.

### 4.3. Module Resource Identity

A module's native address has three components, one more than the two-level
Group/Resource hierarchy provides. The `moduleid` MUST therefore encode the
remaining two components as `name~provider`.

| Terraform source | `terraformregistryid` | `moduleid` |
|---|---|---|
| `terraform-aws-modules/vpc/aws` | `terraform-aws-modules` | `vpc~aws` |

`~` is chosen because the *public* Terraform Registry constrains published
namespace, name and provider components to alphanumerics, `_` and `-`, so `~`
cannot occur within any component of an address published there and the
substitution is unambiguous for that host.

That constraint is a publishing rule of the public registry, not part of the
module registry protocol. The protocol does not restrict the character set of
`:name` or `:system`, so a third-party host MAY serve a component containing
`~`, for which the substitution would not be collision-free. Therefore:

- If both the name and the provider component consist solely of alphanumerics,
  `_` and `-`, the `moduleid` MUST be `name~provider`.
- Otherwise the `moduleid` MUST be `xh~` followed by the lowercase hexadecimal
  SHA-256 of the UTF-8 encoding of the canonical `namespace/name/provider`
  address. `xh~` is itself outside the unreserved set above, so a hashed
  identifier can never equal a transliterated one.

Percent-encoding MUST NOT be used in either form, because `%` is itself not a
valid Entity ID character.

The `moduleid` is an identifier, not an encoding, and consumers MUST NOT attempt
to recover the address from it; in the hashed form recovery is impossible by
construction. The canonical address MUST be preserved in `source_address`, and
its components in `namespace`, `name` and `provider`; consumers addressing the
Terraform Registry itself MUST read `source_address`.

`name` carries the module name component verbatim and is REQUIRED. Where the
`moduleid` has been hashed it is the only place the module name appears, so an
implementation MUST populate it whichever form the `moduleid` takes.

`source` is *not* the canonical address. It carries the module's repository URL
exactly as the upstream `source` field returns it, for example
`https://github.com/hashicorp/terraform-aws-consul`. Consumers MUST NOT treat
`source` as a Terraform source address.

### 4.4. Version Identity

The `versionid` MUST be the released version string.

Terraform Registry version strings are Semantic Versions. A version containing
build metadata (`+`) is not a valid xRegistry Entity ID, so each `+` MUST be
replaced by `~`, giving `1.0.0~build.5` for the upstream `1.0.0+build.5`.
Versions without build metadata are used verbatim. Percent-encoding MUST NOT be
used, because `%` is itself not a valid Entity ID character.

`~` cannot occur in a Semantic Version, whose grammar admits only ASCII
alphanumerics, `.`, `-` and `+`, so the substitution is collision-free.

The `versionid` is an identifier, not an encoding, and consumers MUST NOT
attempt to recover the upstream version from it. The `version` attribute MUST
carry the released version string exactly, and consumers addressing the
Terraform Registry MUST read `version`.

The upstream version string is carried in `version` rather than in `name`
because xRegistry Core defines a single `name` per entity, and this extension
already binds `name` to the provider or module name component
([Section 4.2](#42-provider-resource-identity) and
[Section 4.3](#43-module-resource-identity)). A Version cannot name both.

Provider and module versions are immutable once published. Versions MUST be
ordered by strict SemVer precedence; build metadata is a deterministic
tie-breaker only, never a precedence input. A value that is not a valid Semantic
Version MUST sort lexically before all valid ones, so that a malformed entry
cannot displace a real release as the default. If every value is non-SemVer, the
lexical maximum is the default.

Because `defaultversionsticky` is constrained to `false`, the default Version is
recomputed from each upstream response, allowing a newly published release to
advance it.

### 4.5. Registry Host Scope

The Group identity carries only the namespace, not the registry host. A
deployment conforming to this specification therefore serves exactly one
registry host, whose base URL is recorded in the `sourceurl` attribute on the
Group and on every Resource.

A deployment that aggregates several hosts MUST disambiguate Group identity —
for example by using collision-free `host~namespace` identifiers — while
continuing to populate `sourceurl` and `namespace`. It MUST NOT silently
merge equally-named namespaces originating from different hosts, since they are
unrelated publishers.

## 5. Group: `terraformregistry`

The Group (`<GROUP>`) name is `terraformregistry` (singular); the plural, used
as the collection name, is `terraformregistries`. A `terraformregistry`
represents one namespace on one registry host.

| Group attribute | Type | Description |
|---|---|---|
| `namespace` | `string` | The canonical Terraform namespace; equal to the `terraformregistryid`. |
| `sourceurl` | `url` | Base URL of the upstream Terraform registry, e.g. `https://registry.terraform.io`. Provenance only. |
| `providers_v1` | `string` | The `providers.v1` service discovery value published by the host. |
| `modules_v1` | `string` | The `modules.v1` service discovery value published by the host. |

### 5.1. Service Discovery

A Terraform registry host is not addressable by convention. A client resolves it
by requesting `/.well-known/terraform.json` from the host and reading the
*service discovery* document, a JSON object whose keys are protocol identifiers
and whose values are the base URLs (absolute, or relative to the discovery
document) at which those protocols are served:

```yaml
{
  "providers.v1": "<STRING>", ?    # e.g. "/v1/providers/"
  "modules.v1": "<STRING>" ?       # e.g. "/v1/modules/"
}
```

`sourceurl` therefore locates the host, and `providers_v1` and `modules_v1`
record what that host advertised. An implementation SHOULD populate them with
the discovery values verbatim, without resolving them, so that a consumer can
reconstruct the upstream endpoints by resolving them against `sourceurl`. An
implementation MUST NOT synthesize a value the host did not advertise.

### 5.2. Independence of the Two Collections

The provider registry protocol and the module registry protocol are separate
protocols with separate discovery identifiers. A host MAY implement either one
without the other, and the public registry's implementation of both does not
generalize.

The two Resource types therefore share a Group only because their address
grammars share the `hostname/namespace/...` prefix and the same definition of a
namespace. This specification does not imply a unified API behind them.

Either collection MAY be permanently empty for a given deployment. An empty
`providers` or `modules` collection MUST NOT be interpreted as a namespace
holding no artifacts of that kind; when the corresponding discovery identifier
is absent, it means the host does not serve that protocol at all. Consumers MUST
NOT infer the availability of one protocol from the presence of the other.

## 6. Resource: `provider`

The Resource (`<RESOURCE>`) name is `provider` (singular); the plural, used as
the collection name, is `providers`.

### 6.1. Identity and Protocol Attributes

| xRegistry attribute | Type | Description |
|---|---|---|
| `name` | `string` | REQUIRED. The provider type, verbatim. Authoritative; the `providerid` is only an addressing key derived from it. |
| `version` | `string` | REQUIRED. The released version string exactly as published, including any build metadata. Authoritative; the `versionid` is a transliteration of it. |
| `namespace` | `string` | The namespace owning the provider. |
| `type` | `string` | The provider type identifier, e.g. `aws`. |
| `source` | `string` | The canonical `namespace/type` source address. |
| `description` | `string` | Human-readable description of the provider. |
| `sourceurl` | `url` | Base URL of the upstream registry. Provenance only. |
| `published_at` | `timestamp` | Publication time of the release. OPTIONAL public-registry extension; the provider registry protocol does not return it. |
| `protocols` | `array` of `string` | Plugin protocol versions declared for the release, e.g. `["5.0"]`. |

`protocols` determines whether a given Terraform CLI version can load the
provider at all, and is therefore a compatibility constraint rather than
descriptive metadata.

Two distinct `protocols` values exist and MUST NOT be merged. The Resource-level
`protocols` above is the *release-level* declaration returned by the versions
listing, and is what a client uses to select a version. The `protocols` inside
each `platforms` entry is the *package-level* declaration returned for one
concrete package by the download endpoint, and describes only that package. An
implementation that has projected only the versions listing MUST populate the
release-level value and omit the package-level one.

### 6.2. Platform Distributions

A provider release publishes one binary per platform. The provider registry
protocol reaches these across two responses, and this specification models both
in one array without pretending they arrive together:

```yaml
{
  # from the "List Available Versions" response
  "os": "STRING",                    # e.g. "linux"
  "arch": "STRING",                  # e.g. "amd64"

  # from a separate "Find a Provider Package" request, per platform
  "protocols": [ "STRING" ] ?,       # this package's plugin protocols
  "filename": "STRING" ?,            # the distributed archive filename
  "download_url": "URI" ?,           # location of the archive
  "shasums_url": "URI" ?,            # location of the SHA256SUMS document
  "shasums_signature_url": "URI" ?,  # location of the detached signature
  "shasum": "STRING" ?,              # checksum of this platform's archive
  "signing_keys": { ... } ?          # see Section 6.3
}
```

`os` and `arch` together identify the platform and are the only fields the
versions listing supplies. Every other field, `signing_keys` included, requires
one additional request per platform and MAY be absent. An implementation that
has projected the versions listing alone MUST omit them rather than leaving them
empty, and MUST NOT synthesize download URLs, filenames or checksums.

The absence of the download fields is therefore a statement about what has been
retrieved, not about what the upstream registry publishes. A consumer that finds
them absent MUST resolve the package itself against the upstream registry.

The download fields are typed `uri` rather than `url` because the protocol
permits them to be relative references, resolved against the endpoint that
returned them.

The integrity chain is deliberately indirect: `shasum` is the archive's hash,
`shasums_url` locates the document asserting that hash for all platforms, and
`shasums_signature_url` locates the signature over that document. A verifier
needs all three plus the platform's signing keys of
[Section 6.3](#63-signing-keys).

### 6.3. Signing Keys

`signing_keys` is a property of a *package*, not of a release. The provider
registry protocol returns it as a REQUIRED property of the per-platform "Find a
Provider Package" response, so it appears inside each `platforms` entry:

```yaml
"signing_keys": {
  "gpg_public_keys": [
    {
      "key_id": "STRING",            # the GPG key ID
      "ascii_armor": "STRING",       # the ASCII-armored public key
      "trust_signature": "STRING" ?, # registry countersignature, e.g. partner
      "source": "STRING" ?,          # name of the key's owner
      "source_url": "URI" ?          # location describing the key's provenance
    } *
  ]
}
```

Hoisting `signing_keys` to the release would assert that every package of a
release is signed by the same keys. The protocol does not guarantee that, so
this specification does not restate it. An implementation MUST NOT copy one
platform's signing keys onto another platform, and MUST NOT present
release-level signing keys.

Because `signing_keys` arrives only with the package response, it is absent
whenever the download fields of [Section 6.2](#62-platform-distributions) are
absent. Its absence in that case carries no security meaning.

`trust_signature` is present only where the registry operator has countersigned
the publisher's key. Its absence means the key is self-asserted, which is the
normal case for community providers; implementations MUST NOT treat absence as
a verification failure, nor presence as verification of the artifact itself.

### 6.4. Meta Attributes

The following are declared as Resource `metaattributes` because they describe
the provider as a whole rather than any single release.

Every attribute in this section is an OPTIONAL user-interface extension of the
public Terraform Registry. None of them is part of the provider registry
protocol. The protocol is explicit that third-party implementations should not
include these extensions, because they may change in future without notice. A
third-party host therefore SHOULD NOT populate them, and a consumer MUST NOT
require them, MUST tolerate their absence, and MUST NOT make trust or resolution
decisions depend on them.

| xRegistry attribute | Type | Description |
|---|---|---|
| `downloads` | `uinteger` | Cumulative download count. Public-registry only. |
| `tier` | `string` | Support classification. An open enumeration over `official`, `partner` and `community`; other values are permitted and MUST be served verbatim. Public-registry only. |
| `logo_url` | `uri` | Location of the provider's logo. Public-registry only. |
| `categories` | `array` of `string` | Categories describing the provider's purpose. Public-registry only. |
| `featured` | `boolean` | Whether the registry features the provider. Public-registry only. |
| `unlisted` | `boolean` | Whether the provider is hidden from registry listings. Public-registry only. |
| `warning` | `string` | Deprecation or advisory message published by the registry. Public-registry only. |
| `aliases` | `array` of `string` | Alternate source addresses resolving to this provider. Public-registry only. |

An `unlisted` provider remains resolvable by exact address; unlisting affects
discovery only. Implementations MUST continue to serve exact lookups for it.

## 7. Resource: `module`

The Resource (`<RESOURCE>`) name is `module` (singular); the plural, used as the
collection name, is `modules`.

### 7.1. Attribute Mapping

| xRegistry attribute | Type | Description |
|---|---|---|
| `name` | `string` | REQUIRED. The module name component, verbatim. Authoritative, and the only place the name appears when the `moduleid` has been hashed. |
| `version` | `string` | REQUIRED. The released version string exactly as published, including any build metadata. Authoritative; the `versionid` is a transliteration of it. |
| `id` | `string` | The upstream module identifier, of the form `namespace/name/system/version`. |
| `namespace` | `string` | The namespace owning the module. |
| `provider` | `string` | The provider system the module targets, e.g. `aws`. |
| `source_address` | `string` | The canonical `namespace/name/provider` source address, as written in a Terraform `module` block. |
| `source` | `uri` | The module's **repository URL**, returned verbatim in the upstream `source` field, e.g. `https://github.com/hashicorp/terraform-aws-consul`. |
| `sourceurl` | `url` | Base URL of the upstream registry. Provenance only. |
| `download_url` | `uri` | The module package source address from the `X-Terraform-Get` response header; see [Section 7.2](#72-retrieving-the-module-package). |
| `published_at` | `timestamp` | RFC 3339 timestamp at which the Version was published. |
| `providers` | `array` of `string` | The provider systems for which a module of this name exists in this namespace. |
| `versions` | `array` of `string` | All published version strings of this module, as returned upstream. |
| `root` | `object` | The module's interface contract; see [Section 7.3](#73-module-interface-contract). |
| `submodules` | `array` of `object` | Nested modules published in the same package, each with the shape of `root`. |

`name` and `description` are xRegistry Core attributes carrying the module name
and its human-readable description; this extension does not redefine them.

`source` and `source_address` are different things and MUST NOT be conflated.
`source` is a URL locating the module's source code, which is what the module
registry protocol returns under that field name. `source_address` is the
registry address a Terraform configuration writes. A consumer resolving the
module against the registry MUST use `source_address`, never `source`.

`provider` is part of the module's *identity*, not a dependency declaration: it
names the provider system whose resources the module manages. Two modules
differing only in `provider` are unrelated.

`providers` lists sibling identities under the same namespace and name, not
dependencies of this module; the module's actual provider requirements are in
`root.provider_dependencies`.

`versions` is informational and reproduces the upstream list. The authoritative
projection of releases is the xRegistry Versions collection, and a consumer MUST
prefer it where the two disagree.

### 7.2. Retrieving the Module Package

The module registry protocol does not publish a package location as a field of
any JSON response. A client obtains it by requesting

```
GET <modules.v1>/:namespace/:name/:system/:version/download
```

which responds `204 No Content` and carries the package location in the
`X-Terraform-Get` response header. That value is a
[go-getter](https://github.com/hashicorp/go-getter) source string, not
necessarily an `http` URL, and it is the only thing that makes a module
installable.

This specification projects that header into `download_url`. It is typed `uri`
because the protocol permits a relative reference, which is resolved against the
URL of the download request itself.

An implementation SHOULD populate `download_url`, since without it a consumer of
this projection cannot install the module. An implementation that has not
performed the download request MUST omit the attribute rather than guessing a
value; `download_url` MUST NOT be synthesized from `source`, because the
repository URL is not the package location.

### 7.3. Module Interface Contract

`root` describes the module's callable interface — what a caller must supply,
what it gets back, and what the module in turn requires. `submodules` carries
the same structure for each nested module published in the package. Both share
this shape:

| Field | Type | Description |
|---|---|---|
| `path` | `string` | Path of the module within the source repository; empty for `root`. |
| `name` | `string` | Name of the module. |
| `readme` | `string` | README content of the module. |
| `empty` | `boolean` | Whether the module declares no Terraform configuration. |
| `inputs` | `array` of `object` | Input variables: `name`, `type`, `description`, `default`, `required`. |
| `outputs` | `array` of `object` | Output values: `name`, `description`. |
| `dependencies` | `array` of `object` | Modules this module calls: `name`, `source`, `version`. |
| `provider_dependencies` | `array` of `object` | Providers this module requires: `name`, `namespace`, `source`, `version`. |
| `resources` | `array` of `object` | Resources and data sources declared: `name`, `type`. |

`inputs[].default` carries the JSON encoding of the default value, because a
Terraform default may be of any type. An input with `required` true has no
default and MUST be supplied by the caller; `required` and the presence of
`default` are therefore complementary, and an implementation MUST NOT report an
input as both.

`empty` true means the module contains no configuration. It is a valid published
state, typically a documentation-only or placeholder module, and MUST NOT be
treated as an error or as a missing projection.

`inputs`, `outputs`, `dependencies`, `provider_dependencies` and `resources`
describe the module *as published at this Version*. Because Versions are
immutable, the contract is immutable with them; a change to any of them is a new
Version.

### 7.4. Meta Attributes

The following are declared as Resource `metaattributes` because they describe
the module as a whole rather than any single release. Each is an OPTIONAL
public-registry user-interface extension and is not part of the module registry
protocol; a consumer MUST tolerate their absence.

| xRegistry attribute | Type | Description |
|---|---|---|
| `owner` | `string` | The account or organization owning the module's source repository. Public-registry only. |
| `downloads` | `uinteger` | Cumulative download count across all versions. Public-registry only. |
| `verified` | `boolean` | Whether HashiCorp has verified the module. Public-registry only. |
| `trusted` | `boolean` | Whether the registry considers the module's publisher trusted. Public-registry only. |

`owner` is the source-repository owner, which need not equal `namespace`.

`trusted` is a statement about the publisher; `verified` is a statement about
the module. They are independent and MUST NOT be conflated.

### 7.5. Timestamps

An implementation MUST set the core `createdat` attribute of a module Version
to that version's `published_at` value, and `modifiedat` to the time of the most
recent change to the projected metadata. The same rule applies to provider
Versions, using the release's publication time.

## 8. Conformance

An implementation conforms to this specification when:

1. It serves a model equivalent to [`model.json`](model.json), and
2. it applies the identity mapping in [Section 4](#4-identity-mapping), and
3. every attribute it populates carries the meaning assigned in
   [Section 6](#6-resource-provider) and [Section 7](#7-resource-module).

An implementation MAY expose additional extension attributes. An implementation
MAY omit any attribute for which the upstream registry supplies no value.

[xRegistry Core]: https://xregistry.io/xreg/xregistryspecs/core-v1/docs/spec.html
[Terraform Registry]: https://registry.terraform.io/
