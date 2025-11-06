```
# from repo root
python3 -mvenv .venv
source .venv/bin/activate
pip install -r confgen/requirements.txt
pytest confgen/test_generate_collector_config.py -v
```
