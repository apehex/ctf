
                using System;using System.IO;using System.Diagnostics;using System.Text;
                public class SharPyShell
                {                    
                    private string ClearDirectories(string[] modulesPath, string envDirectory)
                    {
                        string output="";
                        for(int i = 0 ; i < modulesPath.Length ; i++)
                        {
                            try{
                                if(File.Exists(modulesPath[i])){
                                    File.Delete(modulesPath[i]);
                                    output += "File Removed-->" + modulesPath[i] + "\n";
                                }
                                else
                                    output += "File Not Found-->" + modulesPath[i] + "\n";
                            }
                            catch{
                                output += "File Not Removed-->" + modulesPath[i] + "\n";
                            }
                        }
                        try{
                            if(Directory.Exists(envDirectory)){
                                Directory.Delete(envDirectory);
                                output += "Directory Removed-->" + envDirectory + "\n";
                            }
                            else
                                output += "Directory Not Found-->" + envDirectory + "\n";
                        }
                        catch{
                            output += "Directory Not Removed-->" + envDirectory + "\n";
                        }
                        return output;
                    }

                    public byte[] ExecRuntime()
                    {
                        string[] modulesPath = {@"C:\Windows\Temp\x1fvogijp5pyzn7\tbyjzt4vw6y"};
                        string envDirectory = @"C:\Windows\Temp\x1fvogijp5pyzn7";
                        string output_func=ClearDirectories(modulesPath, envDirectory);
                        byte[] output_func_byte=Encoding.UTF8.GetBytes(output_func);
                        return(output_func_byte);
                    }
                }
    