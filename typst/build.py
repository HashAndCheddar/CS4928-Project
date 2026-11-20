"""Build this report using the recorded Python Typst binding, without Universe packages."""
from pathlib import Path
import typst

root = Path(__file__).resolve().parent
pdf, warnings = typst.compile_with_warnings(str(root / 'main.typ'))
if warnings:
    raise SystemExit(f'Compiler warnings: {warnings}')
(root / 'report.pdf').write_bytes(pdf)
print('Built report.pdf with no compiler warnings.')
