# Hugging Face Hub Mapping - Version 1.0-rc1
<!-- words: blobid carddata datasetid datasetscount datasetsurl dtype gpu -->
<!-- words: gradio huggingface huggingfaceregistries -->
<!-- words: huggingfaceregistriescount huggingfaceregistriesurl -->
<!-- words: huggingfaceregistry huggingfaceregistryid lastmodified lfs -->
<!-- words: modelid modelscount modelsurl namespace namespaces openai -->
<!-- words: paperswithcode pointersize rajpurkar repoid rfilename -->
<!-- words: safetensors sdk shas spaceid spacescount spacesurl streamlit -->
<!-- words: subdomain targetcommit transformersinfo unnamespaced -->
<!-- words: usedstorage widgetdata xh -->

## Abstract

This specification defines an xRegistry extension that expresses the content of
the [Hugging Face Hub][HF Hub] — its models, datasets and spaces — in terms of
the xRegistry document format and API [specification][xRegistry Core].

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
  - [4.2. The Reserved `_` Group](#42-the-reserved-_-group)
  - [4.3. Resource Identity](#43-resource-identity)
  - [4.4. Version Identity](#44-version-identity)
  - [4.5. Timestamps](#45-timestamps)
- [5. Group: `huggingfaceregistry`](#5-group-huggingfaceregistry)
- [6. Resources](#6-resources)
  - [6.1. Common Resource Attributes](#61-common-resource-attributes)
  - [6.2. Common Meta Attributes](#62-common-meta-attributes)
  - [6.3. Branch, Tag and Conversion References](#63-branch-tag-and-conversion-references)
  - [6.4. File Manifest](#64-file-manifest)
  - [6.5. Resource: `model`](#65-resource-model)
  - [6.6. Resource: `dataset`](#66-resource-dataset)
  - [6.7. Resource: `space`](#67-resource-space)
- [7. Access Control](#7-access-control)
- [8. Conformance](#8-conformance)

## 1. Overview

The Hugging Face Hub hosts three kinds of repository: machine-learning
**models**, **datasets**, and **spaces** (hosted demonstration applications).
All three are Git repositories, identified as `owner/name`, and all three share
the same versioning substrate: Git commits.

This maps onto xRegistry as an owner namespace Group containing three Resource
types, with commits as Versions. Unlike package registries, where a version is a
publishing event with a chosen version number, a Hub repository's Versions are
*commit SHAs*: content-addressed, immutable, and not ordered by any semantic
scheme.

Branches and tags are mutable pointers into that commit history. They are
therefore not Versions; they are recorded as an attribute of the Resource Meta
entity, where their mutability is explicit.

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

**repository ID** (`repoid`): The Hub identifier of a repository, normally
`owner/name`. Upstream it is the `id` field of a repository object; models
additionally repeat it in the legacy `modelId` field.

**sibling**: A file in a Hub repository, as listed in the `siblings` array of a
repository object.

**owner**: The user or organization namespace owning a repository.

**gated**: A Hub access state requiring the requester to accept terms before
downloading. Its value is `false`, `"auto"` or `"manual"`.

**pipeline tag**: A label identifying the machine-learning task a model
performs, such as `text-generation`.

## 3. Registry Model

The formal xRegistry extension model of the Hugging Face Hub Registry resides
in the [model.json](model.json) file. It declares one Group type,
`huggingfaceregistries`, and three Resource types, `models`, `datasets` and
`spaces`.

All three Resource types set `hasdocument` to `false`, `maxversions` to `0`,
`setversionid` to `true`, `versionmode` to `manual` and `singleversionroot` to
`false`. All three constrain the spec-defined `defaultversionsticky` attribute
to `false`.

`versionmode` is `manual` because commit SHAs carry no intrinsic order; the
implementation determines lineage from the commit graph rather than from the
identifier. `singleversionroot` is `false` because a Git history can have
several roots.

The authoritative list of Hub response fields referenced throughout this
specification is the Hub's own machine-readable API description, the
[OpenAPI document][HF Hub OpenAPI] published at
`https://huggingface.co/.well-known/openapi.json`. The Hub's prose API
documentation now defers to that document, so it is cited here in preference to
the narrative pages.

For easy reference, the JSON serialization of a Hugging Face Hub Registry
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

  "huggingfaceregistriesurl": "<URL>",
  "huggingfaceregistriescount": <UINTEGER>,
  "huggingfaceregistries": {
    "<KEY>": {                                  # owner namespace, or "_"
      "huggingfaceregistryid": "<STRING>",      # xRegistry core attributes
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
      "namespace": "<STRING>",                  # "" for the reserved "_" group

      "modelsurl": "<URL>",
      "modelscount": <UINTEGER>,
      "models": {
        "<KEY>": {                              # modelid = repo basename
          "modelid": "<STRING>",                # xRegistry core attributes
          "versionid": "<STRING>",              # the Git commit SHA
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
          "ancestor": "<STRING>",               # from the commit graph

          # Start of repository extension attributes
          "repoid": "<STRING>", ?               # the Hub "id" field
          "repository": "<STRING>", ?           # canonical owner/repository
          "namespace": "<STRING>", ?            # canonical owner namespace
          "author": "<STRING>", ?
          "sha": "<STRING>", ?                  # tip of the default branch
          "message": "<STRING>", ?              # commit title of this Version
          "siblings": [                         # file manifest of this commit
            {
              "rfilename": "<STRING>",
              "size": <UINTEGER>, ?
              "blobid": "<STRING>", ?
              "lfs": {
                "size": <UINTEGER>, ?
                "sha256": "<STRING>", ?
                "pointersize": <UINTEGER> ?
              } ?
            } *
          ], ?
          # End of repository extensions and default Version's attributes

          "metaurl": "<URL>",
          "meta": {
            # ... xRegistry core Meta attributes ...

            # Repository-wide meta attributes
            "private": <BOOLEAN>, ?
            "gated": <ANY>, ?                   # false | "auto" | "manual"
            "disabled": <BOOLEAN>, ?
            "used_storage": <UINTEGER>, ?
            "likes": <UINTEGER>, ?
            "card_data": { "license": "<STRING>", ? "<STRING>": <ANY> * }, ?
            "tags": [ "<STRING>" * ], ?
            "refs": {                           # MUTABLE pointers, not Versions
              "branches": [
                { "name": "<STRING>", "ref": "<STRING>",
                  "targetcommit": "<STRING>" } *
              ], ?
              "tags": [
                { "name": "<STRING>", "ref": "<STRING>",
                  "targetcommit": "<STRING>" } *
              ], ?
              "converts": [
                { "name": "<STRING>", "ref": "<STRING>",
                  "targetcommit": "<STRING>" } *
              ] ?
            }, ?

            # "models" and "datasets" only
            "downloads": <UINTEGER>, ?

            # "models" only
            "pipeline_tag": "<STRING>", ?       # e.g. text-generation
            "library_name": "<STRING>", ?       # e.g. transformers
            "config": { "<STRING>": <ANY> * }, ?
            "transformers_info": {
              "auto_model": "<STRING>", ?
              "pipeline_tag": "<STRING>", ?
              "processor": "<STRING>" ?
            }, ?
            "safetensors": {
              "parameters": { "<STRING>": <UINTEGER> * }, ?
              "total": <UINTEGER> ?
            }, ?
            "model_index": [ <ANY> * ], ?       # the "model-index" card block
            "inference": <ANY>, ?
            "widget_data": [ <ANY> * ] ?
          }, ?
          "versionsurl": "<URL>",
          "versionscount": <UINTEGER>,
          "versions": { ... } ?
        } *
      }, ?

      "datasetsurl": "<URL>",
      "datasetscount": <UINTEGER>,
      "datasets": {
        "<KEY>": {                              # datasetid = repo basename
          # Same shape as "models" above, except that the Meta entity carries
          # no model-only attributes and instead adds:
          "meta": {
            "paperswithcode_id": "<STRING>" ?
          } ?
        } *
      }, ?

      "spacesurl": "<URL>",
      "spacescount": <UINTEGER>,
      "spaces": {
        "<KEY>": {                              # spaceid = repo basename
          # Same shape as "models" above, except that the Meta entity has no
          # "downloads" and no model-only attributes, and instead adds:
          "meta": {
            "sdk": "<STRING>", ?                # gradio | streamlit | docker | static
            "runtime": {
              "stage": "<STRING>", ?            # e.g. RUNNING | SLEEPING | BUILDING
              "hardware": {
                "current": "<STRING>", ?
                "requested": "<STRING>" ?
              }, ?
              "resources": {
                "cpu": "<STRING>", ?
                "memory": "<STRING>", ?
                "gpu": "<STRING>", ?
                "gpu_memory": "<STRING>" ?
              } ?
            }, ?
            "subdomain": "<STRING>", ?
            "host": "<STRING>" ?
          } ?
        } *
      } ?
    } *
  } ?
}
```

## 4. Identity Mapping

### 4.1. Group Identity

The `huggingfaceregistryid` MUST be the Hub owner namespace, and MUST be
preserved in the Group-level `namespace` attribute.

| Hub repository ID | Group | Resource type | Resource | Path |
|---|---|---|---|---|
| `google-bert/bert-base-uncased` | `google-bert` | `models` | `bert-base-uncased` | `/huggingfaceregistries/google-bert/models/bert-base-uncased` |
| `rajpurkar/squad` | `rajpurkar` | `datasets` | `squad` | `/huggingfaceregistries/rajpurkar/datasets/squad` |
| `gradio/hello_world` | `gradio` | `spaces` | `hello_world` | `/huggingfaceregistries/gradio/spaces/hello_world` |

### 4.2. The Reserved `_` Group

Some Hub repositories have a bare identifier with no owner component. The Group
ID `_` is reserved for these.

`_` MUST be used only when the authoritative `repoid` returned by the Hub is
genuinely bare. It MUST NOT be used for a *public alias* of an owned
repository: `gpt2` is an alias of `openai-community/gpt2`, so its canonical
identity is the `openai-community` Group. A request for an alias SHOULD be
answered with HTTP 308 redirecting to the canonical owner path.

When the Group is `_`, the `namespace` attribute MUST be the empty string.

### 4.3. Resource Identity

The Resource ID MUST be the repository basename — the component after the owner.

Resource identity is scoped per Resource type, so an owner MAY have a model and
a dataset with the same basename; they are distinct Resources.

Neither the Group ID nor the Resource ID ever contains `/`. Hub repository names
are otherwise restricted to ASCII alphanumerics, `-`, `_` and `.`, all of which
are valid Entity ID characters, so no encoding is required and percent-encoding
never arises — which is fortunate, since `%` is itself not a valid Entity ID
character. The canonical upstream identity is retained in `repoid`, `repository`
and `name`, and consumers addressing the Hub itself MUST read `repoid`.

Lookup is case-sensitive, per xRegistry Core
[`<SINGULAR>id` constraints][xRegistry singularid]. A request differing from the
canonical identity only by case MUST return HTTP 404 and MUST NOT be aliased.

Uniqueness, however, is case-*insensitive*, while Hub repository names are
case-sensitive. Two repositories of the same type under one owner differing only
in case therefore cannot both be represented verbatim. Such a collision MUST be
handled deterministically rather than by silently dropping a repository: the
implementation MUST retain the verbatim basename for the lexicographically
smallest name and MUST assign every other colliding repository a Resource ID of
`xh~` followed by the lowercase hex SHA-256 of the UTF-8 bytes of its basename.
`xh~` is a reserved prefix and MUST NOT be emitted otherwise. The same rule
applies to owner namespaces colliding case-insensitively at the Group level.

### 4.4. Version Identity

The `versionid` MUST be the Git commit SHA.

Commit SHAs are content-addressed and immutable, making them the natural Version
identity. The commit message MUST be carried in the `message` attribute so that
a Version is human-recognizable despite the opaque identifier.

The current tip of the default branch is the default Version. Because
`defaultversionsticky` is constrained to `false`, a new commit advances it.

Version lineage MUST be expressed through the xRegistry `ancestor` attribute,
derived from the commit graph.

If commit enrichment is unavailable — for example because anonymous access to
the commit list is refused — while repository metadata still exposes the HEAD
SHA, that SHA MUST be materialized as a minimal Version, so that the Resource
always has one resolvable default.

Git commit SHAs are 40 hexadecimal characters, well within the xRegistry Entity
ID length limit, and consist only of valid Entity ID characters, so no encoding
is required.

### 4.5. Timestamps

An implementation MUST set the core `createdat` attribute of a Version to the
commit date of that commit.

The Hub returns `createdAt` and `lastModified` on model, dataset and space
objects alike. These MUST be mapped onto the xRegistry *core* attributes
`createdat` and `modifiedat` of the Resource; this specification deliberately
declares no extension attributes for them, because the core attributes already
carry exactly that meaning.

| Hub field | xRegistry attribute |
|---|---|
| `createdAt` | core `createdat` of the Resource |
| `lastModified` | core `modifiedat` of the Resource |
| commit date | core `createdat` of the Version |

All three are RFC 3339 timestamps, so no conversion beyond normalization to UTC
is required.

## 5. Group: `huggingfaceregistry`

The Group (`<GROUP>`) name is `huggingfaceregistry` (singular); the plural, used
as the collection name, is `huggingfaceregistries`. A `huggingfaceregistry`
represents one Hub owner namespace.

| Group attribute | Type | Description |
|---|---|---|
| `namespace` | `string` | The canonical Hub owner namespace, or the empty string for the reserved `_` Group. |

## 6. Resources

### 6.1. Common Resource Attributes

All three Resource types share the following attributes:

| xRegistry attribute | Hub field | Type | Description |
|---|---|---|---|
| `name` | `id` | `string` | REQUIRED. The full Hub repository identity in `owner/name` form, verbatim. Authoritative; the Resource ID is only the basename and does not identify the repository on its own. |
| `repoid` | `id` (models also repeat it as `modelId`) | `string` | The full Hub repository ID, `owner/name` or the bare name. |
| `repository` | derived | `string` | The canonical `owner/repository` identity, or the bare ID for an unnamespaced repository. |
| `namespace` | derived | `string` | The canonical owner namespace, or the empty string for an unnamespaced repository. |
| `author` | `author` | `string` | The owner or organization that publishes the repository. |
| `sha` | `sha` | `string` | The commit SHA at the tip of the default branch. |
| `message` | commit title | `string` | The commit title or message of a Version. |
| `siblings` | `siblings` | `array` of `object` | The file manifest of this commit, see [6.4](#64-file-manifest). |

The Hub has no field called `repoid`; the upstream field is `id`, and models
additionally carry the legacy duplicate `modelId`. The xRegistry attribute is
named `repoid` because `id` alone would read ambiguously beside the xRegistry
core `<SINGULAR>id` attributes.

`repoid` and `repository` are both retained: `repoid` is the value the Hub API
returns, while `repository` is the canonicalized identity this specification
derives. They coincide in the ordinary case and diverge for bare repositories.

The repository timestamps `createdAt` and `lastModified` are *not* extension
attributes; they are mapped onto the xRegistry core attributes as described in
[4.5](#45-timestamps).

### 6.2. Common Meta Attributes

The following are declared as Resource `metaattributes` because they describe
the repository as a whole rather than any single commit:

| xRegistry attribute | Hub field | Type | Description |
|---|---|---|---|
| `private` | `private` | `boolean` | Whether the repository is private. |
| `gated` | `gated` | `any` | Gated-access state: `false`, `"auto"` or `"manual"`. |
| `disabled` | `disabled` | `boolean` | Whether the repository has been disabled by the Hub. |
| `used_storage` | `usedStorage` | `uinteger` | Storage consumed by the repository, in bytes. |
| `likes` | `likes` | `uinteger` | Like count. |
| `card_data` | `cardData` | `object` | The repository card front matter, see below. |
| `tags` | `tags` | `array` of `string` | Repository tags. |
| `refs` | `/refs` response | `object` | Branch, tag and conversion pointers, see [6.3](#63-branch-tag-and-conversion-references). |

`downloads` is deliberately *not* in this table. The Hub reports a download
count for models and datasets only; a space is executed, not downloaded, and
`GET /api/spaces/{owner}/{name}` returns no such field. It is therefore declared
on `model` and `dataset` alone rather than fabricated for `space`.

`gated` is typed `any` because the Hub overloads it across a boolean and two
string states. `"auto"` means access is granted on acceptance of terms;
`"manual"` means a human approves each request. Coercing the value to a boolean
would erase that distinction.

`card_data` is the parsed YAML front matter of the repository card. Its only
key guaranteed enough interest to be declared explicitly is `license`; every
other key is admitted through a wildcard attribute, because the front matter is
author-controlled and open-ended. The declaration uses the extended name
character set so that hyphenated card keys survive verbatim.

### 6.3. Branch, Tag and Conversion References

```yaml
"refs": {
  "branches": [
    { "name": "STRING", "ref": "STRING", "targetcommit": "STRING" } *
  ],
  "tags": [
    { "name": "STRING", "ref": "STRING", "targetcommit": "STRING" } *
  ],
  "converts": [
    { "name": "STRING", "ref": "STRING", "targetcommit": "STRING" } *
  ]
}
```

`refs` records mutable pointers into the commit history, as returned by the
Hub's `/api/{type}/{repo}/refs` endpoint. Each `targetcommit` maps the upstream
`targetCommit` field and MUST be a commit SHA that is, or could be, a Version of
this Resource. `name` is the short reference name and `ref` is the fully
qualified Git reference, for example `refs/heads/main`; both are returned
upstream and both are retained, because the short name alone cannot distinguish
a branch from an identically named tag.

`converts` carries the Hub's auto-generated conversion references, such as
`refs/convert/parquet` for datasets. They are ordinary Git references pointing
at machine-generated commits, so they belong beside `branches` and `tags` rather
than being dropped.

Branches, tags and conversions are deliberately *not* Versions. A reference
moves; a Version identity must not. Placing them on the Meta entity keeps the
Versions collection immutable while retaining the human-meaningful names.

### 6.4. File Manifest

```yaml
"siblings": [
  {
    "rfilename": "STRING",
    "size": UINTEGER,
    "blobid": "STRING",
    "lfs": { "size": UINTEGER, "sha256": "STRING", "pointersize": UINTEGER }
  } *
]
```

`siblings` is the Hub's file manifest for a repository at a given revision. It
is declared as a Resource attribute rather than a Meta attribute because its
content is a property of the commit: different Versions of the same Resource
have different file lists.

`rfilename` is the repository-relative path and is the only member the Hub
returns unconditionally. `size`, `blobid` (upstream `blobId`) and `lfs` appear
only when blob details are requested, and `lfs` only for LFS-tracked files;
`lfs.pointersize` maps the upstream `pointerSize`. An implementation MUST omit
the members the Hub did not supply rather than substituting zero.

Because this specification projects a content registry, the manifest is the
single most consequential piece of repository metadata: without it a consumer
can discover that a model exists but not what it consists of.

### 6.5. Resource: `model`

The Resource (`<RESOURCE>`) name is `model` (singular); the plural, used as the
collection name, is `models`. It carries the common attributes of
[6.1](#61-common-resource-attributes), the common Meta attributes of
[6.2](#62-common-meta-attributes), and additionally:

| Meta attribute | Hub field | Type | Description |
|---|---|---|---|
| `downloads` | `downloads` | `uinteger` | Download count as anonymously visible. |
| `pipeline_tag` | `pipeline_tag` | `string` | The primary machine-learning task, e.g. `text-generation`. |
| `library_name` | `library_name` | `string` | The primary library required to load the model, e.g. `transformers`, `diffusers`. |
| `config` | `config` | `object` | Model configuration summary, e.g. `architectures`, `model_type`. Open-ended, admitted through a wildcard attribute. |
| `transformers_info` | `transformersInfo` | `object` | Transformers auto-class information: `auto_model`, `pipeline_tag`, `processor`. |
| `safetensors` | `safetensors` | `object` | Weight summary: `parameters`, a map of dtype to count, and `total`. |
| `model_index` | `model-index` | `array` of `any` | The evaluation-results block of the model card. |
| `inference` | `inference` | `any` | Inference provider availability; the Hub returns either a string state or a boolean. |
| `widget_data` | `widgetData` | `array` of `any` | Example inputs shown by the Hub widget. |

`pipeline_tag` and `library_name` are the two facets by which the Hub's own
model discovery is organized: the former states what the model does, the latter
what is needed to run it. `config`, `transformers_info` and `safetensors` state
what the model *is* — its architecture, its loading entry points, and its
parameter count — and are the fields a consumer needs to size a deployment
without downloading the weights.

`model_index` retains the upstream hyphenated name in its description but is
declared as `model_index`, matching the snake_case convention used by the other
attributes in this model.

### 6.6. Resource: `dataset`

The Resource (`<RESOURCE>`) name is `dataset` (singular); the plural, used as
the collection name, is `datasets`. It carries the common attributes of
[6.1](#61-common-resource-attributes), the common Meta attributes of
[6.2](#62-common-meta-attributes), and additionally:

| Meta attribute | Hub field | Type | Description |
|---|---|---|---|
| `downloads` | `downloads` | `uinteger` | Download count as anonymously visible. |
| `paperswithcode_id` | `paperswithcode_id` | `string` | The Papers With Code identifier of the dataset. |

The Hub returns a `description` field on dataset objects. It MUST be mapped onto
the xRegistry core `description` attribute rather than onto an extension
attribute of the same name; the core attribute already carries that meaning, and
duplicating it would leave two authoritative descriptions.

A dataset has no `pipeline_tag`: the task association of a dataset is expressed
through `tags` rather than through a single primary task.

### 6.7. Resource: `space`

The Resource (`<RESOURCE>`) name is `space` (singular); the plural, used as the
collection name, is `spaces`. It carries the common attributes of
[6.1](#61-common-resource-attributes), the common Meta attributes of
[6.2](#62-common-meta-attributes), and additionally:

| Meta attribute | Hub field | Type | Description |
|---|---|---|---|
| `sdk` | `sdk` | `string` | The framework the space runs on: `gradio`, `streamlit`, `docker`, `static`, and others. |
| `runtime` | `runtime` | `object` | The current runtime state, see below. |
| `subdomain` | `subdomain` | `string` | The subdomain label under which the space is served. |
| `host` | `host` | `string` | The fully qualified host name serving the running space. |

```yaml
"runtime": {
  "stage": "STRING",
  "hardware": { "current": "STRING", "requested": "STRING" },
  "resources": {
    "cpu": "STRING", "memory": "STRING",
    "gpu": "STRING", "gpu_memory": "STRING"
  }
}
```

`sdk` determines how the Hub builds and serves the space, and is therefore the
attribute that distinguishes an executable space from a plain repository.
`runtime` states whether that executable is actually running: `stage` reports
the lifecycle state, such as `RUNNING`, `SLEEPING` or `BUILDING`, `hardware`
reports the allocated and requested hardware flavors, and `resources` reports
the CPU, memory and GPU allocation.

`subdomain` and `host` are the addressing pair for a running space and let a
consumer reach the deployed application rather than only its source.

A space has no `downloads` attribute, for the reason given in
[6.2](#62-common-meta-attributes).

## 7. Access Control

This specification describes a projection of *anonymously visible* Hub content.

An implementation MUST NOT configure or forward a Hub access token. An incoming
`Authorization` header MUST be rejected rather than passed upstream, so that the
projection cannot become a credential-laundering path to private repositories.

Consequently, `private` is expected to be `false` for every projected
repository, and gated repositories are projected with metadata only.

## 8. Conformance

An implementation conforms to this specification when:

1. It serves a model equivalent to [`model.json`](model.json), and
2. it applies the identity mapping in [Section 4](#4-identity-mapping), and
3. it enforces the access-control rules of [Section 7](#7-access-control), and
4. every attribute it populates carries the meaning assigned in
   [Section 6](#6-resources).

An implementation MAY expose additional extension attributes. An implementation
MAY omit any attribute for which the Hub supplies no value.

[xRegistry Core]: https://xregistry.io/xreg/xregistryspecs/core-v1/docs/spec.html
[xRegistry singularid]: https://xregistry.io/xreg/xregistryspecs/core-v1/docs/spec.html#singularid-id-attribute
[HF Hub]: https://huggingface.co/
[HF Hub OpenAPI]: https://huggingface.co/.well-known/openapi.json
