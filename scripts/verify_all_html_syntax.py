import subprocess
import re

files_to_test = ['index.html', 'app/index.html', 'app/index_carbon.html', 'app/index_nordea_simulation.html']

for filepath in files_to_test:
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    scripts = re.findall(r'<script(?:\s+type="text/javascript")?>(.*?)</script>', html, re.DOTALL)
    print(f"Testing {filepath}: found {len(scripts)} script block(s)")
    for i, s in enumerate(scripts):
        tmp_name = f'temp_syntax_{i}.js'
        with open(tmp_name, 'w', encoding='utf-8') as tf:
            tf.write(s)
        res = subprocess.run(['node', '-c', tmp_name], capture_output=True, text=True)
        if res.returncode != 0:
            print(f"  [ERROR] Script {i} in {filepath} failed syntax check:\n{res.stderr}")
            exit(1)
        else:
            print(f"  [PASS] Script {i} passed syntax check.")

print("\nALL HTML FILES PASSED NODE.JS SYNTAX CHECK!")
