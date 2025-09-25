import os
import json

def get_conf_file(path = "./res/conf.json"):
    with open(path,"rt",encoding="utf-8") as f:
        raw_json = f.read()
    
    dict_to_go = {"models":[],"chats":[]}
    try:
        dict_to_go = json.loads(raw_json) #loaded data
    except Exception as e:
        print("Error Parsing JSON, probably it is now empty.",e)
    return dict_to_go

def write_conf_file(thing,path="./res/conf.json"):
    with open(path,"wt",encoding="utf-8") as f:
        f.write(json.dumps(thing,indent=2))

def test():
    print(get_conf_file())
    write_conf_file(thing={"models":["gemma","gpt"],"chats":{"1":["thing1","thing2"],"2":["thing3","thing4"]}})

if __name__ == "__main__":
    test()