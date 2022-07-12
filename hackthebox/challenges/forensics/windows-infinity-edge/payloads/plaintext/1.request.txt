
                using System;using System.IO;using System.Diagnostics;using System.Text;
                public class SharPyShell
                {                    
                    private string GetTempDirectory()
                    {
                        string tempDirectory="";
                        string osTempDirectory = Environment.GetEnvironmentVariable("SYSTEMROOT") + "\\" + "Temp";
                        string osPublicDirectory = Environment.GetEnvironmentVariable("Public");
                        if(Directory.Exists(osTempDirectory))
                            tempDirectory=osTempDirectory;
                        else
                            if(Directory.Exists(osPublicDirectory))
                                tempDirectory=osPublicDirectory;
                            else
                                tempDirectory=@"C:\Windows\Temp";
                        return tempDirectory;
                    }
                    
                    public byte[] ExecRuntime()
                    {
                        string output_func=GetTempDirectory();
                        byte[] output_func_byte=Encoding.UTF8.GetBytes(output_func);
                        return(output_func_byte);
                    }
                }
    