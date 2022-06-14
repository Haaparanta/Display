from ctypes import windll, byref, Structure, WinError, POINTER, WINFUNCTYPE
from ctypes.wintypes import BOOL, HMONITOR, HDC, RECT, LPARAM, DWORD, BYTE, WCHAR, HANDLE


_MONITORENUMPROC = WINFUNCTYPE(BOOL, HMONITOR, HDC, POINTER(RECT), LPARAM)


class _PHYSICAL_MONITOR(Structure):
    _fields_ = [('handle', HANDLE),
                ('description', WCHAR * 128)]


def _iter_physical_monitors(close_handles=True):
    def callback(hmonitor, hdc, lprect, lparam):
        monitors.append(HMONITOR(hmonitor))
        return True

    monitors = []
    if not windll.user32.EnumDisplayMonitors(None, None, _MONITORENUMPROC(callback), None):
        raise WinError('EnumDisplayMonitors failed')

    for monitor in monitors:
        # Get physical monitor count
        count = DWORD()
        print(len(monitors))
        if not windll.dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR(monitor, byref(count)):
            raise WinError() 
        # Get physical monitor handles
        physical_array = (_PHYSICAL_MONITOR * count.value)()
        if not windll.dxva2.GetPhysicalMonitorsFromHMONITOR(monitor, count.value, physical_array):
            print('error')
            raise WinError()
        for physical in physical_array:
            yield physical.handle
            if close_handles:
                if not windll.dxva2.DestroyPhysicalMonitor(physical.handle):
                    raise WinError()


def set_vcp_feature(monitor, code, value):
    if not windll.dxva2.SetVCPFeature(HANDLE(monitor), BYTE(code), DWORD(value)):
        raise WinError()
    
# Turns out the vcp code for input commands is 0x60, and from there the values can be determined quite easily, they are as followed:

# 0x01: D-sub/VGA, 0x03: DVI, 0x11 or 0x04 depending on the brand: HDMI, 0x0F: DisplayPort

# Switch to HDMI, wait for the user to press return and then back to DP
for handle in _iter_physical_monitors(): #päänäyttö 1
    set_vcp_feature(handle, 0x60, 0x11) #Change input to HDMI
    input("Press Enter to continue...")   
    set_vcp_feature(handle, 0x60, 0x0F) #Change input to DisplayPort
    # 0xA0 0x6e
    
    