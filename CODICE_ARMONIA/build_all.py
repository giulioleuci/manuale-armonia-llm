import os, subprocess, sys

for orient in ('orizzontale', 'verticale'):
    for script in ('build1.py', 'build2.py', 'build3.py'):
        subprocess.run([sys.executable, script], check=True,
                       env={**os.environ, 'PDF_ORIENT': orient})
