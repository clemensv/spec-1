# xRegistry Ecosystem Extensions
<!-- words: artifactid composerregistries containerregistries -->
<!-- words: dartregistries dotnet dotnetregistries ghcr goregistries -->
<!-- words: huggingface huggingfaceregistries javanamespaces mcp -->
<!-- words: mcpproviders namespace namespaces nodejs nodescopes nuget -->
<!-- words: packagist php pypi pythonregistries registryhost rubygems -->
<!-- words: rubyregistries rustregistries sourceurl terraform -->
<!-- words: terraformregistries versionnormalized xh -->

This directory contains specifications that express the metadata of existing
package, artifact and service registries in terms of
[xRegistry](https://xregistry.io/).

Each specification is *descriptive*. It does not propose a new metadata
standard; it documents how an ecosystem's native metadata is projected onto the
xRegistry Group / Resource / Version model, which identity encodings are used,
and which modelling decisions preserve — or would have destroyed — meaning
present upstream.

Every extension directory contains:

- `model.json` — the normative xRegistry model definition, servable as-is.
- `spec.md` — the formal specification of the mapping.

## Extensions

| Extension | Ecosystem | Group (plural) | Resource (plural) |
|---|---|---|---|
| [dart-pub-dev](dart-pub-dev/spec.md) | Dart & Flutter / pub.dev | `dartregistries` | `packages` |
| [dotnet-nuget](dotnet-nuget/spec.md) | .NET / NuGet | `dotnetregistries` | `packages` |
| [go-modules](go-modules/spec.md) | Go modules / module proxy | `goregistries` | `modules` |
| [huggingface-hub](huggingface-hub/spec.md) | Hugging Face Hub | `huggingfaceregistries` | `models`, `datasets`, `spaces` |
| [java-maven-central](java-maven-central/spec.md) | Java / Maven Central | `javanamespaces` | `packages` |
| [mcp-server-registry](mcp-server-registry/spec.md) | Model Context Protocol servers | `mcpproviders` | `servers` |
| [nodejs-npm](nodejs-npm/spec.md) | Node.js / npm | `nodescopes` | `packages` |
| [oci-container-registry](oci-container-registry/spec.md) | OCI container registries | `containerregistries` | `images` |
| [php-packagist](php-packagist/spec.md) | PHP / Composer / Packagist | `composerregistries` | `packages` |
| [python-pypi](python-pypi/spec.md) | Python / PyPI | `pythonregistries` | `packages` |
| [ruby-rubygems](ruby-rubygems/spec.md) | Ruby / RubyGems | `rubyregistries` | `packages` |
| [rust-crates-io](rust-crates-io/spec.md) | Rust / crates.io | `rustregistries` | `crates` |
| [terraform-registry](terraform-registry/spec.md) | Terraform Registry | `terraformregistries` | `providers`, `modules` |

## Recurring Mapping Concerns

The specifications differ in detail but repeatedly confront the same problems.

**Identity encoding.** Every extension has to express an upstream identifier as
an xRegistry Entity ID, and upstream identifiers routinely contain characters
that an Entity ID cannot. The rule below is common to all of them; each
specification restates it normatively for its own ecosystem.

An Entity ID is limited to the [RFC3986 `unreserved`
characters](https://datatracker.ietf.org/doc/html/rfc3986#section-2.3) (ALPHA,
DIGIT, `-`, `.`, `_`, `~`) plus `:` and `@`, must start with ALPHA, DIGIT or
`_`, and is at most 128 characters. Two consequences drive every mapping in this
directory:

- **Percent-encoding is unavailable.** `%` is not itself a legal Entity ID
  character, so the usual escape hatch cannot be used. This is stated explicitly
  because it is the first thing an implementer reaches for.
- **Entity IDs are unique case-*insensitively* within their parent.** Upstream
  identifiers that differ only in case therefore collide, even though upstream
  treats them as distinct. Go solved exactly this problem for its module proxy
  with the `!lower` escape; the same hazard applies to case-sensitive Maven
  `artifactId`s and crate names.

Crucially, an Entity ID does **not** need to be reversible. xRegistry Core
notes that a `<SINGULAR>id` may be "something that isn't human friendly, like a
UUID", and carries the readable value in `name` instead. Every extension here
therefore preserves the exact upstream identifier verbatim in `name` (or in a
named ecosystem attribute such as `version`), and requires consumers addressing
the origin registry to read that attribute rather than decode an identifier.

Two corollaries follow, and both are binding on every extension in this
directory:

- **The authoritative name is REQUIRED, not optional.** Core leaves `name`
  OPTIONAL, but an identifier that cannot be reversed is useless without it, so
  each extension redeclares its authoritative name attribute as `required`.
  Without that, a projection could omit the only verbatim copy of the upstream
  name and still be valid. Where Core `name` is already bound to an upstream
  *display* name — Maven's `project/name`, which is prose such as "Apache
  Commons Lang" and not the `artifactId` — the ecosystem attributes carrying
  identity (`group_id`, `artifact_id`) are the ones marked required instead.
- **`name` names the Resource, never the Version string.** Core defines a single
  `name` per entity, so an extension cannot bind `name` to the Resource's
  package name and to the version string on the Version; one silently overwrites
  the other. The verbatim upstream version therefore always lives in a named
  attribute — `version`, `num` or `versionnormalized` — and never in `name`.

An identifier must only be **deterministic, stable and collision-free**. Freed
from reversibility, the extensions derive identifiers in this order of
preference:

1. Use the upstream identifier **verbatim** when it is already legal.
2. Otherwise **transliterate** the illegal characters to a legal stand-in that
   cannot occur upstream, keeping the identifier readable. `~` is the usual
   stand-in, being legal here and absent from most upstream grammars.
3. Only where neither is possible — a residual collision, or a value over 128
   characters — fall back to a hash, using the reserved `xh~` prefix followed by
   the lowercase hex SHA-256 of the UTF-8 bytes of the upstream identifier.

Separately, identifiers containing `/` — npm scopes, Go module paths, Composer
vendor/package, OCI repository names, Hugging Face `owner/name` — are handled
wherever possible by promoting the leading component to the Group, so that the
`/` becomes the Group/Resource boundary and needs no encoding at all.

**The Group as the projection boundary.** Where an ecosystem has no namespace
component to promote, the Group instead denotes the **projection**: one reading
of an upstream ecosystem's metadata model into the attributes these
specifications define. This covers the five ecosystems whose package names are
flat, and their Group identifiers are the fixed tokens `nuget`, `pypi`,
`rubygems`, `crates-io` and `pub`.

The identifier is deliberately not a host, a feed or an account. A flat
ecosystem's package name is global — a NuGet package ID or a PyPI project name
denotes the same artifact whoever serves it — so binding the serving authority
into the path would make the same artifact unreachable under the same URI when
it is served from a mirror, an internal proxy or a private network. Keeping the
Group constant is what allows one registry to shadow another, as described in
[Section 8.3 of the core primer](../core/primer.md).

Holding a constant there is not wasted, because it gives the ecosystem somewhere
to put disagreement and change:

- **Breaking upstream change.** When an upstream registry adopts a metadata
  model that cannot be projected into the existing attributes without loss or
  contradiction, the new model takes a new Group identifier — `nuget-v4`,
  `pypi-v2` — and the two coexist in one registry. A client selects the model it
  understands instead of being handed attributes whose meaning changed
  underneath it.
- **Conflicting definitions.** Where two parties project the same ecosystem
  under incompatible interpretations, each takes its own Group identifier. A
  Group therefore identifies an ecosystem together with the reading of it that
  produced the entries, and any two entries within one Group are directly
  comparable.

Access control is a property of the registry deployment rather than of the
identifier. A registry serving only a private feed still serves it under the
same Group, and may omit entries the caller is not entitled to see; absence is
not evidence that an artifact does not exist upstream.

OCI container registries are the exception, and deliberately so. An OCI
repository name is not global: `library/nginx` means nothing without a registry,
and the registry name is written into every fully qualified reference. There the
registry name is part of the artifact's own identity rather than an address, so
`containerregistries` keeps host-shaped identifiers — `docker.io`, `ghcr.io` —
and a pull-through cache files images under the registry the reference names
rather than under its own.

Each of these Groups carries an OPTIONAL `sourceurl` attribute holding the base
URL the artifacts were projected from, matching the attribute of the same name
already used by the npm and Maven Groups. It records provenance and never
identity, which is also why it can differ between two registries serving the
same entries.

`sourceurl` is the default name for that idea, but it does not displace a name
the ecosystem already has. Terraform keeps `registryhost`, because service
discovery is defined over a *host* rather than a base URL and the discovery
document is what supplies the paths; and an OCI image keeps a `registry` meta
attribute recording the registry that actually served it, because a registry
name is a syntactic element of an image reference and not a URL. Renaming either
onto `sourceurl` would have made these mappings read less like the ecosystem
they describe, for the sake of a consistency no consumer needs.

The remaining Groups are namespaces, even where the name suggests otherwise:
`goregistries` holds the leading component of a module path,
`huggingfaceregistries` a Hub owner, `composerregistries` a Composer vendor, and
`mcpproviders` the reverse-DNS namespace of a server name.

**Version ordering.** `versionmode` is chosen per ecosystem according to what
the upstream registry actually guarantees: `semver` where SemVer is mandated,
`createdat` where publication order is authoritative, and `manual` where the
version string carries no reliable order.

**Mutability.** Most package versions are immutable once published. OCI tags and
Hugging Face branches are not. Where a Version identity is mutable, the
specification says so explicitly and names the immutable content identity
(a digest or commit SHA) that a consumer must pin to instead.

**Cross-registry references.** The
[mcp-server-registry](mcp-server-registry/spec.md) extension links MCP server
entries to the npm, PyPI, OCI and NuGet extensions through typed `xid`
attributes, so that a federated deployment of these extensions is navigable from
a service catalogue into the package graph.
