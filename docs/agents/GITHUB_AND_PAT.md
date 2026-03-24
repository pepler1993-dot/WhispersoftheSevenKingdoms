# GitHub and PAT

## Zweck
Diese Seite beschreibt, wie Agenten in diesem Projekt sauber mit GitHub arbeiten und wie ein vorhandener **PAT (Personal Access Token)** sicher benutzt wird.

---

## Sicherheitsregel Nummer 1

**Den PAT niemals in Doku, Commits, Screenshots oder Chatnachrichten ausschreiben.**

Wenn ein Remote bereits einen eingebetteten Token enthält, ist das ein lokaler Betriebszustand — kein Freifahrtschein, ihn überall zu reproduzieren.

---

## Erwartetes Zielverhalten

Ein Agent soll:
- bestehenden Git-Remote prüfen
- vorhandene Authentifizierung nutzen, wenn sie bereits sauber eingerichtet ist
- nicht unnötig an Remote-URLs herumspielen
- niemals einen Token committen

---

## Vor dem Push

Immer zuerst:

```bash
git status
git branch --show-current
git fetch --all --prune
```

Dann prüfen:
- gibt es lokale Änderungen?
- ist `main` hinter `origin/main`?
- ist der Worktree sauber genug für Pull/Rebase?

---

## Sicheres Standardvorgehen

### Fall A – kleiner sauberer Fix auf `main`

```bash
git add <dateien>
git commit -m "docs: ..."
git pull --rebase origin main
git push origin main
```

Nur tun, wenn:
- der Worktree sauber ist
- keine offenen Konflikte absehbar sind
- der Scope klein und klar ist

### Fall B – Konfliktpotenzial oder größere Änderung

```bash
git checkout -b docs/<name>-<topic>
git add <dateien>
git commit -m "docs: ..."
git push -u origin docs/<name>-<topic>
```

Dann kann reviewed und später gezielt gemerged werden.

---

## Wenn `git pull --rebase` blockiert

Typischer Grund:
- schmutziger Worktree
- lokale Änderung auf Datei, die upstream ebenfalls geändert wurde

Dann nicht stumpf weitermachen.

Stattdessen:
1. Diff prüfen
2. Scope sichern
3. ggf. Branch erstellen
4. Konflikte dort lösen

---

## Wenn der Remote bereits einen PAT verwendet

Beispielhaft kann `git remote -v` einen bereits authentifizierten HTTPS-Remote zeigen.

Dann gilt:
- vorhandenen Remote nutzen
- nicht auf "normales https ohne PAT" zurückfallen, wenn klar ist, dass PAT eingerichtet ist
- aber den Token **nicht** auslesen, posten, dokumentieren oder weiterverbreiten

---

## Niemals tun

- Token in `README.md`, `CHANGELOG.md`, Issues oder Commit-Message schreiben
- Token in Skripte hardcoden
- `.git/config`-Inhalt öffentlich dumpen, wenn dort Secrets enthalten sind
- behaupten, ein Push sei unmöglich, ohne den vorhandenen Remote ehrlich geprüft zu haben

---

## Push-Checkliste für Agenten

Vor jedem Push kurz prüfen:
- [ ] richtiger Pfad / richtiges Repo?
- [ ] richtiger Branch?
- [ ] keine Secrets im Diff?
- [ ] keine versehentlichen Rollbacks?
- [ ] falls `main`: wirklich konfliktarm?

Wenn alle fünf Punkte sauber sind, erst dann pushen.
