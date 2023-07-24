function Component()
{
    // default constructor
}

Component.prototype.createOperations = function()
{
    // This actually installs the files
    component.createOperations();

    if (systemInfo.productType == "windows") {
        // Start menu shortcut
        component.addOperation("CreateShortcut", 
                               "@TargetDir@/iBridges.exe", 
                               "@StartMenuDir@/iBridges.lnk", 
                               "workingDirectory=@TargetDir@", 
                               "iconPath=@TargetDir@/icons/iBridges.ico");

       // Desktop Shortcut
       component.addOperation("CreateShortcut", 
                              "@TargetDir@/iBridges.exe",
                              "@DesktopDir@/iBridges.lnk",
                              "workingDirectory=@TargetDir@", 
                              "iconPath=@TargetDir@/icons/iBridges.ico");
    }
}