# EMCO Safety Measures and Testing Protocols

## Safety Architecture

### 1. Dual-System Support
The implementation maintains both YATCO and EMCO simultaneously:
- YATCO remains fully functional as fallback
- EMCO runs through compatibility layer
- Toggle between systems with simple command
- No code changes required to switch

### 2. Compatibility Layer Protection
The compatibility wrapper ensures:
- All YATCO API calls work unchanged
- Configuration automatically mapped
- Error handling prevents crashes
- Debug logging available for troubleshooting

### 3. Non-Destructive Installation
- No YATCO code is removed or modified
- All triggers remain unchanged
- Aliases continue to work
- User settings preserved

## Testing Protocol Checklist

### Pre-Installation Verification
- [ ] Create git backup tag: `git tag -a yatco-final-v2.0.4.016`
- [ ] Document current YATCO behavior
- [ ] Verify all chat channels working
- [ ] Test all aliases (gag chat, dblink, dsound, etc.)
- [ ] Check Adjustable Container functionality

### Installation Testing

#### Phase 1: Add EMCO Components
- [ ] Add EMCO script group
- [ ] Add demontools.lua script
- [ ] Add loggingconsole.lua script
- [ ] Add emco.lua script
- [ ] Add compatibility layer script
- [ ] Verify no errors on load

#### Phase 2: Initialize with Toggle
- [ ] Add toggle system alias
- [ ] Add EMCO initialization script
- [ ] Update demonnicOnStart() with conditional logic
- [ ] Test with `GUI.useEMCO = false` (YATCO mode)
- [ ] Verify YATCO still works perfectly

#### Phase 3: EMCO Testing
- [ ] Type `toggle chat system` to enable EMCO
- [ ] Restart Mudlet
- [ ] Check error console for issues
- [ ] Test each chat channel trigger:
  - [ ] Tell messages captured
  - [ ] Chat messages captured
  - [ ] Say messages captured
  - [ ] Group messages captured
  - [ ] Auction messages captured
  - [ ] Congrats messages captured
  - [ ] Wiz messages captured

#### Phase 4: Feature Testing
- [ ] Test `gag chat` toggle
- [ ] Test `dblink` for tab blinking
- [ ] Test `dsound` for sound notifications
- [ ] Test `set chat sound on/off/test`
- [ ] Test `fix chat` command
- [ ] Test channel color prefixes
- [ ] Test Adjustable Container resize/move

#### Phase 5: Stress Testing
- [ ] Run for 1 hour with normal gameplay
- [ ] Monitor memory usage
- [ ] Test with heavy chat activity
- [ ] Rapid tab switching
- [ ] Multiple simultaneous channels

### Rollback Testing
- [ ] Toggle back to YATCO: `toggle chat system`
- [ ] Restart Mudlet
- [ ] Verify YATCO works normally
- [ ] No residual EMCO effects

### Performance Benchmarks

#### Baseline (YATCO)
- Memory usage after 1 hour: _____MB
- CPU usage during chat: _____%
- Tab switch latency: _____ms
- Lines before lag: _____

#### EMCO Performance
- Memory usage after 1 hour: _____MB
- CPU usage during chat: _____%
- Tab switch latency: _____ms
- Lines before lag: _____

### Edge Case Testing
- [ ] Very long messages (500+ characters)
- [ ] Rapid consecutive messages (10+ per second)
- [ ] Special characters and emojis
- [ ] Color code sequences
- [ ] Empty messages
- [ ] Malformed color codes
- [ ] Tab names with spaces
- [ ] Case sensitivity in tab names

### Integration Testing
- [ ] GUI refresh with `fix gui`
- [ ] Profile loading/saving
- [ ] Mudlet restart persistence
- [ ] Container minimize/maximize
- [ ] Multi-profile support

## Success Metrics

### Required for Go-Live
1. **Zero Breaking Changes**: All existing functionality works
2. **Performance Parity**: No degradation vs YATCO
3. **Stable Operation**: No crashes in 24-hour test
4. **Easy Rollback**: Toggle switch works reliably
5. **User Transparency**: No visible changes unless user explores

### Nice to Have
1. **Performance Improvement**: Lower memory/CPU usage
2. **New Features**: Additional EMCO capabilities accessible
3. **Better Debugging**: Enhanced error messages

## Troubleshooting Guide

### Common Issues and Solutions

1. **EMCO won't initialize**
   - Check error console for missing dependencies
   - Verify all scripts loaded in correct order
   - Try toggling back to YATCO and restart

2. **Chat triggers not capturing**
   - Verify compatibility layer loaded
   - Check `demonnic.chat:append()` is wrapped correctly
   - Enable debug logging in compatibility layer

3. **Tabs not displaying correctly**
   - Check container assignment
   - Verify CSS/styling applied
   - Try `fix chat` command

4. **Sound notifications not working**
   - Verify sound file path
   - Check compatibility layer sound handling
   - Test with `set chat sound test`

5. **Performance degradation**
   - Check buffer sizes
   - Monitor blink timer frequency
   - Verify no duplicate event handlers

## Go/No-Go Decision Matrix

| Criteria | Required | Status | Notes |
|----------|----------|--------|-------|
| All triggers work | YES | [ ] | Must capture all channels |
| All aliases work | YES | [ ] | No user retraining |
| Performance acceptable | YES | [ ] | Equal or better than YATCO |
| Rollback works | YES | [ ] | Instant switch to YATCO |
| No data loss | YES | [ ] | Chat history preserved |
| Stable for 24 hours | YES | [ ] | No crashes or errors |
| Memory usage stable | YES | [ ] | No memory leaks |
| User approval | NO | [ ] | Nice to have |

## Final Approval
- [ ] All required criteria met
- [ ] Testing documented
- [ ] Rollback plan verified
- [ ] Ready for production use