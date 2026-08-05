# Mudlet 4.22 analysis stubs

These LuaCATS definitions describe the subset of Mudlet 4.22 and Geyser APIs
used by LuminariGUI. They are loaded by Lua Language Server for static
diagnostics only; Mudlet provides the real implementations at runtime.

Keep this directory versioned with the supported Mudlet release. Add or refine
definitions when production code starts using another Mudlet/Geyser surface,
and verify the signature against the Mudlet API documentation before relying
on it for a blocking diagnostic.
