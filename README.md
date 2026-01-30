# AMC
## Generazione exe (da PC Windows):
```
pyinstaller --noconsole --onefile \
--add-data "ui:ui" \
--add-data "database:database" \
--add-data "utils:utils" \
--add-data "acm_data.db:." \
main.py
```
