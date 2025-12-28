# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.4.0] - 2025-12-28

### Added

- `inherit_context` class attribute for explicit control over parent context inheritance
  - Set to a list/tuple of variable names to inherit only those variables from parent context
  - Example: `inherit_context = ("request", "user")`

### Changed

- **BREAKING**: Bricks now have **context isolation by default** - they no longer inherit
  the parent template context automatically. This prevents unwanted parameter shadowing
  where parent context variables could override brick optional parameters.
  - To restore access to parent context variables (like `request`, `user`, etc.),
    add `inherit_context = ("request", "user", ...)` to your brick class
  - Brick's own context always takes precedence over inherited context

### Fixed

- Parent template context variables no longer shadow brick optional parameters
  - Previously, if a parent template had `class` in context and a brick had
    `class_: str | None = None`, the parent's value would leak into the brick
  - Now bricks are isolated by default, preventing this issue

## [0.3.0] - 2025-12-12

### Added

- Support for template filter expressions in brick kwarg values (e.g., `{% mybrick title=name|title %}`)
- Bricks now inherit the parent template context, giving access to `request` and other context processor variables
- Special handling for `class` kwarg - can now use `class="foo"` directly instead of `class_="foo"`
- Support for `Any`-typed kwargs (skips validation)
- Support for Django's `gettext_lazy` proxy objects in `str`-typed kwargs

### Changed

- Validation error messages now include the brick name for easier debugging

## [0.2.0] - 2025-12-11

### Added

- `extra` dict for collecting undefined kwargs passed to bricks
- `attrs` template filter for converting `extra` dict to HTML attributes
- Sphinx documentation for Read the Docs

### Changed

- Renamed `extra_attrs` to `extra`

## [0.1.0] - 2025-12-10

### Added

- Initial release
- `Brick` base class for simple template components
- `BlockBrick` base class for components that wrap children
- `@register` decorator for registering bricks as template tags
- Type validation for brick kwargs
- Django `Media` class support for CSS/JS assets
- Autodiscovery of bricks from `bricks.py` modules

[Unreleased]: https://github.com/philippbosch/django-brick-astley/compare/v0.4.0...HEAD
[0.4.0]: https://github.com/philippbosch/django-brick-astley/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/philippbosch/django-brick-astley/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/philippbosch/django-brick-astley/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/philippbosch/django-brick-astley/releases/tag/v0.1.0
