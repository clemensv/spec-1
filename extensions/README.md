# xRegistry Ecosystem Extensions

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
