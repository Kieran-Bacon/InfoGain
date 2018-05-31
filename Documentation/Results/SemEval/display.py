import matplotlib.pyplot as plt
import numpy
structures = [0,1,2,3,4,5]
alphas = numpy.logspace(-16,1,20)

results = [[{'F1': 0.0, 'recall': 0.0, 'precision': 0.525371383692234}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5400073387460755}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5209644629774364}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5206579700025663}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5399920802572494}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5187734452945214}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5310621738871018}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5389078224345243}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5392272360350254}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.545524936103525}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.546015216443332}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5219444758222229}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5314874923926552}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5301359707260246}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5390059570599592}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5401402350453705}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5431502538897715}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5169576141528495}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5334392790548051}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5232724131932296}], [{'F1': 0.0, 'recall': 0.0, 'precision': 0.5621462280939037}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5442829962590527}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5513243527913929}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5758883625919673}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.565698747360251}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5453574799780185}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5537684527915445}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5584697361837758}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5652249968395673}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5672800045887582}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5565291137693447}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5547739785053085}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.556375292710656}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5614152012855234}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5719943393924841}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5559133882669915}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5580449290932284}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5681613417808993}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5581274643996804}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5501991174725984}], [{'F1': 0.0, 'recall': 0.0, 'precision': 0.5846540558011964}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5752754241044258}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.569699313409578}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5944988239081832}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5782997234447278}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5833932480507811}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.574945284709497}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5752531061835664}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5891784916288076}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5832674909226301}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5645275393970118}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5746160142816583}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5701949047227657}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5804184783783651}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5726073832797844}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5846249516252259}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5719991881705262}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5746645434551125}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5636079052376934}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5840611861846426}], [{'F1': 0.0, 'recall': 0.0, 'precision': 0.5784529663673551}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5927940060418766}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5810818090336068}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5805923301536391}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5809515863867147}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5727447243453755}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5852934281177268}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5933446366251101}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5811185764596795}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5969671527794979}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.592732654062543}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.577245473893383}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5911681649764029}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.579822573053484}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5954041158913337}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5711548782489595}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5838437479284908}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.588433520488218}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.590972374762237}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5921817570365987}], [{'F1': 0.0, 'recall': 0.0, 'precision': 0.601306832028137}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5964701374977889}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5965938264821928}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5994373569210862}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6030625064799232}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.60032957123976}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5999859526522002}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5992815345981392}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6021230949778545}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5978781553774872}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6071468337299443}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6049613589667524}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6135323450489895}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5998353042435012}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6075641420271032}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6080708081110416}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6055336722886343}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5985561558120096}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6106041283609878}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.5999551730513402}], [{'F1': 0.0, 'recall': 0.0, 'precision': 0.6142228482193489}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6145384281713643}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6182272588688943}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6184100414346321}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6152898779911362}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6373009798621825}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6150330746005139}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6151801250630682}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6165509472747859}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6121020530717697}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6071893450758721}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6189740384910335}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6261517427716548}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6101662509465691}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.611922953774757}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6159833106373908}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6232102862779996}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6199764873536853}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6164699624449999}, {'F1': 0.0, 'recall': 0.0, 'precision': 0.6110621144310617}]]

import random
struct_i, alpha_i, precision = 0, 0, 0

# Iterate through information to identify best score
for i, result_dict in enumerate(results):
    collection = [d["precision"] for d in result_dict]
    if max(collection) > precision:
        alpha_i, struct_i = collection.index(max(collection)), i
        precision = max(collection)

plt.figure()
plt.title("Model metrics with changing hidden layers structure")

struc_range = range(len(structures))
precision = [results[i][alpha_i]["precision"] for i in struc_range]


plt.plot(range(len(structures)), precision, "b", label="Precision")

plt.ylabel("Precision")
plt.xlabel("Structure ID")
plt.legend()

plt.savefig("./results1conf.pdf", bbox_inches='tight')

plt.figure()
plt.title("Model metrics with changing alphas")

alpha_range = range(len(alphas))
precision = [results[struct_i][i]["precision"] for i in alpha_range]

plt.plot(alpha_range, precision, "b", label="Precision")

plt.ylabel("Precision")
plt.xlabel("Alpha value (e^-x)")

plt.legend()

plt.savefig("./results2conf.pdf", bbox_inches='tight')