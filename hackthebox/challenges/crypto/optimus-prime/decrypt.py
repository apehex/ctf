#!/usr/bin/env python

import math

####################################################################### kwnowns

M1 = 330050996892843073677145850811385100644710910441287539887633089371171185510476480500510056741059194785063582154089631785442050012717748248957909932011684810968465036042448919893050832641951464075204509242424607091166282776334907830526566354188722572983184440736664945398937312667767339303753982200039423965246958988899498638381484314075364834513625474099507361747324898475038734596086780856115902656787155777457486216109622398505593385092141553663708381965905507113650381591723624968854293208718671989497923278577727202180125655073928452406306809787836089550797241805439570694132399623752282039787473959501085994485638344096459026016943682062636931450256222453903238328607085301849287669095321023040412964027428479793520520444886893759949841052125606689812709856288578228666819740549600278140030330487766999856495809601577086363669338391566944133919105610412573495608902255446729328472355268765139169660990480631747841437125029613610231219004062943988835015273586430245338950782661514264035639520225619300663907758522058261649277649714233514971951122033495531513348881396892706983799736390756142799111075801558773848729953361893487382295691481619627681361209728560568201915845940812280295457402130052761013620658434678850222535815583
M2 = 564737874123821384153353610322715858009295555169250376083334778186280985804252191139881666280939866063292143315658572378484937936583709872363631282484993044442234207190655522219040000215496159717815850760774837374204936355088766172666835551834618355309660363806422454857339465548230463247914327645025731186951279153879772272139342864166603271068690252069581314253485935429412105747138593842987805418038307710848862668928791121519608459460944322619967409002331561160908813173656637010638357823343757875234391803496262773310703730465245032460056766349180617119023910586510896129514838872100757148897576871781938105302544001564433178631923180146892751717303803638987149532811038395041398469879732568060597044293373664397347673079632605649678368443965513420278107864368240624511989910356855609616430467488440501124904060516647905856384308970082083942097557578161294664947370470293876825855722915464941851404931833340687091449499280936315818543199423001139348321348637022600195653362143747712828617192332848437278622751354393035364359404455954197210334414385364512547141968570379726621295100937577115349185906338400380913050748654999854172202350581108809635603941229192942116479924665021414765018140462159632674047441377890498431342282413

C1 = 318433730329429019172365548533206978442787880178028307978406547944071072664345822262617192440037939538293713740491635278828252377326250567756710112440636776815130695795694883010113221285221826554626535454228739274163021710535009763615977848966791951843152802803201758740312007442518437518093198188510585675935581054387748929412429803172320582456944619329915646547951586232187990058211847570818278515630105120031319102730810149523921111827996121057640857831452193779141101224264925655762895626439779667715109202891622089625389971786103057282090295892413534846178849751325675870704113384436349944676691966360530861809289783216594388277220718430442641198082486956767376424177041302250404618978016654443157486245360556093877771891566376802899944177300405177231690161427977995602068480761808049530989369231275179912246263530742755253805960457634885290096620839784733133827678036330062831623139994450188644763273331619439113474900035868097457230695363234399255171591448051468072448821765631004700251781709213340815033674062095252002318903152954398125892545426231960399753721064113070902951734991800157441316081906378189642421906637712966940496688375560910837925090752754004414967656434346957036118272472041421976872073898652705626966083749
C2 = 180841452004045272347323180272513657300796809114756094554182853864349649113827089376061829735684587804163562420699714508105800971548830514469081436388033559283434736018912652785555045755677137595283406062467029854226886939421209842464416772312669933078316485749581612180505236242849358728512138867462389722658371796410372148341558834013031089910778253501819879548050454792888775386105234832983440406047801510774260741533137728994999225057479275962218535281912008432068180617940407896974722339438172700230563533971466676890599403287627473326405003740089698797250404950951350944970362870079052236013759279450962425289430347601891422729366969819923374800548729469441289163802941696499626254632321532705851331686841903547767000211518501436131192321621693751126463272498286125886445461314492000727530687651127449639136700890864057330521806216282043039538239878107440387223562498534520032820164100950927928404835433910271760949447709983032907858886919631230694485659686020013647501583847013657802372633080190178810768264551351372957063086884401193325298264985458053933650318100676623241139620396683314841171200882632136586273140274421560416159553391536874118613259936677182209495314784280970420365746499914592994496803006675852773254549885

E = 0x10001

########################################################### Euclidean algorithm

def extended_euclid_gcd(a, b):
    """
    Returns a list `result` of size 3 where:
    Referring to the equation ax + by = gcd(a, b)
        result[0] is gcd(a, b)
        result[1] is x
        result[2] is y
    """
    s = 0; old_s = 1
    t = 1; old_t = 0
    r = b; old_r = a

    while r != 0:
        quotient = old_r//r
        old_r, r = r, old_r - quotient*r
        old_s, s = s, old_s - quotient*s
        old_t, t = t, old_t - quotient*t
    return [old_r, old_s, old_t]

######################################################### factoring the modulus

p, _, _ = extended_euclid_gcd(M1, M2)

q = M2 // p

################################################ computing the private exponent

phi = (p - 1) * (q - 1)

d = pow(E, -1, phi)

###################################################################### decoding

password = pow(C2, d, M2)

print(bytes.fromhex(hex(password)[2:]))