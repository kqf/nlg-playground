dataset = data/input-test.txt
size = 12
model = artifacts/hmm.builtin.$(size).pkl

data $(dataset): model/dataset.py
	python model/dataset.py

train $(model): $(dataset)
	@-mkdir artifacts
	nlg-train -n $(size) -o artifacts/hmm < $(dataset)

generate: $(model) 
	nlg-generate -w 10 --filename $(model)
# 	python model/freq.py -l 20 -w 12 artifacts/hmm.builtin.8.freqdist artifacts/hmm.builtin.8.le
# 	python model/rnd.py -l 20 -w 12 artifacts/hmm.builtin.8.le

clean:
	rm -rf $(model).pkl

.PHONY: data train generate clean
