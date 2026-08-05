import sys, json, copy, time
sys.path.insert(0, '/home/user/Team/tools')
import wp

BACKUP='/tmp/claude-0/-home-user-Team/f8696e23-6866-5a2c-b368-7481df712ef1/scratchpad/strain-cpt-BACKUP.json'
data = json.load(open(BACKUP))['data']
payload = copy.deepcopy(data)

def field(name, title, ftype, **kw):
    f = {"title": title, "name": name, "type": ftype, "object_type": "field",
         "width": "100%", "options": [], "repeater-fields": [],
         "isNested": False, "options_source": "manual"}
    f.update(kw); return f

def tab(name, title):
    return {"title": title, "name": name, "type": "text", "object_type": "tab",
            "width": "100%", "options": [], "repeater-fields": [],
            "isNested": False, "options_source": "manual"}

def sub(name, title, ftype="text"):
    return {"title": title, "name": name, "type": ftype, "options_source": "manual"}

# --- new sections, mirroring the existing headline/html/repeater pattern ---
new_blocks = [
    tab("tab_cultivation", "Cultivation Section"),
    field("cultivation_headline", "Cultivation Headline", "textarea"),
    field("cultivation_html", "Cultivation Content", "wysiwyg"),
    field("grow_specs", "Grow Specs", "repeater",
          **{"repeater-fields": [sub("label", "Label"), sub("value", "Value")]}),
    tab("tab_use", "How to Use Section"),
    field("use_headline", "How to Use Headline", "textarea"),
    field("use_html", "How to Use Content", "wysiwyg"),
    field("use_methods", "Consumption Methods", "repeater",
          **{"repeater-fields": [sub("label", "Method"), sub("text", "Text", "textarea")]}),
]

existing = {f.get('name') for f in payload['meta_fields']}
to_add = [b for b in new_blocks if b['name'] not in existing]
print(f"new entries to add: {len(to_add)} -> {[b['name'] for b in to_add]}")

# insert before the 'In the Jar' tab so order matches the live page flow
idx = next(i for i,f in enumerate(payload['meta_fields']) if f.get('name')=='tab_jar')
payload['meta_fields'][idx:idx] = to_add

# expose every real field (not tabs) to REST
n=0
for f in payload['meta_fields']:
    if f.get('object_type') == 'field':
        f['show_in_rest'] = True; n+=1
print(f"show_in_rest=true on {n} fields; total entries now {len(payload['meta_fields'])}")

res,_ = wp.request("POST", "/jet-engine/v2/edit-post-type/2", data=payload)
print("save:", json.dumps(res)[:200])
