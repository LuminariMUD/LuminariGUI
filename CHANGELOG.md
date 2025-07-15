# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Fixed auction channel capture by updating regex patterns to match actual game verbs
  - Changed `auctions` to `auctalks` for incoming auction messages
  - Changed `auction` to `auctalk` for outgoing auction messages
  - This resolves the issue where auction channel messages were not being captured in the chat system
