import ctypes


def create_process(path):
    """Creates a process.

    Returns the handle of the created process or 0
    if the process could not be created.

    """

    word = ctypes.c_ushort
    dword = ctypes.c_ulong
    lpbyte = ctypes.POINTER(ctypes.c_ubyte)
    lptstr = ctypes.POINTER(ctypes.c_char)
    handle = ctypes.c_void_p

    class StartupInfo(ctypes.Structure):
        _fields_ = [
            ("cb", dword),
            ("lpReserved", lptstr),
            ("lpDesktop", lptstr),
            ("lpTitle", lptstr),
            ("dwX", dword),
            ("dwY", dword),
            ("dwXSize", dword),
            ("dwYSize", dword),
            ("dwXCountChars", dword),
            ("dwYCountChars", dword),
            ("dwFillAttribute",dword),
            ("dwFlags", dword),
            ("wShowWindow", word),
            ("cbReserved2", word),
            ("lpReserved2", lpbyte),
            ("hStdInput", handle),
            ("hStdOutput", handle),
            ("hStdError", handle),
        ]

    class ProcessInformation(ctypes.Structure):
        _fields_ = [
            ("hProcess", handle),
            ("hThread", handle),
            ("dwProcessId", dword),
            ("dwThreadId", dword),
        ]

    startup_info = StartupInfo()
    process_info = ProcessInformation()
    ret = ctypes.windll.kernel32.CreateProcessW(path,
                                                None,
                                                None,
                                                None,
                                                None,
                                                0x00000010,  # CREATE_NEW_CONSOLE
                                                None,
                                                None,
                                                ctypes.byref(startup_info),
                                                ctypes.byref(process_info))

    return process_info.hProcess if ret != 0 else 0


def kill_process(handle):
    """Kills a process using the given handle.
    """
    if handle != 0:
        ctypes.windll.kernel32.TerminateProcess(handle, 0)
