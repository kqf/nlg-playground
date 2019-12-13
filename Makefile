dataset = data/input-test.txt
model = demo/hmm.builtin.9

data $(dataset): model/dataset.py
	python model/dataset.py

train $(model).pkl: $(dataset)
	python model/train.py -n 9 -o demo/hmm < $(dataset)

generate: $(model).pkl 
	python model/generate.py -l 20 -w 12 $(model)
# 	python freq.py -l 20 -w 12 demo/hmm.builtin.8.freqdist demo/hmm.builtin.8.le
# 	python rnd.py -l 20 -w 12 demo/hmm.builtin.8.le
