dataset = data/input-test.txt
size = 10
model = artifacts/hmm.$(subst /,.,$(dataset)).n-components.$(size).pkl

generate: $(model) 
	nlg-generate -w 10 --filename $(model)

talk: $(model)
	nlg-dialogue --filename $(model) < data/dialogue.txt

data $(dataset): model/dataset.py
	nlg-dataset

train $(model): $(dataset)
	-@mkdir artifacts
	nlg-train -n $(size) -o $(model) < $(dataset)

clean:
	rm -rf $(model)

.PHONY: data train generate clean
