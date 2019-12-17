dataset = data/input-test.txt
model = artifacts/hmm.builtin.9

data $(dataset): model/dataset.py
	python model/dataset.py

train $(model).pkl: $(dataset)
	@-mkdir artifacts
	train -n 9 -o artifacts/hmm < $(dataset)

generate: $(model).pkl 
	echo "skipping the generation"
# 	python model/generate.py -l 20 -w 12 $(model)
# 	python model/freq.py -l 20 -w 12 artifacts/hmm.builtin.8.freqdist artifacts/hmm.builtin.8.le
# 	python model/rnd.py -l 20 -w 12 artifacts/hmm.builtin.8.le

clean:
	rm -rf $(model).pkl

.PHONY: data train generate clean
