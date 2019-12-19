dataset = data/input-test.txt
size = 12
model = artifacts/hmm.builtin.$(size).pkl

generate: $(model) 
	nlg-generate -w 10 --filename $(model)
	nlg-generate -w 10 --filename $(model) -m freq
	nlg-generate -w 10 --filename $(model) -m random

data $(dataset): model/dataset.py
	python model/dataset.py

train $(model): $(dataset)
	@-mkdir artifacts
	nlg-train -n $(size) -o artifacts/hmm < $(dataset)

clean:
	rm -rf $(model)

.PHONY: data train generate clean
