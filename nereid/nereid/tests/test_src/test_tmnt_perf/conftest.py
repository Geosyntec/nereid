import io

import pandas
import pytest

DCu_CURVES = """Detention Basin,Sand Filter,Vegetated Swale,Wet Pond,xhat,param
3.0,3.0,3.0,3.0,0.5271367641440915,Dissolved Copper
3.0,3.0,3.0,3.0,0.6584701210572295,Dissolved Copper
3.0,3.0,3.0,3.0,0.8225244942441611,Dissolved Copper
3.0,3.0,3.0,3.0,1.0274521530990048,Dissolved Copper
3.0,3.0,3.0,3.0,1.2834364621297416,Dissolved Copper
3.0,3.0,3.0,3.0,1.6031979176410207,Dissolved Copper
3.0,3.0,3.0,3.0,2.002626260799407,Dissolved Copper
3.0,3.0,3.0,3.0,2.5015700783497574,Dissolved Copper
3.124823128204064,3.0,3.124823128204064,3.124823128204064,3.124823128204064,Dissolved Copper
3.868817953297775,3.364691835932935,3.903356402871798,3.832344616821179,3.903356402871798,Dissolved Copper
4.7807400751428615,4.163434685931897,4.875857155024641,4.152514773766262,4.875857155024641,Dissolved Copper
5.907612077377537,5.16118012299393,5.877820008735089,4.552453644174688,6.090651363199595,Dissolved Copper
7.300099965324722,6.407508596769187,7.026735827139959,5.052035184158762,7.608105169737605,Dissolved Copper
9.020812268260983,7.964353265602681,8.400225987021647,5.6760848416426235,9.50362462437521,Dissolved Copper
11.14711502112809,9.909077609044367,10.042187207392834,6.455613194548013,11.871402798201045,Dissolved Copper
13.774610267797293,12.338319811356318,12.005096537180155,7.429356943456497,14.829100471379432,Dissolved Copper
17.02143448507315,15.372794952984723,14.351688520695497,8.645703834502072,18.52369298964306,Dissolved Copper
21.033570191599193,19.16329364282193,17.15696019246196,10.165097166695139,23.138773834380316,Dissolved Copper
25.991409560275322,23.8981751781992,20.51056798099039,12.063039369620755,28.903677838860595,Dissolved Copper
32.11786514491902,29.812727586346693,24.519693126504936,14.433843906749273,36.1048774058781,Dissolved Copper
"""

DZn_CURVES = """Biofiltration,Detention Basin,Sand Filter,Vegetated Swale,Wet Pond,xhat,param
5.0,5.0,5.0,5.0,5.0,0.26374786453466487,Dissolved Zinc
5.0,5.0,5.0,5.0,5.0,0.37483693841684385,Dissolved Zinc
5.0,5.0,5.0,5.0,5.0,0.5327160871979164,Dissolved Zinc
5.0,5.0,5.0,5.0,5.0,0.7570930195888766,Dissolved Zinc
5.0,5.0,5.0,5.0,5.0,1.0759762171350569,Dissolved Zinc
5.0,5.0,5.0,5.0,5.0,1.5291711716863337,Dissolved Zinc
5.0,5.0,5.0,5.0,5.0,2.173249217852408,Dissolved Zinc
5.0,5.0,5.0,5.0,5.0,3.088609208927001,Dissolved Zinc
5.0,5.0,5.0,5.0,5.0,4.389513529836012,Dissolved Zinc
6.238351220647673,6.238351220647673,5.0,6.238351220647673,6.238351220647673,6.238351220647673,Dissolved Zinc
8.86590864514552,8.86590864514552,5.0,8.86590864514552,8.86590864514552,8.86590864514552,Dissolved Zinc
12.600178047670948,12.600178047670948,5.91242977523043,12.600178047670948,12.600178047670948,12.600178047670948,Dissolved Zinc
15.83027229188148,17.808692589813408,7.670283084180392,17.21580705628273,17.130155266157406,17.907300107354423,Dissolved Zinc
17.39746779762619,24.43748230504408,9.95077232679197,21.019985387336565,21.475053504783375,25.44975125919981,Dissolved Zinc
19.119815514775766,33.533654331870295,12.909284939413615,25.664773323687886,26.92199316747694,36.169039178002066,Dissolved Zinc
21.012675498036565,46.01562300128015,16.747407354329177,31.335920440415798,33.75049640496746,51.40322912142207,Dissolved Zinc
23.092928446122844,63.143656794468036,21.72666064837665,38.26022141180438,42.31098345860233,73.05397168848359,Dissolved Zinc
25.379126245374124,86.64712402712975,28.186320004194247,46.71458575036098,53.042755275464074,103.82388170313669,Dissolved Zinc
27.8916574171769,118.8991021950213,36.56653216232752,57.037111686827366,66.49653723992432,147.5538997095515,Dissolved Zinc
30.65292894466594,163.15598078426413,47.43830603567852,69.64060704638659,83.36274090471365,209.7027481764692,Dissolved Zinc
"""

FC_CURVES = """Biofiltration,Detention Basin,Sand Filter,Vegetated Swale,Wet Pond,xhat,param
400.0,400.0,400.0,400.0,400.0,0.6580975196990224,Fecal Coliform
400.0,400.0,400.0,400.0,400.0,1.333169259913931,Fecal Coliform
400.0,400.0,400.0,400.0,400.0,2.7007247746387444,Fecal Coliform
400.0,400.0,400.0,400.0,400.0,5.471108978929194,Fecal Coliform
400.0,400.0,400.0,400.0,400.0,11.083333533430324,Fecal Coliform
400.0,400.0,400.0,400.0,400.0,22.452537993001815,Fecal Coliform
400.0,400.0,400.0,400.0,400.0,45.48419126850588,Fecal Coliform
400.0,400.0,400.0,400.0,400.0,92.14155014434671,Fecal Coliform
400.0,400.0,400.0,400.0,400.0,186.65969485714123,Fecal Coliform
400.0,400.0,400.0,400.0,400.0,378.1338780341628,Fecal Coliform
716.0019006718009,766.0209121556098,766.0209121556098,766.0209121556098,766.0209121556098,766.0209121556098,Fecal Coliform
1041.8130343780665,1551.799698324567,1551.799698324567,1551.799698324567,1551.799698324567,1551.799698324567,Fecal Coliform
1515.8820075500687,3143.624756853947,3143.624756853947,3143.624756853947,3143.624756853947,3143.624756853947,Fecal Coliform
2205.672404728367,6368.3326028318925,6368.3326028318925,5550.31818668912,6368.3326028318925,6368.3326028318925,Fecal Coliform
3209.3465934349965,12517.025933549337,11734.621419894707,9779.3864019578,12900.922749087464,12900.922749087464,Fecal Coliform
4669.734968217675,21657.18184941131,21131.655821061766,17230.795637654475,26134.59725767342,26134.59725767342,Fecal Coliform
6794.661791282339,37471.64287654954,38053.794985046865,30359.810534449643,52943.280655571885,52943.280655571885,Fecal Coliform
9886.520149886184,64834.1058236917,68527.11046527071,53492.48607379741,107252.12020444155,107252.12020444155,Fecal Coliform
14385.304769622478,112177.12796329655,123403.32601688406,94251.11738126585,206037.44385399274,217270.579871732,Fecal Coliform
20931.22657695749,194090.870510556,222224.17914070797,166065.8118480779,388159.4702735651,440145.1904896128,Fecal Coliform
"""

TCu_CURVES = """Biofiltration,Detention Basin,Hydrodynamic Separator,Sand Filter,Vegetated Swale,Wet Pond,xhat,param
2.9999370574951167,2.9999370574951167,2.9999370574951167,2.9999370574951167,2.9999370574951167,2.9999370574951167,0.20000000298023227,Total Copper
2.9999370574951167,2.9999370574951167,2.9999370574951167,2.9999370574951167,2.9999370574951167,2.9999370574951167,0.2972231707160663,Total Copper
2.9999370574951167,2.9999370574951167,2.9999370574951167,2.9999370574951167,2.9999370574951167,2.9999370574951167,0.4417080594705965,Total Copper
2.9999370574951167,2.9999370574951167,2.9999370574951167,2.9999370574951167,2.9999370574951167,2.9999370574951167,0.6564293400518979,Total Copper
2.9999370574951167,2.9999370574951167,2.9999370574951167,2.9999370574951167,2.9999370574951167,2.9999370574951167,0.9755300344698695,Total Copper
2.9999370574951167,2.9999370574951167,2.9999370574951167,2.9999370574951167,2.9999370574951167,2.9999370574951167,1.4497506282664725,Total Copper
2.9999370574951167,2.9999370574951167,2.9999370574951167,2.9999370574951167,2.9999370574951167,2.9999370574951167,2.1544973603003386,Total Copper
3.2018326359282847,3.2018326359282847,3.2018326359282847,3.2018326359282847,3.2018326359282847,3.2018326359282847,3.2018326359282847,Total Copper
4.758294169859815,4.536505022845575,4.758294169859815,4.456697384134617,4.758294169859815,4.719095823732861,4.758294169859815,Total Copper
7.071376296455818,6.1869235698890055,6.846687327663115,5.828408647362672,6.484504340390208,5.976133669005932,7.071376296455818,Total Copper
8.399847160978455,8.437778216244046,9.452852703751766,7.622314111248138,8.528852338841967,7.568011959031582,10.508884264200578,Total Copper
9.424108366716693,11.507512647000405,13.051044974376817,9.96835944865025,11.217715094226136,9.58392301515775,15.617419275751677,Total Copper
10.573266013720438,15.694042190625428,18.01887538727899,13.03648585550398,14.75428661862785,12.136817549667816,23.2092940318602,Total Copper
11.862549733799806,21.40366626886421,24.877691469130173,17.048940132648106,19.405821220817717,15.36973325025191,34.491699297188426,Total Copper
13.309046230773724,29.190499438224037,34.34728969101841,22.296373644581582,25.52382958176273,19.463809126006424,51.25866037866378,Total Copper
14.93192572825857,39.81024777481608,47.42145430104036,29.158896320294364,33.57064197932534,24.648434655650348,76.17630668690678,Total Copper
16.752696030064683,54.293549558694096,65.47224972495299,38.133610791201484,44.15434601198309,31.21410239078527,113.2068153476966,Total Copper
18.795487560228835,74.04599791381196,90.39401147072283,49.87062116486021,58.074739021869156,39.52868414055962,168.23844051460475,Total Copper
21.087373160280116,100.98455252267226,124.80214662083007,65.22012481290777,76.38376778455522,50.058042686032906,250.02180990477055,Total Copper
23.658726881969113,137.7235790660081,172.30760697252435,85.29399837530956,100.46502281771374,63.392133890577256,371.5613699036318,Total Copper
"""

TPb_CURVES = """Biofiltration,Detention Basin,Sand Filter,Vegetated Swale,Wet Pond,xhat,param
1.0,1.0,1.0,1.0,1.0,0.10334039043643814,Total Lead
1.0,1.0,1.0,1.0,1.0,0.1460789257356682,Total Lead
1.0,1.0,1.0,1.0,1.0,0.2064928577680566,Total Lead
1.0,1.0,1.0,1.0,1.0,0.29189220891708406,Total Lead
1.0,1.0,1.0,1.0,1.0,0.4126102110621028,Total Lead
1.0,1.0,1.0,1.0,1.0,0.5832536157930619,Total Lead
1.0,1.0,1.0,1.0,1.0,0.8244700960260015,Total Lead
1.1654465927602569,1.0,1.1654465927602569,1.1654465927602569,1.1654465927602569,1.1654465927602569,Total Lead
1.6474409043134732,1.0,1.3581547264007998,1.6474409043134732,1.6474409043134732,1.6474409043134732,Total Lead
2.3287738366261657,1.666535360249285,1.516343381616367,2.3287738366261657,2.1786960510222197,2.3287738366261657,Total Lead
3.2918859595843997,2.6296474832075187,1.674532036831934,2.772804139338508,2.371318521538631,3.2918859595843997,Total Lead
4.146709750633081,3.9910743530941044,1.8327206920475012,3.365024846159625,2.6436039604338397,4.653312829470985,Total Lead
4.768808831197506,5.915547192617862,1.9909093472630683,4.202170557391066,3.0284986201046076,6.577785668994743,Total Lead
5.484236668610662,8.63592519600864,2.1490980024786355,5.385535025673463,3.5725743505004948,9.298163672385522,Total Lead
6.306994660924814,12.48137124717961,2.3072866576942026,7.058304109962699,4.341663744099845,13.14360972355649,Total Lead
7.253184728625367,17.91718028328957,2.4654753129097693,9.422881114218413,5.4288258105214116,18.579418759666453,Total Lead
8.341324439911617,25.601079493904457,2.6236639681253364,12.765377374801002,6.965606019041254,26.26331797028134,Total Lead
9.592709411808034,36.46281262078057,2.7818526233409036,17.490231431954122,9.137953162344271,37.125051097157446,Total Lead
11.031830079536565,51.81663797503549,2.940041278556471,24.16914566879618,12.208718965322701,52.47887645141237,Total Lead
12.686850990603439,73.52035231373974,3.098229933772038,33.61026169978931,16.5494628679773,74.18259079011662,Total Lead
"""

TN_CURVES = """Biofiltration,Detention Basin,Hydrodynamic Separator,Sand Filter,Vegetated Swale,Wet Pond,xhat,param
1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,0.07999999821186067,Total Nitrogen
1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,0.11353778749835965,Total Nitrogen
1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,0.16113536847693954,Total Nitrogen
1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,0.228686920419109,Total Nitrogen
1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,0.3245575944319161,Total Nitrogen
1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,0.46061940014051694,Total Nitrogen
1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,0.6537213592465098,Total Nitrogen
1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,0.9277759803532725,Total Nitrogen
1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,1.7000000476837158,1.3167204307238967,Total Nitrogen
1.8687190974976062,1.8613217447434338,1.7373100243490358,1.7000000476837158,1.8656892292077931,1.7000000476837158,1.8687190974976062,Total Nitrogen
2.6521279566022997,2.361871758740382,2.0584668423175776,1.8663071957527575,2.3588215729927837,1.7000000476837158,2.6521279566022997,Total Nitrogen
3.009142417070885,2.862421772737329,2.514259784407364,2.4706966236366505,3.0586860293513274,1.8535676867803008,3.7639593385706807,Total Nitrogen
3.278313587941936,3.362971786734277,3.161131326394099,3.3284596231758545,4.051949325598632,2.057714016630924,5.341895313589467,Total Nitrogen
3.547484758812987,3.863521800731225,4.079185892824544,4.545816064956364,5.461610820347608,2.2618603464815474,7.581337356366148,Total Nitrogen
3.8166559296840377,4.364071814728173,5.38210947538814,6.273515566031391,7.4622339555078865,2.4660066763321704,10.759603612001827,Total Nitrogen
4.085827100555089,4.864621828725119,7.231247777265934,8.725505356013608,10.301563073773455,2.6701530061827934,15.270270197142708,Total Nitrogen
4.35499827142614,5.365171842722068,9.85558623059546,12.20542413033522,14.331202489687184,2.874299336033417,21.671909142976467,Total Nitrogen
4.62416944229719,5.8657218567190155,13.580106084318723,17.144202719606504,20.050156913753597,3.0784456658840393,30.757258374466026,Total Nitrogen
4.893340613168242,6.366271870715964,18.866027998536467,24.153427800901554,28.166624996576523,3.2825919957346623,43.65138929258793,Total Nitrogen
5.1625117840392925,6.866821884712912,26.367926654084155,34.10107687085192,39.68569810935743,3.486738325585286,61.9510284035886,Total Nitrogen
"""
TP_CURVES = """Biofiltration,Detention Basin,Sand Filter,Vegetated Swale,Wet Pond,xhat,param
0.10000000149011612,0.10000000149011612,0.10000000149011612,0.10000000149011612,0.10000000149011612,0.0020000000949949017,Total Phosphorus
0.10000000149011612,0.10000000149011612,0.10000000149011612,0.10000000149011612,0.10000000149011612,0.0029924923243071643,Total Phosphorus
0.10000000149011612,0.10000000149011612,0.10000000149011612,0.10000000149011612,0.10000000149011612,0.004477504942848581,Total Phosphorus
0.10000000149011612,0.10000000149011612,0.10000000149011612,0.10000000149011612,0.10000000149011612,0.006699449268554121,Total Phosphorus
0.10000000149011612,0.10000000149011612,0.10000000149011612,0.10000000149011612,0.10000000149011612,0.010024024780501102,Total Phosphorus
0.10000000149011612,0.10000000149011612,0.10000000149011612,0.10000000149011612,0.10000000149011612,0.014998407894771044,Total Phosphorus
0.10000000149011612,0.10000000149011612,0.10000000149011612,0.10000000149011612,0.10000000149011612,0.02244130918506018,Total Phosphorus
0.10000000149011612,0.10000000149011612,0.10000000149011612,0.10000000149011612,0.10000000149011612,0.03357772114699208,Total Phosphorus
0.10000000149011612,0.10000000149011612,0.10000000149011612,0.10000000149011612,0.10000000149011612,0.05024053401375281,Total Phosphorus
0.10000000149011612,0.10000000149011612,0.10000000149011612,0.10000000149011612,0.10000000149011612,0.07517220263213614,Total Phosphorus
0.11247611434663646,0.11247611434663646,0.10000000149011612,0.11247611434663646,0.10000000149011612,0.11247611434663646,Total Phosphorus
0.16829194643166379,0.16829194643166379,0.11663546266373379,0.16829194643166379,0.1252617645972593,0.16829194643166379,Total Phosphorus
0.25180616700958214,0.21649629987070457,0.13952411329473008,0.25180616700958214,0.16698338433597487,0.25180616700958214,Total Phosphorus
0.37676399309936237,0.26406712232342805,0.16241276392572643,0.3385583545977106,0.20870500407469053,0.37676399309936237,Total Phosphorus
0.44437007205140716,0.3116379447761514,0.18530141455672272,0.39328367229024164,0.2504266238134061,0.5637316519367632,Total Phosphorus
0.4835015147698993,0.35920876722887474,0.20819006518771901,0.4480089899827726,0.29214824355212166,0.8434812806316702,Total Phosphorus
0.5226329574883914,0.4067795896815983,0.23107871581871534,0.5027343076753038,0.33386986329083723,1.262055569049104,Total Phosphorus
0.5617644002068837,0.45435041213432165,0.25396736644971163,0.5574596253678348,0.3755914830295528,1.8883457119226694,Total Phosphorus
0.6008958429253758,0.501921234587045,0.2768560170807079,0.6121849430603657,0.4173131027682684,2.8254298900827504,Total Phosphorus
0.640027285643868,0.5494920570397686,0.2997446677117042,0.6669102607528968,0.45903472250698407,4.227538428673038,Total Phosphorus
"""

TSS_CURVES = """Biofiltration,Detention Basin,Hydrodynamic Separator,Sand Filter,Vegetated Swale,Wet Pond,xhat,param
5.0,5.0,5.0,5.0,5.0,5.0,0.02999999932944775,Total Suspended Solids
5.0,5.0,5.0,5.0,5.0,5.0,0.051973644623065605,Total Suspended Solids
5.0,5.0,5.0,5.0,5.0,5.0,0.09004199319275262,Total Suspended Solids
5.0,5.0,5.0,5.0,5.0,5.0,0.1559936886651512,Total Suspended Solids
5.0,5.0,5.0,5.0,5.0,5.0,0.27025202397806036,Total Suspended Solids
5.0,5.0,5.0,5.0,5.0,5.0,0.4681994322284034,Total Suspended Solids
5.0,5.0,5.0,5.0,5.0,5.0,0.8111343815756037,Total Suspended Solids
5.0,5.0,5.0,5.0,5.0,5.0,1.405253701061885,Total Suspended Solids
5.0,5.0,5.0,5.0,5.0,5.0,2.434538603224115,Total Suspended Solids
5.0,5.0,5.0,5.0,5.0,5.0,4.217728233777061,Total Suspended Solids
7.3070237746246836,7.3070237746246836,6.448434195442714,5.153839009332126,7.3070237746246836,7.3070237746246836,7.3070237746246836,Total Suspended Solids
12.659088846773834,12.659088846773834,10.809010622060395,7.110945789483219,12.659088846773834,12.659088846773834,12.659088846773834,Total Suspended Solids
14.499631768986601,18.553363564304572,18.118307031865957,9.811239724292793,20.67710469478727,21.93129998933732,21.93129998933732,Total Suspended Solids
16.16373333777856,26.656315048185338,30.370314284915413,13.53693696693707,29.468799503943735,28.14440071814674,37.9949872415095,Total Suspended Solids
18.01882141404715,38.29813011993037,50.90740476703057,18.67742177302024,41.99863361056355,33.88125358846041,65.82460028289864,Total Suspended Solids
20.08681524041683,55.0243635713245,85.33213834410294,25.769942265323422,59.85602585942813,40.787485803007414,114.03814863424184,Total Suspended Solids
22.392149698986202,79.05557208532484,143.0356520372639,35.55575991314758,85.30619983749651,49.10145941876078,197.56594476889057,Total Suspended Solids
24.962064027597577,113.58211294232954,239.75958121690587,49.05762108371278,121.57752918319807,59.110123352453414,342.2740810850392,Total Suspended Solids
27.8269236716514,163.18769240604755,401.89040960452354,67.68664745942401,173.27105920142415,71.15891715037824,592.9743950540159,Total Suspended Solids
31.020579074383438,234.45789361509827,673.6577554578365,93.38981677237116,246.9441529079254,85.66369350681155,1027.3013722657986,Total Suspended Solids
"""
TZn_CURVES = """Biofiltration,Detention Basin,Hydrodynamic Separator,Sand Filter,Vegetated Swale,Wet Pond,xhat,param
5.0,5.0,5.0,5.0,5.0,5.0,0.14342829585075378,Total Zinc
5.0,5.0,5.0,5.0,5.0,5.0,0.22385109523065255,Total Zinc
5.0,5.0,5.0,5.0,5.0,5.0,0.34936839023803634,Total Zinc
5.0,5.0,5.0,5.0,5.0,5.0,0.5452654675276436,Total Zinc
5.0,5.0,5.0,5.0,5.0,5.0,0.8510055242134802,Total Zinc
5.0,5.0,5.0,5.0,5.0,5.0,1.328179474716404,Total Zinc
5.0,5.0,5.0,5.0,5.0,5.0,2.0729133558660857,Total Zinc
5.0,5.0,5.0,5.0,5.0,5.0,3.235232784970944,Total Zinc
5.049285414333075,5.049285414333075,5.0,5.049285414333075,5.049285414333075,5.049285414333075,5.049285414333075,Total Zinc
7.880509654153281,7.880509654153281,6.820108514134762,7.880509654153281,7.880509654153281,7.880509654153281,7.880509654153281,Total Zinc
12.29925173825923,12.29925173825923,10.799975556402574,12.258658865316907,12.29925173825923,12.29925173825923,12.29925173825923,Total Zinc
17.528931038354315,19.195661189419116,17.10228976227524,14.453071221143135,19.195661189419116,19.195661189419116,19.195661189419116,Total Zinc
19.404160906861865,29.95901021789499,27.08231269462714,17.040303512682474,28.238688539389816,23.734284626130204,29.95901021789499,Total Zinc
21.48000124340358,41.470098519637624,42.886167354469315,20.090674110811754,35.57815184520709,28.639958042678828,46.75756069974154,Total Zinc
23.777913182190655,55.09877845074076,67.91234452884929,23.687089019654525,44.825200963385946,34.55959215148848,72.97535755317173,Total Zinc
26.321653750994308,73.20637025557625,107.5425206753639,27.927295178368112,56.47563285889512,41.70276394600159,113.89393993863118,Total Zinc
29.137521483851355,97.2648177815359,170.2988438029563,32.92653712461447,71.15410613368923,50.32236818978274,177.75630006736043,Total Zinc
32.254628309204485,129.2298026120858,269.6765522929342,38.82068922515562,89.64763320729902,60.72357082871138,277.4274226588606,Total Zinc
35.705200524400325,171.6997190152442,427.04601647648497,45.76994860444981,112.94777738575644,73.27461299681427,432.9859184398634,Total Zinc
39.52491196817886,228.1268942150092,675.7688326930225,53.96318914133291,142.3038172896651,88.41984811759859,675.7688326930225,Total Zinc
"""

PARAMS = """bmp,pollutant,unit,N,ND_infl,ND_effl,dl,A,B,e1,C,D,E,e2,Low_Slope,High_Slope,MAD
Detention Basin,Dissolved Copper,ug/L,134,4,6,3.0,,,,,0.9236272807281125,0.9513943204363491,1.1465436448038817,0.8753243543458822,1.0207210594775327,1.2688514137317966
Sand Filter,Dissolved Copper,ug/L,128,4,8,3.0,0.06842614767415078,0.821328773505593,0.09032676133288714,,,,,0.7222222222222222,0.9148936102756174,1.1804019650747595
Vegetated Swale,Dissolved Copper,ug/L,127,5,3,3.0,,,,,1.188706301595668,0.8025579439621737,1.1598547343095786,0.7100117403120254,0.8795000412322551,1.2444785186877936
Wet Pond,Dissolved Copper,ug/L,212,16,27,3.0,2.239050679625116,0.32922355713999807,0.3082170574574224,,,,,0.25,0.3999999894036187,1.2866215613633103
Biofiltration,Dissolved Zinc,ug/L,81,1,4,5.0,,,,,6.593931010536991,0.26856688512436294,1.1061692766308953,0.18281550707458552,0.3816881096205451,1.3050419884607825
Detention Basin,Dissolved Zinc,ug/L,140,8,8,5.0,,,,,1.2401984126131742,0.9002380293927091,1.069339248746588,0.835621130929328,0.9602928444322281,1.3124211286680474
Sand Filter,Dissolved Zinc,ug/L,176,2,40,5.0,,,,,0.4860124167762393,0.740536240375053,1.8631585743995562,0.6224356751577328,0.8516059603459485,1.919933583469468
Vegetated Swale,Dissolved Zinc,ug/L,135,5,6,5.0,,,,,2.77240458323549,0.5679860784050093,1.2060550157406025,0.45718622659250935,0.6706339960759037,1.3497874275524826
Wet Pond,Dissolved Zinc,ug/L,234,20,27,5.0,,,,,2.480004942923664,0.643110051016774,1.0801212086422922,0.5207984510867515,0.7642015922570726,1.6472127675278565
Biofiltration,Fecal Coliform,MPN/100 mL,27,3,10,400.0,,,,,2.1676462003973334,0.5312402086342878,9.698424393225666,0.0,0.7931980201367962,4.997986782590709
Detention Basin,Fecal Coliform,MPN/100 mL,104,1,1,400.0,,,,,5.108471961699482,0.7765970165394386,1.5736723284639285,0.6514775783924994,0.906194947047279,2.0109542715713635
Sand Filter,Fecal Coliform,MPN/100 mL,100,3,6,400.0,,,,,1.9776906151289153,0.8332308567851365,2.2295368785930068,0.696795082269774,0.9568417654197242,2.6285016660987557
Vegetated Swale,Fecal Coliform,MPN/100 mL,64,12,4,400.0,,,,,5.2019760013725245,0.8023408584658163,0.9462900220069328,0.6332729161781256,0.8832157857131984,1.5156243370871099
Wet Pond,Fecal Coliform,MPN/100 mL,90,0,2,400.0,,,,,0.7769382045000744,0.8971574873810775,4.31945881091867,0.6771964859705935,1.125157732232468,3.580556264602806
Biofiltration,Total Copper,ug/L,195,2,10,2.9999370574951167,,,,,3.076352906619502,0.2904278679630129,1.3789442920881192,0.1805601020759985,0.3982874062265809,1.5881095699310066
Detention Basin,Total Copper,ug/L,167,15,18,2.9999370574951167,,,,,1.1946969305399533,0.7832099450586449,1.1191210440851758,0.7099388424499294,0.865610428443,1.3636502807048616
Hydrodynamic Separator,Total Copper,ug/L,32,0,0,2.9999370574951167,,,,,1.561114934340905,0.814183256544875,0.8920593005816799,0.527423926667197,1.0656704417943643,1.278994953315628
Sand Filter,Total Copper,ug/L,235,18,26,2.9999370574951167,,,,,1.425525773617589,0.677332437035123,1.0868718493775225,0.5503397132132092,0.7991337402307842,1.543744039950393
Vegetated Swale,Total Copper,ug/L,233,27,33,2.9999370574951167,,,,,1.6473139890060997,0.6917289724570004,1.017358236494385,0.6062249469441255,0.7754384270644044,1.3506558514096174
Wet Pond,Total Copper,ug/L,492,52,89,2.9999370574951167,,,,,1.3818325002660055,0.5961053227134463,1.3476312542642725,0.5139614577111147,0.6821084379722717,1.679012014992582
Biofiltration,Total Lead,ug/L,99,38,71,1.0,,,,,2.3626053666664575,0.4038537623100841,0.943265944087347,0.0,0.7617464582497366,1.6701483605089862
Detention Basin,Total Lead,ug/L,106,48,55,1.0,-0.8310306072235107,1.0,0.16879213084663003,,,,,0.9359278886561284,1.0,0.8310306072235107
Sand Filter,Total Lead,ug/L,192,28,53,1.0,0.9545496123033135,,0.17544229194125768,0.45703577110499105,,,,0.2442585669709935,0.6966527888457994,0.825680855196066
Vegetated Swale,Total Lead,ug/L,183,62,65,1.0,1.6949999594092362,0.43500001353025464,-0.3541662570299971,,,,,0.38248847913609413,0.47540984546306364,0.8649997158646539
Wet Pond,Total Lead,ug/L,466,84,144,1.0,0.9080340321142439,0.20000004768371582,0.8049071405381525,,,,,0.16,0.25000000764162117,1.3550000619888323
Biofiltration,Total Nitrogen,mg/L,240,2,3,1.7000000476837158,1.8728950827998465,,0.11719728636460723,0.7688208386386141,,,,0.47634528415591554,1.090957846836765,1.1055511057811933
Detention Basin,Total Nitrogen,mg/L,188,0,0,1.7000000476837158,0.8314740585094027,,0.13592487767194097,1.4296972454232912,,,,1.2398035787761914,1.6338148451692842,0.39918768489789547
Hydrodynamic Separator,Total Nitrogen,mg/L,53,0,0,1.7000000476837158,0.9599587298760718,0.40994790170686946,0.011273821574265645,,,,,0.23466561336194605,0.5719868377616023,0.4284826745573447
Sand Filter,Total Nitrogen,mg/L,149,0,0,1.7000000476837158,0.38108752196832774,0.5435981010122998,0.043527952933788805,,,,,0.4545412778889943,0.6239315803896243,0.3356678668973436
Vegetated Swale,Total Nitrogen,mg/L,125,0,0,1.7000000476837158,0.4581131436663697,0.629469960741265,0.231273548603153,,,,,0.4948453196481888,0.7635135992985983,0.3162084472001361
Wet Pond,Total Nitrogen,mg/L,476,0,0,1.7000000476837158,1.025825332092291,,0.05486862329624412,0.5830934717594277,,,,0.4747812890822995,0.6977672150357,0.3983147342254547
Biofiltration,Total Phosphorus,mg/L,305,8,14,0.10000000149011612,0.4815547464896113,,0.018476621291603632,0.09711014577965155,,,,0.05720633907492513,0.14291505504826804,0.21920595695055584
Detention Basin,Total Phosphorus,mg/L,342,0,0,0.10000000149011612,0.363657107344895,,0.015646464678879837,0.11805364643657323,,,,0.10149579496674248,0.13551681138512067,0.06122936657012483
Sand Filter,Total Phosphorus,mg/L,233,0,1,0.10000000149011612,0.1986469570100241,,0.019211702133698792,0.056801386431509844,,,,0.046935682514544746,0.06832532543672404,0.032771347541307574
Vegetated Swale,Total Phosphorus,mg/L,197,2,1,0.10000000149011612,0.4477732473488902,,0.023352739979538864,0.13580852659051185,,,,0.10315652875105655,0.17247330347075931,0.09231885594842176
Wet Pond,Total Phosphorus,mg/L,671,4,15,0.10000000149011612,0.2784379092700252,,0.0313343264930728,0.10353803216857162,,,,0.0901906290043048,0.11825047761423185,0.08627082835857168
Biofiltration,Total Suspended Solids,mg/L,391,0,20,5.0,,,,,5.182555667045641,0.19770519929225766,1.5194191572811055,0.11723262681851129,0.2814099934269232,1.850654342681905
Detention Basin,Total Suspended Solids,mg/L,379,1,1,5.0,,,,,1.6077335597645468,0.6594158496071107,1.506223687056861,0.5793589426457443,0.7372364081343984,1.633157135050027
Hydrodynamic Separator,Total Suspended Solids,mg/L,108,0,0,5.0,,,,,0.768986927019923,0.9399558346136275,1.2931752195325439,0.8327891682668732,1.0267582378929538,1.420557398271768
Sand Filter,Total Suspended Solids,mg/L,318,1,30,5.0,,,,,0.8745098001020576,0.585751237677174,1.8383537645812948,0.4775901242760519,0.6937841595852507,2.098543306773352
Vegetated Swale,Total Suspended Solids,mg/L,215,1,2,5.0,,,,,2.0892556648094356,0.6447308912570916,1.3516757063921951,0.5321082794658546,0.7654435158303247,1.6400528244260757
Wet Pond,Total Suspended Solids,mg/L,727,3,13,5.0,,,,,3.7025622993393044,0.33757988062448374,2.2264134355118554,0.26981668329817793,0.40716122979134967,2.219667217990105
Biofiltration,Total Zinc,ug/L,268,5,53,5.0,,,,,6.852341396059041,0.2283179889967647,1.3029810348690831,0.13658271777200756,0.3213957392205946,1.6827187163230874
Detention Basin,Total Zinc,ug/L,223,16,29,5.0,,,,,3.0177319909924547,0.6383411141904243,1.1806449453918824,0.5482920629554029,0.7232921120167302,1.568377926011119
Hydrodynamic Separator,Total Zinc,ug/L,63,0,0,5.0,,,,,0.7981011797423625,1.0326244543915575,1.0137466486757027,0.8639105175658841,1.1644848884972785,1.3179304389023438
Sand Filter,Total Zinc,ug/L,302,5,41,5.0,,,,,3.279633643134738,0.36993358626138795,1.4771850176834287,0.2609056640726383,0.47621196705476626,2.038610474670809
Vegetated Swale,Total Zinc,ug/L,240,25,27,5.0,,,,,4.267430877118879,0.5190181303506816,1.1332702964227863,0.45065671733338925,0.5849625007211564,1.3763598315998733
Wet Pond,Total Zinc,ug/L,638,40,80,5.0,,,,,4.156361721427686,0.4220690064430488,1.3597727425574873,0.34548511359011674,0.5022858032054983,1.7177534041269542
"""


@pytest.fixture
def KTRL_curves():
    curves = {
        "Dissolved Copper": DCu_CURVES,
        "Dissolved Zinc": DZn_CURVES,
        "Fecal Coliform": FC_CURVES,
        "Total Copper": TCu_CURVES,
        "Total Lead": TPb_CURVES,
        "Total Nitrogen": TN_CURVES,
        "Total Phosphorus": TP_CURVES,
        "Total Suspended Solids": TSS_CURVES,
        "Total Zinc": TZn_CURVES,
    }

    return {k: pandas.read_csv(io.StringIO(v)) for k, v in curves.items()}


@pytest.fixture
def tmnt_params():
    df = pandas.read_csv(io.StringIO(PARAMS))
    df["unit"] = df["unit"].replace("MPN/100 mL", "mpn/_100ml")
    return df
