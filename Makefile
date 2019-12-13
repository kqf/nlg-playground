dataset = data/input-test.txt
model = demo/hmm.builtin.9

data $(dataset): dataset.py
	python dataset.py

train $(model).pkl: $(dataset)
	python train.py -n 9 -o demo/hmm < data/input-test.txt

generate: $(model).pkl 
	python gen.py -l 20 -w 12 $(model)
# 	python freq.py -l 20 -w 12 demo/hmm.builtin.8.freqdist demo/hmm.builtin.8.le
# 	python rnd.py -l 20 -w 12 demo/hmm.builtin.8.le
