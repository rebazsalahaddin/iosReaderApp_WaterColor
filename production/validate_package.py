"""Run current planning, staging and self-containment validation."""
from pathlib import Path
import runpy,sys
root=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'agent-workflow'))
for validator in ['package-builder/validate_full_book_r6.py','package-builder/validate_narrative_staging.py','validate_self_contained.py','agent-workflow/validate_handoff.py','validate_geometry.py','validate_text_alignment.py','validate_reference_lineage.py','validate_workflow9.py']:
    try:runpy.run_path(str(root/validator),run_name='__main__')
    except SystemExit as result:
        if result.code not in (None,0):raise
