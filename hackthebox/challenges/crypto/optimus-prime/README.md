> Optimus Prime has returned to Earth,
> choose an historical character and overcome this threat.

> Author: **[Xh4H][author-profile]**

## The challenge

The server responds with:

```
Give them personalities worthy of him who created me. Let them think for themselves, to grow in knowledge and wisdom. And let them always value freedom and life wherever they find it.
1. View status of the Transformer.
2. View Serial ID's of the Transformer.
3. Register new Transformer.
4. Enter to the access panel.
Enter the option: 4
PUBLIC KEY: 330050996892843073677145850811385100644710910441287539887633089371171185510476480500510056741059194785063582154089631785442050012717748248957909932011684810968465036042448919893050832641951464075204509242424607091166282776334907830526566354188722572983184440736664945398937312667767339303753982200039423965246958988899498638381484314075364834513625474099507361747324898475038734596086780856115902656787155777457486216109622398505593385092141553663708381965905507113650381591723624968854293208718671989497923278577727202180125655073928452406306809787836089550797241805439570694132399623752282039787473959501085994485638344096459026016943682062636931450256222453903238328607085301849287669095321023040412964027428479793520520444886893759949841052125606689812709856288578228666819740549600278140030330487766999856495809601577086363669338391566944133919105610412573495608902255446729328472355268765139169660990480631747841437125029613610231219004062943988835015273586430245338950782661514264035639520225619300663907758522058261649277649714233514971951122033495531513348881396892706983799736390756142799111075801558773848729953361893487382295691481619627681361209728560568201915845940812280295457402130052761013620658434678850222535815583
ENCRYPTED PASSWORD: 318433730329429019172365548533206978442787880178028307978406547944071072664345822262617192440037939538293713740491635278828252377326250567756710112440636776815130695795694883010113221285221826554626535454228739274163021710535009763615977848966791951843152802803201758740312007442518437518093198188510585675935581054387748929412429803172320582456944619329915646547951586232187990058211847570818278515630105120031319102730810149523921111827996121057640857831452193779141101224264925655762895626439779667715109202891622089625389971786103057282090295892413534846178849751325675870704113384436349944676691966360530861809289783216594388277220718430442641198082486956767376424177041302250404618978016654443157486245360556093877771891566376802899944177300405177231690161427977995602068480761808049530989369231275179912246263530742755253805960457634885290096620839784733133827678036330062831623139994450188644763273331619439113474900035868097457230695363234399255171591448051468072448821765631004700251781709213340815033674062095252002318903152954398125892545426231960399753721064113070902951734991800157441316081906378189642421906637712966940496688375560910837925090752754004414967656434346957036118272472041421976872073898652705626966083749
The private key has been sent to your email. Please use it to proceed:
```

It looks like RSA. The "public key" is too big to be an exponent, so it's probably the modulus.

The values change each time:

```
PUBLIC KEY: 579253867308028871949892911793560301538601253852330693038284777142952086832101349425550060158967895749168947665129450154793791226788413121368326978634727655496426589492439613209223918550686631908006151922358053618352758841537951118679550321877903403005307774939766371707209486656568613965399754069025394083482293314592666051865129413011949345261520434367573167481403219187652374201226992076552774215482741885787868407931268655037624190038534293281654840585111321208851716644821847294279799200535642608308501220505386599132969120738612636550168035199222002960421856786078199931412707898370672514304376860868072805112179516394559692655967990892226820896252431009920062880738079021068455200701727909105343771511718911744621378245766937702937284744104715228365537640308058760431930140817098238372787429147762098206292643539161276880869502081742328061636745954327356115018307020182808317828029942723879425905612369408685519581357936768947674665282861101060987896390847293525595443932201028627028676361436010951748096596157890653917747136553315633006501385538103385365749440369777608035767848482294303009576120599835985570100387192550933644928059690330765536078568252714325553014774259370874614371312646261629831518872454354668036511933963
ENCRYPTED PASSWORD: 30370354102642445531440684207214438541589956391304270532346953922583815512279577762174277372705532746824505679587710550611914960183251698039728947535039939640251670121550920790738453155808232068757309917050484869659344030465825759376803187465593773579951077042845169363079417133265749294337913270239985059352565320660754418548677107606193153618733931439887575163445366504059546814613212958124830215400543840310791108331722968903140575215561071910081054259723182831789310476281477111692317523214868642979877345392130862289687570204296055765148752701099897444245344068714688628933401478930785553950811172939100106698479515520455720999089870289823371505549823698542905413167835094884359437226189470749937963240483959103171801140228921443672590125031532132505233966650108751151469411307444246250965635398682961066473698266875705195028910141806421165776080369895969134235682955369551119855676024531577220038835732733483688175812789387295616206214114198552180515221055315486183761194801077719785243167367512010170847770632152528892312736190801875323475673323856307455924826116375208458470807420596076769149633816985927872722576264466043477277715827684374073830373152912471985774853976210341639529451111304860907219089671818928672960587407
```

## Factoring the modulus

The moduli are not coprime: the [extended Euclidean algorithm][wiki-egcd] can be used to factor them.

```python
p, _, _ = extended_euclid_gcd(M1, M2)
q = M1 // p
```

The most common values for the public exponent are 3 and 65537. The latter is used in our case:

```python
phi = (q - 1) * (p - 1)
d = pow(0x10001, -1, phi)
```

## Decoding the password

```python
password = pow(C2, d, M2)
print(bytes.fromhex(hex(password)[2:]))
```

> `HTB{3uc1id_w4z_th3_pr1me_h4x0r}`

[author-profile]: https://app.hackthebox.com/users/21439
[wiki-egcd]: https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm