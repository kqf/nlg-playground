dataset = data/input.txt
size = 10
model = artifacts/hmm.$(subst /,.,$(dataset)).n-components.$(size).json

generate: $(model) 
	nlg-generate -w 10 --filename $(model)

talk: $(model)
	nlg-dialogue --filename $(model)

data $(dataset): model/dataset.py
	nlg-dataset

train $(model): $(dataset)
	-@mkdir artifacts
	nlg-train -n $(size) -o $(model) --inputs $(dataset)

clean:
	rm -rf $(model)

.PHONY: data train generate clean
