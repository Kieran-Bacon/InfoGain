from sklearn.neural_network import MLPClassifier

model = MLPClassifier(hidden_layer_sizes=(5,5,5))

Xtr = [[1,2],[2,3],[7,6],[12,13],[8,6]]
ttr = [-1,-1,1,0,1]

model.fit(Xtr, ttr)

print(model.classes_)

print(model.predict_proba([[2,2],[7,7]]))
print(model.predict_proba([[2,2],[7,7]]))
print(model.predict_proba([[2,2],[7,7]]))