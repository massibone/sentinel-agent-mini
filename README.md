Versione didattica di SentinelAgent — 3 file, zero dipendenze, per capire i gate identity/policy/audit prima di passare all'architettura completa.

Comando                                  Gate scattato         Motivo
python main.py run delete_file           Identitytool          non in whitelist
python main.py read ../secrets.txt       Toolpath              traversal bloccato
python main.py con can_read_docs=False   Policy                flag disabilitato


Qualcuno prova a leggere un file fuori dalla cartella docs/ usando ../.
python main.py read ../secrets.txt

── Esecuzione: 'read_document' ──
  [AUDIT] TOOL_CALL — {'tool': 'read_document', 'args': {'filename': '../secrets.txt'}}
  [AUDIT] TOOL_ERROR — {'tool': 'read_document', 'error': "File non trovato: '../secrets.txt'"}
[ERRORE] File non trovato: '../secrets.txt'

Ora il caso 2 — policy denied. Esegui:
python main.py run delete_file

── Esecuzione: 'delete_file' ──
  [AUDIT] IDENTITY_DENIED — {'tool': 'delete_file'}
[BLOCCATO] 'delete_file' non è nella whitelist dell'agente.

Ora vediamo il blocco di policy — che è diverso: il tool esiste ed è noto, ma la policy lo vieta.
In agent.py cambia temporaneamente una riga:

DA
can_read_docs: bool = True

A
can_read_docs: bool = False

e── Esecuzione: 'list_documents' ──
  [AUDIT] POLICY_DENIED — {'tool': 'list_documents', 'reason': "Policy nega l'accesso a: 'list_documents'"}
[BLOCCATO] Policy: Policy nega l'accesso a: 'list_documents'
