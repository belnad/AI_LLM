
import os
os.system('pip install faiss-cpu') # instal dependances

# processing
os.system('python3 fetch.py')
os.system('python3 storing.py')