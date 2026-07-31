# LuminariGUI Chunk Audit Plan

> **Historical layout note:** This audit predates the composite GUI source
> migration. References to `src/scripts/01_gui.xml` describe the former
> monolithic source and are superseded by
> [`split-gui-source.md`](split-gui-source.md) and the focused files under
> `src/scripts/gui/`. The trigger file with the same basename is unchanged.

This document defines the comprehensive audit checklist for reviewing and perfecting each source fragment in `theGUI/src/`.

## Audit Overview

**Goal:** Ensure each chunk follows project conventions, is well-structured, properly documented, and production-ready.

**Last Audit:** 2025-11-29 (Session 2 - Phase 4 Testing complete)

**Source Files to Audit:**
| Category | File | Component | Status |
|----------|------|-----------|--------|
| Scripts | `00_msdpmapper.xml` | MSDP protocol & room mapping | ✅ Complete |
| Scripts | `01_gui.xml` | Main GUI framework (large) | ✅ Complete |
| Scripts | `02_yatcoconfig.xml` | Chat configuration | ✅ Complete |
| Scripts | `03_yatco.xml` | Tabbed chat system | ✅ Complete |
| Triggers | `00_yatcoconfig.xml` | YATCO config triggers | ✅ Complete |
| Triggers | `01_gui.xml` | GUI-related triggers | ✅ Complete |
| Aliases | `00_toggles.xml` | Toggle commands | ✅ Complete |
| Aliases | `01_yatco.xml` | YATCO chat aliases | ✅ Complete |
| Keys | `00_movement.xml` | Numpad movement bindings | ✅ Complete |

---

## Master Audit Checklist

### 1. XML Structure Validation

- [x] **Valid XML syntax** - Fragment parses without errors
- [x] **Correct element hierarchy** - Proper nesting of Script/Trigger/Alias/Key groups
- [x] **Required attributes present** - `isActive`, `isFolder`, `name`
- [x] **Proper XML escaping** - `<` → `&lt;`, `>` → `&gt;`, `&` → `&amp;` in Lua code
- [x] **Consistent indentation** - Tabs for XML structure
- [x] **packageName consistency** - Either empty or matches component purpose
- [x] **eventHandlerList presence** - Required empty element for Scripts

### 2. Lua Namespacing & Globals

- [x] **GUI. prefix for GUI functions** - All GUI-related functions use `GUI.functionName`
- [x] **map. prefix for mapper functions** - All mapper functions use `map.functionName`
- [x] **demonnic. prefix for YATCO** - Chat system uses `demonnic.chat.*`
- [x] **Safe table initialization** - Use `GUI.Table = GUI.Table or {}` pattern
- [x] **No accidental globals** - All variables properly scoped with `local`
- [x] **Forward declarations** - Local functions declared before use

### 3. Error Handling & Robustness

- [x] **MSDP data fallbacks** - `tonumber(msdp.VALUE) or 0` pattern
- [x] **Nil checks before access** - Validate objects exist before using
- [x] **pcall for risky operations** - Wrap external calls that could fail
- [x] **Trigger cleanup** - Temp triggers properly killed with `exists()` check
- [x] **Event handler cleanup** - Use `registerAnonymousEventHandler` for auto-cleanup
- [x] **Resource cleanup** - Files closed, timers killed when appropriate

### 4. Event Registration Patterns

- [x] **Anonymous handlers preferred** - Use `registerAnonymousEventHandler()`
- [x] **Consistent handler naming** - `Namespace.onEventName` or `Namespace.handleEvent`
- [x] **Event name accuracy** - Correct event names (msdp.HEALTH, sysConnectionEvent, etc.)
- [x] **No duplicate registrations** - Guard against re-registering on reload
- [x] **Handler function exists** - Function defined before registration

### 5. CSS & Styling (CSSMan)

- [x] **CSSMan usage** - Use CSSMan.new() for dynamic styles
- [x] **Path handling in CSS** - `getMudletHomeDir():gsub("\\", "/")` for cross-platform
- [x] **Consistent color scheme** - Uses project color palette
- [x] **Border/padding consistency** - Standard values across components
- [x] **Font consistency** - Matches main window font size where appropriate

### 6. Path Handling

- [x] **Forward slashes** - All paths use `/` via `:gsub("\\", "/")`
- [x] **getMudletHomeDir() usage** - Base path for user files
- [x] **Package-relative paths** - `/LuminariGUI/` prefix for package resources
- [x] **No hardcoded paths** - All paths dynamically constructed

### 7. Code Quality

- [x] **Dead code removed** - No commented-out blocks without explanation
- [x] **Empty loops removed** - No `for k,v in pairs(t) do end` patterns
- [x] **Consistent spacing** - Space after commas, around operators
- [x] **Meaningful variable names** - Descriptive, not single letters (except loops)
- [x] **DRY principle** - No duplicated logic that could be functions
- [x] **Function length** - Large functions broken into logical sub-functions

### 8. Documentation

- [x] **File header comment** - Purpose of the chunk
- [x] **Complex function docs** - Brief description of non-obvious functions
- [x] **TODO markers** - Outstanding work clearly marked
- [x] **Configuration comments** - User-editable values explained
- [x] **No outdated comments** - Comments match current code behavior

### 9. Security Considerations

- [x] **No eval/loadstring with user input** - Avoid dynamic code execution
- [x] **Sanitized display output** - User data escaped before display
- [x] **Safe file operations** - Validate paths before read/write
- [x] **No credential storage** - No passwords/keys in code

### 10. Performance

- [x] **Efficient loops** - Avoid unnecessary iterations
- [x] **Cached lookups** - Repeated access stored in locals
- [x] **Lazy initialization** - Heavy operations deferred until needed
- [x] **Timer efficiency** - Appropriate intervals, consolidated where possible
- [x] **Event handler efficiency** - Quick checks before heavy processing

### 11. Mudlet Compatibility

- [x] **Geyser best practices** - Correct container parenting
- [x] **API version awareness** - Feature checks for newer APIs
- [x] **Resource cleanup** - Proper widget destruction
- [x] **Z-order management** - Consistent layering approach

---

## Per-Chunk Audit Status

### Scripts

#### `00_msdpmapper.xml` - MSDPMapper
- [x] XML Structure
- [x] Namespacing (uses `map.`)
- [x] Error Handling
- [x] Event Registration
- [x] Path Handling
- [x] Code Quality
- [x] Documentation
- **Issues Found & FIXED:**
  - ✅ Empty loop at line 88-90 - REMOVED
  - ✅ Inconsistent indentation in terrain_types table - FIXED (aligned all entries)
  - ✅ `downloading` variable was global - FIXED to `map.downloading`
  - ✅ Commented-out code blocks - REMOVED (cleaned up dead code)
  - ✅ Duplicate alias creation - REMOVED
  - ✅ Added file header comment
  - ✅ Fixed packageName consistency

#### `01_gui.xml` - Main GUI Framework
- [x] XML Structure
- [x] Namespacing (uses `GUI.`)
- [x] Error Handling
- [x] Event Registration
- [x] CSS Styling
- [x] Path Handling
- [x] Code Quality
- [x] Documentation
- **Issues Found & FIXED:**
  - ✅ Path handling - Added `:gsub("\\", "/")` to all getMudletHomeDir() calls
  - ✅ Removed commented-out dead code blocks (GUI.Top, Icon loop)
  - Note: Large file - consider splitting in future refactor

#### `02_yatcoconfig.xml` - YATCO Configuration
- [x] XML Structure
- [x] Namespacing (uses `demonnic.chat.config`)
- [x] Documentation
- [x] Code Quality
- **Issues Found & FIXED:**
  - ✅ Minor indentation fix in channels table
  - Well documented configuration options - no other issues

#### `03_yatco.xml` - Tabbed Chat System
- [x] XML Structure
- [x] Namespacing (uses `demonnic.`)
- [x] Error Handling
- [x] Event Registration
- [x] Code Quality
- [x] Documentation
- **Issues Found & FIXED:**
  - ✅ Fixed comment typos ("0then" → "then", "Anonymouse" → "Anonymous")
  - ✅ Path handling - Added `:gsub("\\", "/")` to sound file paths
  - Note: `demonnicChatSwitch` intentionally global (Mudlet setClickCallback requires global function name)

### Triggers

#### `00_yatcoconfig.xml` - YATCO Config Triggers
- [x] XML Structure
- [x] Trigger Patterns
- [x] Script Quality
- **Issues Found:**
  - No issues - clean trigger definitions with proper namespace usage

#### `01_gui.xml` - GUI Triggers
- [x] XML Structure
- [x] Trigger Patterns
- [x] Namespace Usage
- [x] Error Handling
- **Issues Found & FIXED:**
  - ✅ Global variables `maplineTrig` and `padding` - FIXED to `map.maplineTrig` and `map.padding`
  - Good error handling with pcall
  - Proper trigger cleanup pattern with exists() check
  - Note: `onMapLine` and `onRoomMapLine` intentionally global (Mudlet tempLineTrigger callback requirement)

### Aliases

#### `00_toggles.xml` - Toggle Commands
- [x] XML Structure
- [x] Alias Patterns (regex)
- [x] Namespace Usage
- [x] Help Text
- **Issues Found:**
  - No issues - clean and minimal

#### `01_yatco.xml` - YATCO Aliases
- [x] XML Structure
- [x] Alias Patterns
- [x] Namespace Usage
- **Issues Found & FIXED:**
  - ✅ Path handling - Added `:gsub("\\", "/")` to all getMudletHomeDir() calls in sound-related aliases

### Keys

#### `00_movement.xml` - Movement Bindings
- [x] XML Structure
- [x] Key Code Accuracy
- [x] Command Correctness
- **Issues Found:**
  - No issues - clean, simple structure
  - Uses numpad with modifier (536870912)

---

## Audit Process

### Phase 1: Automated Validation ✅ COMPLETE
```bash
# Validate XML and Lua syntax
python3 theGUI/build.py --validate
python3 tests/run_tests.py
```

### Phase 2: Manual Code Review ✅ COMPLETE
1. Open each chunk in editor
2. Walk through master checklist
3. Document issues in "Issues Found" section
4. Prioritize fixes (Critical/High/Medium/Low)

### Phase 3: Fixes ✅ COMPLETE
1. Address Critical issues first
2. Create focused commits per chunk
3. Re-run validation after each fix
4. Update audit status checkboxes

### Phase 4: Testing ✅ COMPLETE (Automated)
1. Build package: `python3 theGUI/build.py` ✅
2. Validate package structure ✅
3. Import into Mudlet - requires manual testing
4. Test each component manually - requires manual testing

**Phase 4 Results (2025-11-29):**
- **Build:** v2.0.4.018, 5026 lines generated successfully
- **XML Structural Validation:** PASSED
- **Lua Syntax Validation:** PASSED (57/57 scripts)
- **Full Test Suite:** ALL TESTS PASSED
  - Event System: 5/5 tests passed
  - System Tests: 6/6 tests passed
  - Function Tests: 10/10 tests passed
  - Performance Benchmarks: 7/7 tests passed
- **Style Warnings:** 15 cosmetic warnings (function keyword spacing) - non-blocking
- **False Positive Warnings:** validate_package.py reported "unescaped <>" but these are XML tags, not content issues

---

## Priority Classification

| Priority | Description | Action |
|----------|-------------|--------|
| **Critical** | Breaks functionality, security issue | Fix immediately |
| **High** | Bug, incorrect behavior | Fix before release |
| **Medium** | Convention violation, code smell | Fix in audit pass |
| **Low** | Style preference, minor cleanup | Fix as time permits |

---

## Completion Tracking

| Chunk | Phase 1 | Phase 2 | Phase 3 | Phase 4 | Complete |
|-------|---------|---------|---------|---------|----------|
| scripts/00_msdpmapper.xml | [x] | [x] | [x] | [x] | [x] |
| scripts/01_gui.xml | [x] | [x] | [x] | [x] | [x] |
| scripts/02_yatcoconfig.xml | [x] | [x] | [x] | [x] | [x] |
| scripts/03_yatco.xml | [x] | [x] | [x] | [x] | [x] |
| triggers/00_yatcoconfig.xml | [x] | [x] | [x] | [x] | [x] |
| triggers/01_gui.xml | [x] | [x] | [x] | [x] | [x] |
| aliases/00_toggles.xml | [x] | [x] | [x] | [x] | [x] |
| aliases/01_yatco.xml | [x] | [x] | [x] | [x] | [x] |
| keys/00_movement.xml | [x] | [x] | [x] | [x] | [x] |

---

## Summary of Fixes Applied (2025-11-29)

### High Priority Fixes
1. **Global Variables Fixed:**
   - `downloading` → `map.downloading` (scripts/00_msdpmapper.xml)
   - `maplineTrig` → `map.maplineTrig` (triggers/01_gui.xml)
   - `padding` → `map.padding` (triggers/01_gui.xml)

### Medium Priority Fixes
1. **Path Handling:** Added `:gsub("\\", "/")` to all `getMudletHomeDir()` calls for cross-platform compatibility
2. **Dead Code Removed:**
   - Empty loop in 00_msdpmapper.xml
   - Commented-out GUI.Top and Icon loop in 01_gui.xml
   - Duplicate alias creation in 00_msdpmapper.xml
3. **Code Quality:**
   - Fixed inconsistent indentation in terrain_types table
   - Fixed indentation in channels table
   - Fixed typos in comments

### Low Priority Fixes
1. **Documentation:** Added file header comment to 00_msdpmapper.xml
2. **packageName:** Fixed consistency in 00_msdpmapper.xml

### Known Intentional Globals
These are global by design due to Mudlet API requirements:
- `demonnicChatSwitch` - Required for `setClickCallback` (string function name)
- `onMapLine` - Required for `tempLineTrigger` callback
- `onRoomMapLine` - Required for `tempLineTrigger` callback

---

## Notes

- Edit source files in `theGUI/src/`, NOT `LuminariGUI.xml` directly
- Always run `python3 theGUI/build.py --validate` before building
- Commit source files, `theGUI/build.yaml`, built `LuminariGUI.xml`, and any
  new tracked archive
- Reference `AGENTS.md` for project conventions

## Next Steps

All automated phases complete. Remaining items for manual verification:

- [x] Install Lua tools for full syntax validation ✅
- [x] Run full test suite (28/28 tests passed) ✅
- [ ] Import `LuminariGUI.xml` (v2.0.4.018) into Mudlet
- [ ] Test MSDP mapper functionality with live connection
- [ ] Test YATCO tabbed chat system
- [ ] Test GUI gauges and status displays
- [ ] Test alias and key bindings
- [ ] Verify no regressions from audit fixes

## Audit Complete

**Status:** ✅ COMPLETE (Automated phases)

The chunk audit has identified and fixed all issues found during code review:
- 3 global variable leaks fixed
- Path handling standardized across all chunks
- Dead code removed
- Documentation improved
- Code quality issues resolved

The package builds successfully and passes XML structural validation. Manual in-Mudlet testing recommended before release.
