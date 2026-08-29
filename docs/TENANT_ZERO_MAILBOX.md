# Tenant zero — getting real mail onto the farm

Acceptance 1 and 2 in `BUILD_BRIEF_SPRINT_1.md` need a live mailbox. Everything
upstream of the connection is built and tested against fixtures; what was
missing was the sync that puts The Carbon Project's mail on local disk.

This is that sync, scoped to tenant zero only. It is deliberately the smallest
thing that produces a real coverage number, and it is **not** the connectivity
design for client one — see §5.

---

## 1 · The shape

`mbsync` runs on the farm, pulls over IMAP, and writes a Maildir to local disk.
`register ingest` reads that Maildir. Nothing else changes.

```
  farm ──IMAP/993──▶ provider          (the farm dials out; nothing dials in)
   │
   └── ~/mail/carbonproject/  ──▶  register ingest --mailbox …
```

Four properties, and each one is why this is the version we are running rather
than a provider integration:

**Outbound-only.** The farm opens the connection. There is no listener, no
webhook endpoint, no inbound port, and nothing on the public internet that
resolves to the farm. If the link is severed the register goes stale; it does
not become reachable.

**No vendor integration.** No Graph API, no Gmail API, no SDK, no OAuth app
registration. IMAP is a protocol the provider already speaks and `mbsync` is a
package. CLAUDE.md §2 — zero external API dependencies on a client-context
path — stays literally true: the only thing that touches the network is a
sync daemon that hands off a directory, and the register itself still opens no
socket (`register.ingest.mailbox` is read-only against local disk).

**Data lands on-prem.** The Maildir is the copy the system reasons over. It is
inside the same disk-encryption and backup boundary as the register, and the
`shareable_with` default-deny applies to everything extracted from it.

**Reversible.** Delete the Maildir and the channel is gone. There is no app
consent to revoke, no service principal to clean up, no per-tenant credential
record to migrate. That is the point of doing it this way first.

---

## 2 · Setup

`mbsync` is `isync`. Install it on the farm host, not in the repo.

```bash
sudo apt install isync
mkdir -p ~/mail/carbonproject
```

Write `~/.mbsyncrc`. The template below is complete apart from the account
details:

```
IMAPAccount carbonproject
Host            <imap host>
Port            993
User            aaron@carbonproject.com.au
# The credential is never in this file and never in the repository. PassCmd
# runs a command and reads the secret off stdout, so the secret lives wherever
# that command keeps it — pass(1), gpg, a systemd credential, a file with mode
# 0400. Anything but a literal here.
PassCmd         "pass show carbonproject/imap"
TLSType         IMAPS
CertificateFile /etc/ssl/certs/ca-certificates.crt

IMAPStore carbonproject-remote
Account carbonproject

MaildirStore carbonproject-local
Path        ~/mail/carbonproject/
Inbox       ~/mail/carbonproject/Inbox
SubFolders  Verbatim

Channel carbonproject
Far     :carbonproject-remote:
Near    :carbonproject-local:
Patterns "INBOX" "Sent*" "Archive*"
# Pull only. `Sync Pull` means mbsync never writes a flag, a move or a deletion
# back to the provider — the mailbox is a source of truth this system reads and
# does not touch.
Sync    Pull
Create  Near
Expunge Near
SyncState *
```

Then:

```bash
chmod 600 ~/.mbsyncrc
mbsync -V carbonproject          # first run; expect it to take a while
```

Run it on a timer. A systemd user timer at fifteen minutes is fine — the
register is not a real-time system and Q8's compute window is nightly anyway.

```ini
# ~/.config/systemd/user/mbsync.service
[Service]
Type=oneshot
ExecStart=/usr/bin/mbsync -a
```

```ini
# ~/.config/systemd/user/mbsync.timer
[Timer]
OnBootSec=5m
OnUnitActiveSec=15m
[Install]
WantedBy=timers.target
```

`Sent` matters as much as `INBOX`. Commitments made *by* the principal are half
the register — `direction: by_principal` — and they are almost all in Sent.

---

## 3 · Ingest

```bash
register ingest --mailbox ~/mail/carbonproject/Inbox
register ingest --mailbox ~/mail/carbonproject/Sent
register propose --senders senders.json
register queue
register digest --threshold 0.85
```

Ingest is idempotent on RFC 5322 `Message-ID`, so re-running after each sync
adds only what is new. Redaction runs before anything is persisted, which is
the property that makes it safe to point this at a real mailbox at all.

---

## 4 · What to expect, and what not to do about it

**Expect coverage well under 80% on the first real run.** The extraction rules
were written against fixtures and a handful of phrasings. Real mail is worse:
commitments arrive as sentence fragments, inside forwarded threads, in a
postscript, or in phrasing nobody anticipated.

That number is information. It is the first honest measurement this system has
produced, and a low one tells you exactly where the rules are thin.

**Do not tune the extraction rules until they hit 80% on this mailbox.**

This is the standing instruction, and it is not a matter of taste. Tuning rules
against a single mailbox until the number goes green is overfitting to one
person's writing habits. The rules would stop generalising, coverage on client
one would be worse than the honest number here, and — worse — the metric would
have stopped measuring anything. It is the same failure as sycophancy in a
different costume: optimising the score rather than the thing the score was
standing in for.

What to do instead:

- **Record the number.** `register coverage known.json` against a manually
  compiled list. Date it. That is the day-7 artifact, and a real 61% the client
  can falsify by naming what is missing is worth more than a tuned 80%.
- **Read the misses and classify them.** Which are phrasings a rule could
  reasonably catch, and which need a model? That classification is the input to
  the extractor decision, not a pretext to add regexes.
- **Change the rules only for a class of phrasing, never for an instance.** If
  a change would not also have caught a message from a different person, it is
  a fit to this mailbox.
- **Measure against a second mailbox before believing an improvement.** Until
  then an improvement is a hypothesis.

---

## 5 · What this defers

Client one needs the part that is not here:

- **OAuth.** Several providers have already deprecated IMAP basic auth for
  tenants that ask them to. `PassCmd` and an app password work today for tenant
  zero; a client's IT will want an app registration and a token refresh.
- **Per-tenant credential storage.** One `~/.mbsyncrc` on one host is fine for
  one tenant. Four tenants on a farm need credentials scoped, isolated and
  rotatable — and the register's own tenancy model does not currently extend to
  the sync layer.
- **Calendar.** `register ingest --calendar` reads local iCalendar files. The
  equivalent of `mbsync` for CalDAV (`vdirsyncer`) is the same shape of
  solution and is not set up here.
- **Onboarding.** A 7-day setup fee implies someone can do this in an afternoon
  without reading a design document. This file is not that yet.

None of it blocks the coverage number, which is why none of it is here.
