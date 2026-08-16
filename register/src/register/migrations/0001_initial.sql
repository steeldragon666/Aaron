-- 0001_initial
-- Intent: S-4 (register schema), CLAUDE.md §1 (schema invariants)
--
-- Every record table in this file carries, from this first migration:
--
--   tenant_id        even though there is currently one tenant
--   visibility       principal_only | principal_and_ea | leadership | all_users
--   shareable_with   JSON array of counterparty ids — DEFAULT DENY ('[]')
--   provenance       verbatim | paraphrase | inferred
--   produced_by      model identifier, even while there is only one model
--
-- Commitment additionally carries direction (by_principal | to_principal | witnessed).
--
-- Adding one of these to an existing table later rewrites every row written
-- before it existed. tests/test_migration_guard.py fails any migration that
-- introduces a record table without them, and any migration that adds one of
-- them to a table that already exists.
--
-- Migrations are additive and reversible. No destructive migration without an
-- explicit decision recorded in docs/.

-- ---------------------------------------------------------------------------
-- Tenancy
-- ---------------------------------------------------------------------------

CREATE TABLE tenant (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    is_zero     INTEGER NOT NULL DEFAULT 0,   -- tenant zero sits inside the shared-harness boundary
    created_at  TEXT NOT NULL
);

-- ---------------------------------------------------------------------------
-- Person — counterparties, colleagues, the principal.
-- person.id is what commitment.counterparty_id points at.
-- ---------------------------------------------------------------------------

CREATE TABLE person (
    id                      TEXT PRIMARY KEY,
    tenant_id               TEXT NOT NULL REFERENCES tenant(id),
    kind                    TEXT NOT NULL CHECK (kind IN ('person', 'org')),
    display_name            TEXT NOT NULL,
    email                   TEXT,
    relationship            TEXT,             -- to the principal, in the principal's words
    cadence_days            INTEGER,          -- expected contact interval, NULL = no cadence
    last_substantive_contact TEXT,
    sensitivity_flags       TEXT NOT NULL DEFAULT '[]',   -- JSON array: comp, personnel, board, m_and_a, legal, health
    is_principal            INTEGER NOT NULL DEFAULT 0,

    tenant_scoped_note      TEXT,

    visibility              TEXT NOT NULL CHECK (visibility IN ('principal_only','principal_and_ea','leadership','all_users')),
    shareable_with          TEXT NOT NULL DEFAULT '[]',
    provenance              TEXT NOT NULL CHECK (provenance IN ('verbatim','paraphrase','inferred')),
    produced_by             TEXT NOT NULL,
    created_at              TEXT NOT NULL,
    updated_at              TEXT NOT NULL
);

CREATE INDEX person_tenant_idx ON person(tenant_id);
CREATE UNIQUE INDEX person_tenant_email_idx ON person(tenant_id, email) WHERE email IS NOT NULL;

-- ---------------------------------------------------------------------------
-- Meeting — including the dark case, which must be loud rather than absent.
-- ---------------------------------------------------------------------------

CREATE TABLE meeting (
    id              TEXT PRIMARY KEY,
    tenant_id       TEXT NOT NULL REFERENCES tenant(id),
    title           TEXT NOT NULL,
    starts_at       TEXT NOT NULL,
    ends_at         TEXT,
    brief_issued    INTEGER NOT NULL DEFAULT 0,
    consent_outcome TEXT NOT NULL DEFAULT 'not_asked'
                    CHECK (consent_outcome IN ('not_asked','granted','declined','not_applicable')),
    capture         TEXT NOT NULL DEFAULT 'none'
                    CHECK (capture IN ('none','partial','transcript','voice_dump')),
    capture_reason  TEXT,                     -- e.g. consent_declined
    known_topics    TEXT NOT NULL DEFAULT '[]',   -- JSON array, from the brief issued beforehand
    gap_flag        INTEGER NOT NULL DEFAULT 0,   -- true = the register does not know what happened here

    visibility      TEXT NOT NULL CHECK (visibility IN ('principal_only','principal_and_ea','leadership','all_users')),
    shareable_with  TEXT NOT NULL DEFAULT '[]',
    provenance      TEXT NOT NULL CHECK (provenance IN ('verbatim','paraphrase','inferred')),
    produced_by     TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE INDEX meeting_tenant_idx ON meeting(tenant_id);
CREATE INDEX meeting_gap_idx ON meeting(tenant_id, gap_flag);

CREATE TABLE meeting_attendee (
    meeting_id  TEXT NOT NULL REFERENCES meeting(id),
    person_id   TEXT NOT NULL REFERENCES person(id),
    tenant_id   TEXT NOT NULL REFERENCES tenant(id),
    PRIMARY KEY (meeting_id, person_id)
);

-- ---------------------------------------------------------------------------
-- Thread — a message chain with a counterparty set and an authority tier.
-- The tier is carried now so Sprint 2's send path has somewhere to read it
-- from; nothing in Sprint 1 acts on it.
-- ---------------------------------------------------------------------------

CREATE TABLE thread (
    id              TEXT PRIMARY KEY,
    tenant_id       TEXT NOT NULL REFERENCES tenant(id),
    subject         TEXT NOT NULL,
    external_ref    TEXT,                     -- RFC 5322 Message-ID of the root, or adapter-native id
    authority_tier  TEXT NOT NULL DEFAULT 'T0' CHECK (authority_tier IN ('T0','T1','T2','T3','T4')),
    last_message_at TEXT,

    visibility      TEXT NOT NULL CHECK (visibility IN ('principal_only','principal_and_ea','leadership','all_users')),
    shareable_with  TEXT NOT NULL DEFAULT '[]',
    provenance      TEXT NOT NULL CHECK (provenance IN ('verbatim','paraphrase','inferred')),
    produced_by     TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE INDEX thread_tenant_idx ON thread(tenant_id);
CREATE UNIQUE INDEX thread_external_idx ON thread(tenant_id, external_ref) WHERE external_ref IS NOT NULL;

CREATE TABLE thread_counterparty (
    thread_id   TEXT NOT NULL REFERENCES thread(id),
    person_id   TEXT NOT NULL REFERENCES person(id),
    tenant_id   TEXT NOT NULL REFERENCES tenant(id),
    PRIMARY KEY (thread_id, person_id)
);

-- ---------------------------------------------------------------------------
-- Commitment — the core record. ACTION_TIER_AND_REGISTER_SPEC §4.
-- ---------------------------------------------------------------------------

CREATE TABLE commitment (
    id              TEXT PRIMARY KEY,
    tenant_id       TEXT NOT NULL REFERENCES tenant(id),
    direction       TEXT NOT NULL CHECK (direction IN ('by_principal','to_principal','witnessed')),
    counterparty_id TEXT REFERENCES person(id),
    statement       TEXT NOT NULL,            -- as close to the words used as capture allows
    made_at         TEXT NOT NULL,
    made_in         TEXT,                     -- meeting_id | thread_id | call_id | 'manual'
    made_in_kind    TEXT CHECK (made_in_kind IN ('meeting','thread','call','manual')),
    source_type     TEXT NOT NULL CHECK (source_type IN ('transcript','email','document','voice_dump','manual','calendar')),
    confidence      REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    due             TEXT,
    status          TEXT NOT NULL DEFAULT 'open'
                    CHECK (status IN ('open','met','missed','superseded','void')),
    owner           TEXT,
    evidence_ref    TEXT,
    superseded_by   TEXT REFERENCES commitment(id),
    last_action     TEXT,                     -- what the agent last did about it
    last_action_at  TEXT,

    visibility      TEXT NOT NULL CHECK (visibility IN ('principal_only','principal_and_ea','leadership','all_users')),
    shareable_with  TEXT NOT NULL DEFAULT '[]',
    provenance      TEXT NOT NULL CHECK (provenance IN ('verbatim','paraphrase','inferred')),
    produced_by     TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE INDEX commitment_tenant_idx ON commitment(tenant_id);
CREATE INDEX commitment_status_idx ON commitment(tenant_id, status);
CREATE INDEX commitment_direction_idx ON commitment(tenant_id, direction);
CREATE INDEX commitment_counterparty_idx ON commitment(tenant_id, counterparty_id);
CREATE INDEX commitment_superseded_idx ON commitment(superseded_by);

-- ---------------------------------------------------------------------------
-- Decision — what was decided, and the reasoning at the time.
-- ---------------------------------------------------------------------------

CREATE TABLE decision (
    id              TEXT PRIMARY KEY,
    tenant_id       TEXT NOT NULL REFERENCES tenant(id),
    statement       TEXT NOT NULL,
    reasoning_at_time TEXT NOT NULL,          -- not reconstructed later
    decided_at      TEXT NOT NULL,
    decided_in      TEXT,                     -- meeting_id | thread_id | 'manual'
    depends_on      TEXT NOT NULL DEFAULT '[]',   -- JSON array of decision/commitment ids
    superseded_by   TEXT REFERENCES decision(id),

    visibility      TEXT NOT NULL CHECK (visibility IN ('principal_only','principal_and_ea','leadership','all_users')),
    shareable_with  TEXT NOT NULL DEFAULT '[]',
    provenance      TEXT NOT NULL CHECK (provenance IN ('verbatim','paraphrase','inferred')),
    produced_by     TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE INDEX decision_tenant_idx ON decision(tenant_id);

CREATE TABLE decision_participant (
    decision_id TEXT NOT NULL REFERENCES decision(id),
    person_id   TEXT NOT NULL REFERENCES person(id),
    tenant_id   TEXT NOT NULL REFERENCES tenant(id),
    PRIMARY KEY (decision_id, person_id)
);

-- ---------------------------------------------------------------------------
-- Exposure — renewals, notice periods, deadlines.
-- ---------------------------------------------------------------------------

CREATE TABLE exposure (
    id              TEXT PRIMARY KEY,
    tenant_id       TEXT NOT NULL REFERENCES tenant(id),
    kind            TEXT NOT NULL CHECK (kind IN ('renewal','notice_period','deadline','obligation')),
    description     TEXT NOT NULL,
    counterparty_id TEXT REFERENCES person(id),
    effective_from  TEXT,
    expires_on      TEXT,
    notice_days     INTEGER,
    status          TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open','discharged','lapsed','void')),

    visibility      TEXT NOT NULL CHECK (visibility IN ('principal_only','principal_and_ea','leadership','all_users')),
    shareable_with  TEXT NOT NULL DEFAULT '[]',
    provenance      TEXT NOT NULL CHECK (provenance IN ('verbatim','paraphrase','inferred')),
    produced_by     TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE INDEX exposure_tenant_idx ON exposure(tenant_id);
CREATE INDEX exposure_expiry_idx ON exposure(tenant_id, expires_on);

-- ---------------------------------------------------------------------------
-- Prediction — links to the AR that carries it. The AR itself lives in the
-- append-only ledger; this is the queryable projection used for scoring.
-- ---------------------------------------------------------------------------

CREATE TABLE prediction (
    id              TEXT PRIMARY KEY,
    tenant_id       TEXT NOT NULL REFERENCES tenant(id),
    ar_id           TEXT NOT NULL,
    agent           TEXT NOT NULL,
    statement       TEXT NOT NULL,
    resolves_on     TEXT NOT NULL,
    falsifiable_by  TEXT NOT NULL,
    stated_confidence REAL CHECK (stated_confidence IS NULL OR (stated_confidence >= 0.0 AND stated_confidence <= 1.0)),
    outcome         TEXT CHECK (outcome IS NULL OR outcome IN ('correct','incorrect','unresolved','void')),
    score           REAL,                     -- Brier component, once resolved
    resolved_at     TEXT,
    ar_was_acted_on INTEGER,                  -- unacted ARs are still scored; NULL until resolution

    visibility      TEXT NOT NULL CHECK (visibility IN ('principal_only','principal_and_ea','leadership','all_users')),
    shareable_with  TEXT NOT NULL DEFAULT '[]',
    provenance      TEXT NOT NULL CHECK (provenance IN ('verbatim','paraphrase','inferred')),
    produced_by     TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE INDEX prediction_tenant_idx ON prediction(tenant_id);
CREATE UNIQUE INDEX prediction_ar_idx ON prediction(ar_id);
CREATE INDEX prediction_resolves_idx ON prediction(tenant_id, resolves_on);

-- ---------------------------------------------------------------------------
-- AR ledger — append-only, hash-chained.
--
-- The chain is over every entry, not only over AR creation: status changes,
-- outcomes and scores are appended, never updated in place. An AR's current
-- state is a fold over its entries.
--
-- Append-only is enforced by trigger as well as in code, because the code is
-- the thing most likely to be wrong.
-- ---------------------------------------------------------------------------

CREATE TABLE ar_ledger (
    seq             INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id       TEXT NOT NULL REFERENCES tenant(id),
    ar_id           TEXT NOT NULL,
    entry_kind      TEXT NOT NULL CHECK (entry_kind IN ('open','status','outcome','void')),
    agent           TEXT NOT NULL,
    payload         TEXT NOT NULL,            -- canonical JSON, the AR body or the delta
    -- The payload is unversioned JSON today because one caller writes it. It
    -- will not stay that way: four agents writing an unversioned payload is the
    -- same retrofit class as a missing invariant, and by then every entry
    -- already written is ambiguous. The version travels inside the payload too,
    -- so it is covered by the hash; this column exists so "which entries are on
    -- v1" is a query rather than a scan.
    payload_schema_version INTEGER NOT NULL DEFAULT 1,
    prev_hash       TEXT NOT NULL,
    entry_hash      TEXT NOT NULL UNIQUE,
    appended_at     TEXT NOT NULL,

    visibility      TEXT NOT NULL CHECK (visibility IN ('principal_only','principal_and_ea','leadership','all_users')),
    shareable_with  TEXT NOT NULL DEFAULT '[]',
    provenance      TEXT NOT NULL CHECK (provenance IN ('verbatim','paraphrase','inferred')),
    produced_by     TEXT NOT NULL
);

CREATE INDEX ar_ledger_ar_idx ON ar_ledger(tenant_id, ar_id, seq);
CREATE INDEX ar_ledger_agent_idx ON ar_ledger(tenant_id, agent, seq);

CREATE TRIGGER ar_ledger_no_update
BEFORE UPDATE ON ar_ledger
BEGIN
    SELECT RAISE(ABORT, 'ar_ledger is append-only: UPDATE rejected');
END;

CREATE TRIGGER ar_ledger_no_delete
BEFORE DELETE ON ar_ledger
BEGIN
    SELECT RAISE(ABORT, 'ar_ledger is append-only: DELETE rejected');
END;

-- ---------------------------------------------------------------------------
-- Curator queue — commitments extracted from conversational sources are
-- proposals, not records. Facts from a source of truth bypass this entirely.
-- ---------------------------------------------------------------------------

CREATE TABLE curator_proposal (
    id              TEXT PRIMARY KEY,
    tenant_id       TEXT NOT NULL REFERENCES tenant(id),
    target_entity   TEXT NOT NULL CHECK (target_entity IN ('commitment','person','decision','exposure')),
    candidate       TEXT NOT NULL,            -- canonical JSON of the proposed record fields
    confidence      REAL NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    source_ref      TEXT NOT NULL,            -- ingest_event id, always resolvable back to the source
    state           TEXT NOT NULL DEFAULT 'queued'
                    CHECK (state IN ('queued','confirmed','auto_confirmed','rejected')),
    resolved_by     TEXT,
    resolved_at     TEXT,
    written_record_id TEXT,

    visibility      TEXT NOT NULL CHECK (visibility IN ('principal_only','principal_and_ea','leadership','all_users')),
    shareable_with  TEXT NOT NULL DEFAULT '[]',
    provenance      TEXT NOT NULL CHECK (provenance IN ('verbatim','paraphrase','inferred')),
    produced_by     TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE INDEX curator_state_idx ON curator_proposal(tenant_id, state);

-- ---------------------------------------------------------------------------
-- Ingest events — one row per source item seen, for dedupe and for tracing a
-- record back to the bytes it came from. Bodies are stored redacted; redaction
-- runs before this insert, never after.
-- ---------------------------------------------------------------------------

CREATE TABLE ingest_event (
    id              TEXT PRIMARY KEY,
    tenant_id       TEXT NOT NULL REFERENCES tenant(id),
    adapter         TEXT NOT NULL,
    source_id       TEXT NOT NULL,            -- adapter-native stable id
    occurred_at     TEXT,
    summary         TEXT NOT NULL,            -- redacted
    body            TEXT,                     -- redacted
    redaction_count INTEGER NOT NULL DEFAULT 0,
    -- Addresses the adapter saw. Carried as structured fields rather than
    -- re-parsed from the redacted body later: sender is what establishes a
    -- commitment's direction, and an extractor that cannot see it declines to
    -- guess. Addresses are personal data, not secrets — they are protected by
    -- visibility and shareable_with, not by redaction.
    sender          TEXT,
    participants    TEXT NOT NULL DEFAULT '[]',

    visibility      TEXT NOT NULL CHECK (visibility IN ('principal_only','principal_and_ea','leadership','all_users')),
    shareable_with  TEXT NOT NULL DEFAULT '[]',
    provenance      TEXT NOT NULL CHECK (provenance IN ('verbatim','paraphrase','inferred')),
    produced_by     TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL
);

CREATE UNIQUE INDEX ingest_event_source_idx ON ingest_event(tenant_id, adapter, source_id);

-- ---------------------------------------------------------------------------
-- Access log — every read of a register record, allowed or denied.
-- Not a client record: it carries tenant_id but deliberately no payload, and
-- is exempt from the invariant guard for that reason.
-- ---------------------------------------------------------------------------

CREATE TABLE access_log (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    tenant_id           TEXT NOT NULL,
    at                  TEXT NOT NULL,
    actor               TEXT NOT NULL,
    actor_role          TEXT NOT NULL,
    counterparty_scope  TEXT,
    entity              TEXT NOT NULL,
    record_id           TEXT NOT NULL,
    decision            TEXT NOT NULL CHECK (decision IN ('allow','deny')),
    reason              TEXT NOT NULL
);

CREATE INDEX access_log_record_idx ON access_log(tenant_id, entity, record_id);
CREATE INDEX access_log_deny_idx ON access_log(tenant_id, decision, at);
