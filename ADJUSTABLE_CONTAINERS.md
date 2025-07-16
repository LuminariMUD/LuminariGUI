# ADJUSTABLE_CONTAINERS.md

Source: https://wiki.mudlet.org/w/Manual:Geyser#Adjustable.Container

## Adjustable Container

**Mudlet Version:** Available in Mudlet 4.8+ 

Adjustable Container is a Geyser element which acts as a container for other Geyser elements, but with more flexibility and user-configurable features than User Windows. They are referred to as "adjustable" because they can be minimized, loaded, saved, moved, adjusted in size with the mouse pointer, and attached to borders .

A brief [video of Introduction to Adjustable Containers](https://youtu.be/GT2ScizuM48) is available.

## Creating an Adjustable Container

An Adjustable Container is created just like any other Geyser Object. For example, we might experiment with creating a new Adjustable Container by running the following line of lua code :

```lua
testCon = testCon or Adjustable.Container:new({name="testContainer"})
```

This will create a new Adjustable Container with the name `testContainer`. Specifying the adjustable container's name is important for saving. Assigning it to a variable, such as `testCon` in our above example, allows functions to be used with the Adjustable Container .

Our newly created Adjustable Container may be used the same way as any other Geyser Container might. For example, let's change the default border to a green, double line border with red buttons using a stylesheet and add a Geyser.Label in our new testContainer :

```lua
-- apply some stylesheets to the container
testCon = testCon or Adjustable.Container:new ({
    name="testContainer",
    adjLabelstyle = [[background-color: rgba(0,0,0,100%); 
      border: 4px double green;
      border-radius: 4px;]],
    buttonstyle = [[
    QLabel{ border-radius: 7px; background-color: rgba(255,30,30,100%);}
    QLabel::hover{ background-color: rgba(255,0,0,50%);}
    ]],
    titleTxtColor = "green"
})
-- add a label to the container
testLabel = Geyser.Label:new({name="myTestLabel", x=0, y=0, height="100%", width="100%", color="green"},testCon)
```

You can also create one for miniconsole :

```lua
miniconsoleContainer = miniconsoleContainer or Adjustable.Container:new({name="miniconsoleContainer"})
myMiniconsole = Geyser.MiniConsole:new({
  name="myMiniconsole",
  x=0, y=0,
  autoWrap = true,
  color = "black",
  scrollBar = false,
  fontSize = 8,
  width="100%", height="100%",
}, miniconsoleContainer)

myMiniconsole:echo("Hello!\n")
```

## Key Functions

A listing of key functions for the Adjustable Container module can be found here: https://www.mudlet.org/geyser/files/geyser/Adjustable.Container.html 

To make the Adjustable Container show on screen use the following :

```lua
testCon:show() --will cause the Adjustable Container to show if not showing
```

## Valid Constraints

Adjustable Container constraints and their default values can be found at .

These are in addition to the standard Geyser.Container constraints.

## Change Title Text

To specify the title text of a new container, use the constraint `titleText` in the constructor (see valid constraints) .

To change the title text after a container has already been created, use `setTitle`. Continuing from the previous example, the title for an existing container named "testCon" might be adjusted in a number of ways :

```lua
testCon:setTitle("Title") -- changes the container's title to "Title"
```

A container's title text defaults to the color green, but this can also be adjusted by using setTitle :

```lua
testCon:setTitle("Red Title Test","red") -- changes the container's title text to "Red Title Test" and displays the text in the specified color "red".
```

To restore a container's default title text, setTitle is issued without any specified title or color :

```lua
testCon:setTitle() -- resets the container's title text
```

## AutoSave and AutoLoad

The following Adjustable Container settings can be saved and loaded :

- x, y, height, width, minimized, locked, lock Style, padding, and hidden.

These settings will be automatically saved when the Mudlet profile is closed, and automatically loaded when a previous Adjustable Container is created within the corresponding profile .

To prevent automatic saving and/or loading of these settings, the `autoLoad` and `autoSave` constraints can be included in the constructor. For example, the following code will prevent the settings of the testCon2 Adjustable Container from being loaded upon creation :

```lua
testCon2 = testCon2 or Adjustable.Container:new({name="testCon2", autoLoad=false})
```

To also prevent the testCon2 Adjustable Container from automatically saving its settings when the Mudlet profile is closed, the `autoSave=false` constraint would be added at creation as follows :

```lua
testCont2 = testCont2 or Adjustable.Container:new({name="testCont2", autoLoad=false, autoSave=false})
```

Automatic saving can also be deactivated after an Adjustable Container has been created, by invoking `testCont:disableAutoSave()` 

**Note:** Even with autoSave and autoLoad disabled, it is still possible to save and load manually through the right-click menu and/or by using `testCont:save()` or `testCont:load()` in a script .

To save/load all your containers manually at the same time, we use `Adjustable.Container:saveAll()` and/or `Adjustable.Container:loadAll()` 

## "All" Functions

The following functions affect all Adjustable Containers at the same time .

**Note:** You must create the Adjustable Containers before these functions will have an effect .

- `Adjustable.Container.loadAll()` loads all the settings from your Adjustable Containers at once .
- `Adjustable.Container.saveAll()` saves all your Adjustable Containers at once .
- `Adjustable.Container:showAll()` shows all your Adjustable Containers at once .
- `Adjustable.Container:doAll(myfunc)` creates a function that will affect all your Adjustable Containers .

For example:

```lua
Adjustable.Container:doAll(function(self) self:hide() end) -- hides all your adjustable containers
```

## Custom Save/Load Directories and Slots

**Mudlet Version:** Available in Mudlet 4.10+ 

### Custom Directory

If no option set your Adjustable Container saves/loads its settings in your profile directory .

It is possible to change the default save/load directory by using for example a different `defaultDir` as constraint when creating your Adjustable Container .

**Note:** This can be especially useful for authors of packages which want to ship their own save files .

Example:

```lua
testCon2 = testCon2 or Adjustable.Container:new({name="testCon2", defaultDir = "/home/edru/MyAdjustableContainerSettings/"}) 
-- note: the directory will be created if it doesn't exist
```

Example for save files in a package (assuming the packagename is "AdjustableContainerTest" and the settings are saved in "myPersonalAdjSettings") :

```lua
local packageName = "AdjustableContainerTest"
testCon2 = testCon2 or Adjustable.Container:new({name="testCon2", defaultDir = string.format("%s/%s/myPersonalAdjSettings/", getMudletHomeDir(), packageName)})
```

### Custom Slot

Another useful addition is to choose a save slot depending on the situation or to reset to a default save state .

To save to a different slot just add it as parameter when saving :

```lua
testCon2:save("combatSlot")
```

To then load from that slot just use :

```lua
testCon2:load("combatSlot")
```

**Note:** This also allows package/module authors to choose a "default" save setting to reset to .

Example:

```lua
Adjustable.Container:saveAll("default") -- saves the default settings

-- to reset to default settings then just use
Adjustable.Container:loadAll("default") -- loads the default settings
```

This can also be used to change the whole GUI on the fly :

```lua
-- in combat situation use combat settings
Adjustable.Container:loadAll("combat") -- loads special combat settings
-- combat is over 
Adjustable.Container:loadAll("default") --reverts to the default settings
```

### Delete Save File

To delete the save file just use :

```lua
testCont2:deleteSaveFile()
```

## Right-Click Menu

Your Adjustable Container also has an integrated right-click menu with the primary key functions for greater usability .

The right-click menu automatically shows you the possible positions to attach to (top, right, bottom, or left) when it's near one of them. For example, to attach a window to the right of the screen, drag it over to the right - and then the 'Attach to - right' will appear as an option .

It also shows the lockstyle selection, which allows you to choose what happens when you press Lock, with 4 lockstyles available by default :

- **standard**: this is the default lockstyle, with a small margin on top to keep the right click menu usable.
- **light**: only hides the min/restore and close labels. Borders and margin are not affected.
- **full**: the container gets fully locked without any margin left for the right click menu.
- **border**: keeps the borders of the container visible while locked.

From Mudlet 4.10+ on it is also possible to change your right-click menu style to dark mode by :

```lua
myAdjustableContainer:changeMenuStyle("dark") -- possible menu styles are "dark" or "light"
```

## Create a Custom Menu with Custom Items

To create a new menu element in your right click menu called "Custom" and add an item to it use :

```lua
testcontainer:newCustomItem(name, func)
-- for example
testcontainer:newCustomItem("Hello world", function(self) echo("Hello world\n") self:flash() end)
-- this will write "Hello world" to the main console and flashes your container.
```

## Add New LockStyles

For more advanced users, it's possible to add a new Lockstyles by :

```lua
testcontainer:newLockStyle(name, func)
-- for example
testcontainer:newLockStyle("NewLockStyle", function(self) self.Inside:move(40, 40) self.Inside:resize(-40,-40) self:setTitle("") end)
```

## Change Adjustable Container Style

In addition to the standard container constraints, Adjustable Containers allow you to change styles at creation: the internal Label style, the menu style, min/close buttons, the menu text, title text... 

An example of a Adjustable Container with different style:

```lua
testCont =
  testCont or
  Adjustable.Container:new(
    {
      name = "TestNewStyleContainer",
      adjLabelstyle = "background-color:rgba(220,220,220,100%); border: 5px groove grey;",
      buttonstyle=[[
      QLabel{ border-radius: 7px; background-color: rgba(140,140,140,100%);}
      QLabel::hover{ background-color: rgba(160,160,160,50%);}
      ]],
      buttonFontSize = 10,
      buttonsize = 20,
      titleText = "My new Style",
      titleTxtColor = "black",
      padding = 15,
    }
  )
```

## Attach your Adjustable Container to a Border

The simplest way to attach your container to a border is to move your container near the border you want it to attach and use the right click menu Attach to .

There is also the function `TestCont:attachToBorder("right")` -- attach TestCont to the right border 

To change the margin between container and border use the constraint `attachedMargin` or the function `TestCont:setBorderMargin(10)` -- 10 is the margin in px 

**Note:** The border is set in percentages and adjusts with screen-size 

## Create a moveable border frame

**Mudlet Version:** Available in Mudlet 4.10+ 

Adjustable Container can be connected to a border and therefore act like a frame .

This only works if your container is attached to a specific border and the border to connect to has also at least one container attached to it. Use the function connectToBorder :

```lua
TestCont:connectToBorder("left") -- possible borders are "top", "bottom", "right", "left"
```

Minimizing automatically disconnects from a border. Another way is to use the function disconnect .

**Note:** Connected containers are still resizable even if locked .

If you like to do everything with your right click menu there is the function :

```lua
TestCont:addConnectMenu()
```

If you want to add the connect menu items to all Adjustable Containers just :

```lua
Adjustable.Container:doAll(function(self) self:addConnectMenu() end)
```

There is also a brief video of how to connect your Adjustable Container available.

Example:

```lua
GUI = GUI or {}

GUI.top = Adjustable.Container:new({name = "top", y="0%", height = "10%", autoLoad = false})
GUI.bottom = Adjustable.Container:new({name = "bottom", height = "20%", y = "-20%", autoLoad = false})
GUI.right = Adjustable.Container:new({name = "right", y = "0%", height = "100%", x = "-20%", width = "20%", autoLoad = false})
GUI.left = Adjustable.Container:new({name = "left", x = "0%", y = "0%", height = "100%", width = "20%", autoLoad = false})

GUI.top:attachToBorder("top")
GUI.bottom:attachToBorder("bottom")
GUI.left:attachToBorder("left")
GUI.right:attachToBorder("right")

GUI.top:connectToBorder("left")
GUI.top:connectToBorder("right")
GUI.bottom:connectToBorder("left")
GUI.bottom:connectToBorder("right")
```

## Add a scrollable box

**Mudlet Version:** Available in Mudlet 4.15+ 

To add a scrollable box to an adjustable label, try the following :

```lua
ScrollContainer = ScrollContainer or Adjustable.Container:new({name = "ScrollContainer"})
ContainerBox = ContainerBox or Geyser.ScrollBox:new({name = "ContainerBox", x = 0, y = 0, height = "100%", width = "100%"}, ScrollContainer)
```

## Change Container

**Mudlet Version:** Available in Mudlet 4.8+ 

With this command it is possible to change an element's or even a container's location to that from another container. For example :

```lua
mycontainerone:changeContainer(mycontainertwo)
--puts container one into container two which means container two will be the parent of container one
```

It is also possible to change to a container which is not located on the main window :

```lua
myEmco:changeContainer(emco_userwindow)
--puts my tabbed chat Emco into my userwindow
--to put it back to the main window change to a container located on the main window
myEmco:changeContainer(mymainwindow_container)
--or if it the element wasn't in a container use the main Geyser Root container called Geyser
myEmco:changeContainer(Geyser)
```

## Geyser.Mapper

**Mudlet Version:** Available in Mudlet 4.8+ 

It's possible to create the mapper as a map window (similar to clicking the icon) like this :

```lua
myMapWidget = Geyser.Mapper:new({embedded= false})
```

This will open a map window with your saved layout (if there is one, otherwise it will dock at the right corner) 

To choose the position of the DockWindow at creation use: (this will create a map window docked at the left corner) 

```lua
myMapWidget = Geyser.Mapper:new({embedded= false, dockPosition="left"})
```

Possible dockPositions are "left", "right", "top", "bottom", and "floating" .

To change the dockPosition after creation use :

```lua
myMapWidget:setDockPosition("floating")
-- this will change myMapWidget dockPosition to floating
```