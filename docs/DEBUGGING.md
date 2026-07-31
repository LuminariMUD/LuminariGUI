# LuminariGUI screen diagnostics

LuminariGUI has one master diagnostic switch, defined at the start of
`theGUI/src/scripts/00_debug.xml`:

```lua
GUI.DEBUG = true
```

This is the only persistent debug-mode setting. Set it to `false` and rebuild
the package when the startup problem has been resolved.

While enabled, diagnostics are deliberately verbose and are written directly
to Mudlet's main console. Normal trace lines begin with `[LGUI-DEBUG`, caught
errors begin with `[LGUI-ERROR`, and complete stack-trace lines begin with
`[LGUI-TRACE]`.

Coverage includes:

- fragment loading and the early GUI construction boundary;
- required APIs, functions, runtime objects, package assets, and versions;
- Mudlet lifecycle events and delayed callbacks;
- MSDP enablement, `REPORT` requests, received variables, and handler calls;
- GUI component initialization and refresh stages;
- mapper setup, downloads, room transitions, movement, and map triggers;
- adjustable-container creation, profiles, visibility, and persistence;
- YATCO configuration, startup, tabs, captured chat, sound, and timers;
- package aliases and movement keybindings.

Errors are caught only while `GUI.DEBUG` is `true`, allowing later diagnostic
code to load and report state even if an early stage fails. With the switch
`false`, functions are called directly and errors propagate normally.
Dependent GUI stages now stop before creating widgets when their core parent
containers are unavailable, so a diagnostic failure cannot create full-screen
orphan controls on Mudlet's root window.

The existing in-game `debug` alias toggles the same `GUI.DEBUG` value for the
current session. It does not create a second setting and does not edit the XML.

For a useful report, reopen the profile and copy from the first
`[LGUI-DEBUG` line whose scope is `[BOOT]` through the first `[LGUI-ERROR` and its
`[LGUI-TRACE]` lines. Include the subsequent `SNAPSHOT` and `MSDP` lines when
available.
