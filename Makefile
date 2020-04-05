rawdata = data/result.json
dataset = data/input.txt
model = artifacts/hmm.$(subst /,.,$(dataset)).json

generate: $(model) 
	nlg-generate -w 10 --filename $(model)

talk: $(model)
	nlg-dialogue --filename $(model)

data $(dataset): model/dataset.py
	nlg-dataset --ifile $(rawdata) --ofile $(dataset)

train $(model): $(dataset)
	-@mkdir artifacts
	nlg-train -o $(model) --inputs $(dataset)

clean:
	rm -rf $(model)

.PHONY: data train generate clean
