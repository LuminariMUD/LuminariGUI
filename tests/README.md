# LuminariGUI Test Data and Mocks

This directory contains test data, mock files, and utilities for the LuminariGUI testing infrastructure.

## Directory Structure

- `mock_data/` - Mock MSDP data, XML snippets, and test fixtures
- `sample_scripts/` - Sample Lua scripts for testing
- `expected_outputs/` - Expected test outputs for validation
- `test_configs/` - Configuration files for test scenarios

## Test Data Files

### Mock MSDP Data
- `mock_msdp_room.json` - Sample room data
- `mock_msdp_affects.json` - Sample affects data  
- `mock_msdp_group.json` - Sample group data

### Sample Scripts
- `simple_function.lua` - Basic function for unit testing
- `event_handler.lua` - Sample event handler
- `performance_test.lua` - Performance benchmark script

### Test Configurations
- `luacheck_config.lua` - Luacheck configuration for testing
- `test_settings.json` - Test runner settings

## Usage

These test files are automatically used by the testing infrastructure. You can also use them manually for debugging or developing new tests.

## Adding New Test Data

When adding new test data:

1. Follow the existing naming conventions
2. Include both positive and negative test cases
3. Document the purpose in comments
4. Add corresponding tests in the main test files