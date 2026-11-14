import os, sys, shutil, zipfile, subprocess
import pypdf

evidence = []

def log(msg):
    print(msg)
    evidence.append(msg)

log("================================================================================")
log("MANDATORY FINAL VERIFICATION AUDIT — Quantitative Research TAKE-HOME SUBMISSION")
log("================================================================================")

# 1. FILE EXISTENCE & SUBMISSION FOLDER INTEGRITY
sub_files = sorted(os.listdir('submission'))
expected_files = ['failed_ideas.md', 'report.pdf', 'survivorship_bias.md', 'task1.py', 'task2.py']
log(f"\n[CHECK 1] Submission Directory File Inventory:")
log(f"   Actual Files: {sub_files}")
log(f"   Expected:     {expected_files}")
check1_pass = (sub_files == expected_files)
log(f"   RESULT: {'PASS' if check1_pass else 'FAIL'}")

# 2. HARNESS & TEMPLATE UNTOUCHED INTEGRITY
import hashlib
with zipfile.ZipFile('candidate_pack.zip', 'r') as z:
    for orig_f in ['harness_public.py', 'task1_template.py', 'task2_template.py', 'README.md']:
        orig_bytes = z.read(orig_f)
        curr_bytes = open(os.path.join('candidate_pack', orig_f), 'rb').read()
        same = (hashlib.md5(orig_bytes).hexdigest() == hashlib.md5(curr_bytes).hexdigest())
        log(f"[CHECK 2] Untouched Check for {orig_f:18}: {'PASS (Exact Match)' if same else 'FAIL'}")

# 3. TASK 1 SIGNATURE & PARAMETER COUNT
sys.path.insert(0, os.path.abspath('submission'))
import task1
t1_params = task1.PARAMS
t1_param_count = len(t1_params)
has_t1_sig = hasattr(task1, 'positions') and callable(task1.positions)
log(f"\n[CHECK 3] Task 1 Parameter Count & Function Signature:")
log(f"   PARAMS: {t1_params} (Count: {t1_param_count} <= 6)")
log(f"   Function: positions(bars, params) present: {has_t1_sig}")
check3_pass = (t1_param_count <= 6) and has_t1_sig
log(f"   RESULT: {'PASS' if check3_pass else 'FAIL'}")

# 4. TASK 2 SIGNATURE & PARAMETER COUNT
import task2
t2_params = task2.PARAMS
t2_param_count = len(t2_params)
has_t2_sig = hasattr(task2, 'orders') and callable(task2.orders)
log(f"\n[CHECK 4] Task 2 Parameter Count & Function Signature:")
log(f"   PARAMS: {t2_params} (Count: {t2_param_count} <= 6)")
log(f"   Function: orders(date, hist, portfolio, params, state) present: {has_t2_sig}")
check4_pass = (t2_param_count <= 6) and has_t2_sig
log(f"   RESULT: {'PASS' if check4_pass else 'FAIL'}")

# 5. REPORT.PDF PAGE COUNT & CONTENT
reader = pypdf.PdfReader('submission/report.pdf')
pdf_pages = len(reader.pages)
log(f"\n[CHECK 5] report.pdf Page Count:")
log(f"   Page Count: {pdf_pages} (Requirement: strictly <= 3)")
check5_pass = (pdf_pages <= 3)
log(f"   RESULT: {'PASS' if check5_pass else 'FAIL'}")

# 6. OFFICIAL HARNESS BACKTEST TASK 1
log(f"\n[CHECK 6] Official Harness Execution — Task 1:")
p1 = subprocess.run(['python', 'candidate_pack/harness_public.py', 'task1', 'submission/task1.py'], capture_output=True, text=True)
log(p1.stdout.strip())
check6_pass = ('look-ahead check: OK' in p1.stdout) and ('sharpe' in p1.stdout) and (p1.returncode == 0)
log(f"   RESULT: {'PASS' if check6_pass else 'FAIL'}")

# 7. OFFICIAL HARNESS BACKTEST TASK 2
log(f"\n[CHECK 7] Official Harness Execution — Task 2:")
p2 = subprocess.run(['python', 'candidate_pack/harness_public.py', 'task2', 'submission/task2.py'], capture_output=True, text=True)
log(p2.stdout.strip())
check7_pass = ('sharpe' in p2.stdout) and (p2.returncode == 0)
log(f"   RESULT: {'PASS' if check7_pass else 'FAIL'}")

# 8. CREATE SUBMISSION ZIP
zip_name = 'saksham_aggarwal.zip'
if os.path.exists(zip_name): os.remove(zip_name)
with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in expected_files:
        z.write(os.path.join('submission', f), f)
log(f"\n[CHECK 8] Submission ZIP Creation:")
log(f"   Created {zip_name} ({os.path.getsize(zip_name)} bytes)")
with zipfile.ZipFile(zip_name, 'r') as z:
    zip_contents = z.namelist()
    log(f"   ZIP Contents: {zip_contents}")
check8_pass = (sorted(zip_contents) == expected_files)
log(f"   RESULT: {'PASS' if check8_pass else 'FAIL'}")

# 9. ISOLATED ZIP EXTRACTION & INDEPENDENT RE-RUN TEST
iso_dir = 'test_isolated_verification'
if os.path.exists(iso_dir): shutil.rmtree(iso_dir)
os.makedirs(iso_dir)
shutil.copy('candidate_pack/harness_public.py', os.path.join(iso_dir, 'harness_public.py'))
shutil.copytree('candidate_pack/data', os.path.join(iso_dir, 'data'))

with zipfile.ZipFile(zip_name, 'r') as z:
    z.extractall(iso_dir)

iso_p1 = subprocess.run(['python', 'harness_public.py', 'task1', 'task1.py'], cwd=iso_dir, capture_output=True, text=True)
iso_p2 = subprocess.run(['python', 'harness_public.py', 'task2', 'task2.py'], cwd=iso_dir, capture_output=True, text=True)

log(f"\n[CHECK 9] Isolated Extracted ZIP Execution:")
log(f"   Task 1 exit code: {iso_p1.returncode}, lookahead OK: {'look-ahead check: OK' in iso_p1.stdout}")
log(f"   Task 2 exit code: {iso_p2.returncode}, trades > 0: {'trades           293' in iso_p2.stdout}")

check9_pass = (iso_p1.returncode == 0) and (iso_p2.returncode == 0) and ('look-ahead check: OK' in iso_p1.stdout) and ('trades           293' in iso_p2.stdout)
log(f"   RESULT: {'PASS' if check9_pass else 'FAIL'}")

# Clean up isolated dir
shutil.rmtree(iso_dir)
log("   Isolated test directory successfully cleaned up.")

with open('FINAL_SUBMISSION_CHECKLIST_DATA.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(evidence))
print("\nFinal verification complete. Evidence logged.")

