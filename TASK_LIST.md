# TASK_LIST.md - LuminariGUI Task Lists

## Missing Changes to Re-implement

### 1. Scrollbar Visibility Fix
- In `GUI.styleScrollbar()` function:
  - Change handle color from `#202020` to `#d0d0d0`
  - Change border color from `#515151` to `#a0a0a0`
  - Change arrow color from white to `#404040`

### 2. Button System Legend/Room Fix
- In Buttons script:
  - Keep button array as `{"Legend", "Mudlet", "ASCII"}`
  - Update button text display to show "Legend/Room" in three places:
    1. Initial button creation
    2. Toggle state when clicked (show)
    3. Toggle state when clicked (hide)