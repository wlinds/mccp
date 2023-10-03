# mccp
MultiCamComposePro - Manage multiple cameras using Python


# Issue 1:

Serial numbers are optional on USB devices. Some models will have them, some won't. If the device has one, then your OS will recognize the device no matter which USB port you plug it into. But if it doesn’t have a serial number, your OS treats each appearance on a different USB port as if it were a new device.

If the cameras connected don't have unique ID:s, such as serial number, **config is necessary**.

It is very important that the same cameras corresponds to the same sides of the target object.