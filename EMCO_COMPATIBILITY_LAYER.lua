-- EMCO Compatibility Layer for LuminariGUI
-- This module provides a compatibility layer that maintains YATCO's API while using EMCO internally
-- This allows all existing triggers, aliases, and scripts to work without modification

local EMCO_COMPAT = {}

-- Store the actual EMCO instance
local emcoInstance = nil

-- Create the compatibility wrapper
function EMCO_COMPAT.createWrapper(emco)
  emcoInstance = emco
  
  -- Create the main wrapper object
  local wrapper = {
    -- Store references that scripts might access
    use = true,
    useContainer = false,
    currentTab = emco.currentTab,
    error = nil,
    
    -- Sound support properties
    lastSoundTime = 0,
  }
  
  -- Method: append - Core functionality for chat triggers
  function wrapper:append(tabName)
    if not emcoInstance then
      error("EMCO not initialized")
    end
    
    -- Get current line for custom processing
    selectCurrentLine()
    local line = getLine()
    
    -- Call EMCO's append
    emcoInstance:append(tabName)
    
    -- Handle gagging if enabled (preserves YATCO behavior)
    if self.config.gag then
      deleteLine()
      tempLineTrigger(1, 1, [[if isPrompt() then deleteLine() end]])
    end
    
    -- Handle sound notifications
    if self.config.soundEnabled and tabName ~= self.currentTab then
      local currentTime = os.time()
      if currentTime - self.lastSoundTime >= self.config.soundCooldown then
        self.lastSoundTime = currentTime
        local soundPath = getMudletHomeDir() .. "/LuminariGUI/" .. self.config.soundFile
        if io.exists(soundPath) then
          playSoundFile(soundPath, self.config.soundVolume)
        end
      end
    end
    
    -- Handle blinking
    if self.config.blink and tabName ~= self.currentTab then
      if not ((self.config.Alltab == self.currentTab) and not self.config.blinkFromAll) then
        self.tabsToBlink[tabName] = true
      end
    end
  end
  
  -- Method: create - Initialize the chat system
  function wrapper:create()
    -- EMCO is already created, just ensure it's visible
    if emcoInstance then
      emcoInstance:show()
      return true
    end
    return false
  end
  
  -- Method: resetUI - Reset the UI
  function wrapper:resetUI()
    if emcoInstance then
      emcoInstance:reset()
    end
  end
  
  -- Method: showAllTabs - Show all tabs
  function wrapper:showAllTabs()
    if emcoInstance then
      for _, tabName in ipairs(emcoInstance.consoles) do
        emcoInstance:showTab(tabName)
      end
    end
  end
  
  -- Method: blink - Start/restart blink timer
  function wrapper:blink()
    -- EMCO handles blinking internally, but we need to maintain compatibility
    if emcoInstance and emcoInstance.blink then
      -- Trigger EMCO's blink functionality if needed
      return true
    end
  end
  
  -- Create config metatable that maps to EMCO properties
  wrapper.config = setmetatable({}, {
    __index = function(t, k)
      if not emcoInstance then return nil end
      
      -- Map YATCO config names to EMCO properties
      local mapping = {
        timestamp = "timestamp",
        timestampFormat = "timestampFormat",
        timestampCustomColor = "timestampCustomColor",
        timestampFG = "timestampFG",
        timestampBG = "timestampBG",
        channels = "consoles",
        Alltab = "allTabName",
        blink = "blink",
        blinkTime = "blinkTime",
        blinkFromAll = "blinkFromAll",
        fontSize = "fontSize",
        preserveBackground = "preserveBackground",
        gag = "gag",
        lines = "height",
        width = "wrapAt",
        activeColors = {r = 0, g = 180, b = 0},
        inactiveColors = {r = 60, g = 60, b = 60},
        windowColors = {r = 0, g = 0, b = 0},
        activeTabText = "activeTabFGColor",
        inactiveTabText = "inactiveTabFGColor",
        -- Sound settings (not in EMCO, stored in wrapper)
        soundEnabled = false,
        soundFile = "audio/chat_sound.mp3",
        soundVolume = 100,
        soundCooldown = 0,
      }
      
      local mapped = mapping[k]
      if type(mapped) == "string" then
        return emcoInstance[mapped]
      elseif type(mapped) == "table" then
        return mapped
      else
        -- Store custom config in wrapper
        return rawget(t, k)
      end
    end,
    
    __newindex = function(t, k, v)
      if not emcoInstance then return end
      
      -- Map YATCO config names to EMCO properties
      local mapping = {
        timestamp = "timestamp",
        timestampFormat = "timestampFormat",
        channels = "consoles",
        Alltab = "allTabName",
        blink = "blink",
        blinkTime = "blinkTime",
        fontSize = "fontSize",
        preserveBackground = "preserveBackground",
        gag = "gag",
      }
      
      local mapped = mapping[k]
      if mapped then
        emcoInstance[mapped] = v
      else
        -- Store custom config in wrapper
        rawset(t, k, v)
      end
    end
  })
  
  -- Create windows accessor that maps to EMCO's mc (MiniConsole)
  wrapper.windows = setmetatable({}, {
    __index = function(t, k)
      if emcoInstance and emcoInstance.mc then
        return emcoInstance.mc[k]
      end
    end,
    __newindex = function(t, k, v)
      if emcoInstance and emcoInstance.mc then
        emcoInstance.mc[k] = v
      end
    end
  })
  
  -- Create tabs accessor
  wrapper.tabs = setmetatable({}, {
    __index = function(t, k)
      if emcoInstance and emcoInstance.tabs then
        return emcoInstance.tabs[k]
      end
    end,
    __newindex = function(t, k, v)
      if emcoInstance and emcoInstance.tabs then
        emcoInstance.tabs[k] = v
      end
    end
  })
  
  -- Create tabsToBlink accessor
  wrapper.tabsToBlink = setmetatable({}, {
    __index = function(t, k)
      if emcoInstance and emcoInstance.tabsToBlink then
        return emcoInstance.tabsToBlink[k]
      end
    end,
    __newindex = function(t, k, v)
      if emcoInstance and emcoInstance.tabsToBlink then
        emcoInstance.tabsToBlink[k] = v
      end
    end
  })
  
  -- Create container accessor
  setmetatable(wrapper, {
    __index = function(t, k)
      if k == "container" and emcoInstance then
        return emcoInstance
      end
      return rawget(t, k)
    end,
    __newindex = function(t, k, v)
      if k == "currentTab" and emcoInstance then
        -- Update both wrapper and EMCO
        rawset(t, k, v)
        emcoInstance.currentTab = v
      else
        rawset(t, k, v)
      end
    end
  })
  
  return wrapper
end

-- Helper function to sync wrapper state with EMCO
function EMCO_COMPAT.syncState(wrapper)
  if emcoInstance then
    wrapper.currentTab = emcoInstance.currentTab
  end
end

-- Store original demonnicChatSwitch function for compatibility
local originalChatSwitch = nil

-- Create replacement for demonnicChatSwitch that works with EMCO
function EMCO_COMPAT.createChatSwitch()
  return function(chat)
    if emcoInstance then
      emcoInstance:switchTab(chat)
      -- Update wrapper's currentTab
      if demonnic and demonnic.chat then
        demonnic.chat.currentTab = chat
      end
    elseif originalChatSwitch then
      -- Fallback to original if EMCO not ready
      originalChatSwitch(chat)
    end
  end
end

-- Initialize the compatibility layer
function EMCO_COMPAT.initialize(emco)
  -- Store EMCO instance
  emcoInstance = emco
  
  -- Create wrapper
  local wrapper = EMCO_COMPAT.createWrapper(emco)
  
  -- Store original functions if they exist
  if demonnicChatSwitch then
    originalChatSwitch = demonnicChatSwitch
  end
  
  -- Replace global functions
  demonnicChatSwitch = EMCO_COMPAT.createChatSwitch()
  
  return wrapper
end

return EMCO_COMPAT