import file_io as fio
from llama_cpp import Llama

print("Pawma v1.0")

template_mapping = fio.get_conf_file()["mapping"]
print("template:",template_mapping)

def feed_as_template(role="user",content="",model_name="other"):
    print("role:",role,"content:",content)
    model_name = model_name.lower() + "__other__" # since other will usually be the last one in the list, put it in to detact if a model name does not meet any of the assigned names
    for i in template_mapping.keys():
        if(i in model_name):
            print("It is",i,"role:",role)
            call_role = template_mapping[i][role]
            print("call role:",call_role)
            call_content = template_mapping[i]["around"]
            print("Content after around:",call_content)
            call_content = call_content.replace("__role__",call_role,1)
            print("Content after putting role:",call_content)
            if(content == ""):
                call_content = call_content[0:call_content.find("__content__")+len("__content__")]# if it's nothing, it means it's asking ai for response, so we may not close the dialog
            call_content = call_content.replace("__content__",content)
            print("After template feed:",call_content)
            return call_content
        
class Chat(object):
    def __init__(self,model_path,n_ctx=4096,n_threads=4,n_gpu_layers=-1,max_tokens=1600,n_batch=256):
        self.llm = Llama(model_path=model_path,n_ctx=n_ctx,n_threads=n_threads,n_gpu_layers=n_gpu_layers,verbose=False,n_batch=256)
        self.history = []#each = {"role":"user/assistant","content": "What they said"}
        self.gen_max_words = max_tokens
        self.max_contents = n_ctx
        self.model_name = model_path.split("/")[-1]
    def chat(self,user_input):
        self.history.append({"role":"user","content":user_input})
        prompt = ""
        for i in range(len(self.history)-1,-1,-1):
            print("To give feed template user:",self.history[i]['role'],"content:",self.history[i]['content'],"model name:",self.model_name)
            after_add = feed_as_template(self.history[i]['role'],self.history[i]['content'],self.model_name)+prompt
            if(len(self.llm.tokenize((after_add).encode("utf-8"), add_bos=True)) > self.max_contents):# Replace split with get_token_num in future
                break
            else:
                prompt = after_add+""
        prompt += feed_as_template("assistant",model_name=self.model_name)
        print("Ask Prompt { ",prompt, "}")
        out_put = self.llm(prompt,max_tokens=self.gen_max_words)
        reply = out_put["choices"][0]["text"].strip()
        self.history.append({"role": "assistant", "content": reply})
        return reply
    def cls_history(self):
        self.history = []
    def set_hist(self,thing):
        self.history = thing.copy()

def main():
    test = Chat("./models/DeepSeek-R1-0528-Qwen3-8B-Q8_0.gguf")
    while 1:
        res = test.chat(input("User:"))
        print("Assistant:"+res)

if __name__ == "__main__":
    main()