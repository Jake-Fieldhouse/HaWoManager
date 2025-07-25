# Changelog

All notable changes to this project will be documented in this file.

## [0.0.10] - 2025-07-20
### Added
- REST API for device management and JSON import/export.
- Interactive management panel showing device status and actions.
- Config flow checks for duplicate IP addresses and allows specifying icon and area.

## [0.0.9] - 2025-07-12
### Added
- Permanent sidebar panel for device management.

## [0.0.8] - 2025-07-11
### Removed
- CLI functionality and `pip` installation instructions. The integration is now
  installed exclusively through HACS.


## [0.0.7] - 2025-06-14
### Added
- CLI entry points for `womgr-cli` and `dashboard-cli` scripts

The release is tagged as `v0.0.7`.

## [0.0.6] - 2025-06-13
### Fixed
- Use lovelace property access for Home Assistant 2026.2 compatibility

The release is tagged as `v0.0.6`.

## [0.0.5] - 2025-06-12
### Added
- Bubble Card pop-up layout for device cards

The release is tagged as `v0.0.5`.

## [0.0.4] - 2025-06-11
### Added
- Optional initial setup without specifying a device
- Windows-compatible ping parameters

The release is tagged as `v0.0.4`.

## [0.0.3] - 2025-06-10
### Fixed
- Bundled library so HACS installs work
- Correct invalid `hacs.json` format

The release is tagged as `v0.0.3` at commit `cbafd71`.

## [0.0.2] - 2025-06-10
### Added
- Automatic dashboard setup script
- Clarify HACS release usage in README
- CODEOWNERS file

### Changed
- Version bump for Home Assistant compatibility

The release is tagged as `v0.0.2` at commit `4b31a21`.
