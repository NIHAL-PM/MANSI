from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

OUT = Path('Personal AI Architecture and SDLC Blueprint.docx')

def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr(); shd = OxmlElement('w:shd'); shd.set(qn('w:fill'), fill); tcPr.append(shd)

def borders(cell):
    tcPr = cell._tc.get_or_add_tcPr(); b = OxmlElement('w:tcBorders')
    for edge in ('top','left','bottom','right','insideH','insideV'):
        e = OxmlElement(f'w:{edge}'); e.set(qn('w:val'),'single'); e.set(qn('w:sz'),'4'); e.set(qn('w:color'),'D9D9D9'); b.append(e)
    tcPr.append(b)

def cell_text(cell, text, bold=False, color=None):
    cell.text = ''
    p = cell.paragraphs[0]; p.paragraph_format.space_after = Pt(2); p.paragraph_format.space_before = Pt(2)
    r = p.add_run(str(text)); r.bold = bold; r.font.size = Pt(8.5)
    if color: r.font.color.rgb = RGBColor(*color)
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    borders(cell)

def table(doc, headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers)); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.style = 'Table Grid'
    for i,h in enumerate(headers):
        c=t.rows[0].cells[i]; shade(c,'17365D'); cell_text(c,h,True,(255,255,255))
        if widths: c.width=Inches(widths[i])
    for ri,row in enumerate(rows):
        cells=t.add_row().cells
        for i,v in enumerate(row):
            if ri % 2: shade(cells[i],'EAF1F8')
            cell_text(cells[i],v)
            if widths: cells[i].width=Inches(widths[i])
    doc.add_paragraph()
    return t

def heading(doc, text, level=1):
    p=doc.add_paragraph(style=f'Heading {level}'); p.paragraph_format.space_before=Pt(12); p.paragraph_format.space_after=Pt(5)
    r=p.add_run(text); r.font.color.rgb=RGBColor(0,0,0)
    return p

def para(doc, text='', boldlead=None):
    p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(6); p.paragraph_format.line_spacing=1.12
    if boldlead and text.startswith(boldlead):
        p.add_run(boldlead).bold=True; p.add_run(text[len(boldlead):])
    else: p.add_run(text)
    return p

def bullets(doc, items):
    for x in items:
        p=doc.add_paragraph(style='List Bullet'); p.paragraph_format.space_after=Pt(2); p.add_run(x)

def code(doc, text):
    p=doc.add_paragraph(); p.paragraph_format.space_after=Pt(7); p.paragraph_format.left_indent=Inches(.25)
    r=p.add_run(text); r.font.name='Consolas'; r.font.size=Pt(8)

doc=Document()
sec=doc.sections[0]; sec.top_margin=Inches(.65); sec.bottom_margin=Inches(.65); sec.left_margin=Inches(.72); sec.right_margin=Inches(.72)
styles=doc.styles; styles['Normal'].font.name='Aptos'; styles['Normal'].font.size=Pt(10)
for s in ['Title','Heading 1','Heading 2','Heading 3']:
    styles[s].font.name='Aptos'; styles[s].font.color.rgb=RGBColor(0,0,0)
styles['Title'].font.size=Pt(24); styles['Heading 1'].font.size=Pt(16); styles['Heading 2'].font.size=Pt(12); styles['Heading 3'].font.size=Pt(10.5)

p=doc.add_paragraph(style='Title'); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run('Personal AI Architecture and SDLC Blueprint')
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=p.add_run('Multi device proactive assistant with continuous multimodal context'); r.italic=True; r.font.size=Pt(11)
para(doc, 'Purpose: This is the build contract for the engineering swarm. It defines the end state, module boundaries, data contracts, Supabase schema, Android application, hardware responsibilities, security requirements, and delivery pipeline. Build the system as a private personal context agent: continuously available, selectively proactive, evidence grounded, and always under user control.')
heading(doc,'1 Product Decision and Non Negotiables')
para(doc,'The product is a personal AI butler that maintains a time aligned memory of the wearer\'s life across separate devices. It receives continuous audio, video, live location, notification context, and opted in integrations. It turns source observations into evidence backed memory events, then asks useful proactive questions or performs explicitly approved actions.')
table(doc,['Decision','Required implementation'],[
['Multi device first','Phone, camera glasses, audio/speaker board, and integrations authenticate independently. No source is assumed to be the sole truth.'],
['Supabase as system of record','Supabase Postgres stores identities, sources, context records, events, permissions, actions, and audit trails. Supabase Storage stores media objects.'],
['Continuous capture not continuous interruption','Capture may be continuous. AI must filter, fuse, and index continuously, but may interrupt only after policy approval.'],
['Evidence first','Every fact, reminder, proactive prompt, and agent answer must retain links to the exact source records.'],
['User control wins','Hardware pause, visible status, retention controls, deletion, export, and consent settings override all automation.'],
['Proactivity is policy controlled','A model drafts questions; deterministic policy decides whether a question may be shown or spoken.']
],[1.55,5.2])
heading(doc,'2 Target Architecture')
para(doc,'The system is event driven. Sources publish immutable observations. Workers enrich those observations. A fusion service builds unified events. The agent retrieves events and facts through scoped tools. The mobile app is the primary control plane and the main live location source.')
table(doc,['Layer','Modules','Responsibility'],[
['Wearables','XIAO camera, Xiaozhi speaker, physical controls','Capture media, display capture state, buffer briefly, and transport encrypted packets.'],
['Android app','Device gateway, location, notifications, CalendarContract adapter, local encrypted cache','Pairs devices, supplies live phone context, handles permissions, shows and speaks assistant output.'],
['Ingestion','API gateway, device authentication, schema validation, object upload, queue publisher','Accepts all sources without waiting for AI inference.'],
['Understanding','ASR, OCR, frame filter, vision, MiniCPM o worker, embedding workers','Converts raw data into timestamped observations, transcripts, embeddings, and structured candidates.'],
['Memory','Supabase Postgres, Supabase Storage, pgvector','Stores raw-source references, context, fused events, graph facts, permissions, and audit logs.'],
['Intelligence','Fusion service, retrieval service, proactivity policy, agent orchestrator','Creates event narratives, retrieves evidence, decides interruptions, proposes or performs actions.'],
['Experience','Android app, later web/caregiver portal','Asking, timeline, review/delete/export, settings, device status, and approved sharing.']
],[1.15,2.25,3.35])
heading(doc,'3 Source and Context Data Model')
para(doc,'Every source emits a versioned envelope. Context records are stored even when they do not become a memory event. This preserves complete temporal context while allowing retention rules to delete raw media later.')
code(doc,'ContextEnvelope v1: source_id, device_id, user_id derived server side, sequence_no, occurred_at, received_at, type, payload, accuracy, privacy_level, signature')
table(doc,['Source','Typical records','Storage destination','Cadence'],[
['Nothing Phone 2a Plus','GPS, speed, heading, activity, notification metadata, device state, app state','context_records','Adaptive: movement or meaningful change; not fixed high frequency indoors'],
['XIAO ESP32S3 Sense','JPEG frames, short video chunks, microphone PCM or encoded chunks, camera state','media_assets plus Storage; derived observations','Continuous/adaptive stream'],
['Xiaozhi N16R8 speaker board','Playback state, acknowledgement, volume, button events','context_records and device_events','On change'],
['Calendar and integrations','Calendar event snapshot, task, contact reference, OAuth connection state','integration_connections and integration_records','Initial sync plus delta sync'],
['Agent and app','User command, notification interaction, confirmation, pause, delete, action result','agent_actions and audit_log','Every action']
],[1.35,2.3,2.05,1.05])
para(doc,'Required timestamps: occurred_at is source event time; received_at is server receipt time; created_at is database insertion time. Never use a single global latest location cache. Fusion always selects the nearest valid time aligned location sample and retains its source ID and accuracy.')
heading(doc,'4 Continuous Processing and State Flow')
table(doc,['State','Entry condition','Work','Exit'],[
['Privacy paused','Hardware switch or app pause','No capture or upload. Record only local state change.','User resumes capture.'],
['Always sensing','Authorized stream active','Receive encrypted media and context; append source records.','Chunk/event arrives, offline, or pause.'],
['Fast detection','Audio or visual chunk arrives','Voice activity, wake word, blur/duplicate, motion, scene change, safety cue.','Discard, live conversation, or enrich.'],
['Event enrichment','Meaningful source region identified','Streaming ASR, OCR, visual observations, embeddings, context lookup.','Fusion candidate created.'],
['Memory fusion','Evidence overlaps in time','Group source records; create/extend memory event and fact candidates.','Index and evaluate proactivity.'],
['Proactivity evaluation','New event or timed trigger','Apply preferences, confidence, urgency, quiet modes, interruption budget.','Ask now, notify later, or store quietly.'],
['Live conversation','Wake word/button/user command','Realtime voice session; retrieve scoped context; agent/tool calls.','Response ends, user interrupts, or pause.'],
['Offline buffering','Connection unavailable','Encrypted local queue; monotonic sequencing; later sync.','Authenticated reconnection.']
],[1.45,1.55,2.95,1.15])
heading(doc,'5 Model and Worker Plan')
para(doc,'Do not use one model for every frame and audio sample. MiniCPM o is the candidate real time multimodal interaction layer. It is not the database and it is not the policy engine. Deploy it behind an evaluation gate for latency, license, language, reliability, and interruption behavior.')
table(doc,['Function','Worker or model','Input','Output and rule'],[
['Wake and safety fast path','On phone lightweight VAD/wake/sound classifier','Raw local audio','Immediate acknowledgement; no server wait.'],
['Streaming ASR','Specialist streaming ASR worker','Short audio windows','Timestamped transcript segments and confidence.'],
['Vision filter','Lightweight CV worker','Frames','Blur score, duplicate, motion, scene-change and quality decision.'],
['OCR','OCR worker','Selected frames','Text spans, language, confidence.'],
['Visual retrieval','SigLIP embedding worker','Selected images and text queries','Embeddings for pgvector semantic search.'],
['Multimodal conversation','MiniCPM o candidate','Recent audio/video plus retrieved context','Speech/text response and structured intent candidates.'],
['Deep event summary','Multimodal worker','Fused evidence window','Event summary, entities, commitments, uncertain facts.'],
['Proactivity','Rules plus small reasoning call','Events, calendar, preferences','Candidate prompt only; cannot bypass policy.']
],[1.35,2.1,1.35,2.3])
heading(doc,'6 Supabase Database and Storage Design')
para(doc,'Supabase Postgres is canonical. All primary keys use UUID. All user owned rows carry user_id for Row Level Security. Store raw audio/video/frame bytes in Supabase Storage buckets and only store object references and hashes in Postgres. Use pgvector initially; migrate only if measured scale requires a dedicated vector service.')
table(doc,['Table','Primary key','Foreign keys and purpose'],[
['profiles','id','id -> auth.users. Timezone, consent defaults, retention settings, interruption preferences.'],
['devices','id','user_id -> profiles. Device identity, public key, type, firmware, last seen.'],
['data_streams','id','device_id -> devices; user_id -> profiles. One logical live source stream.'],
['context_records','id','user_id, device_id, stream_id. Location, notification, motion, app/device state, integration context.'],
['media_assets','id','user_id, device_id, stream_id. Storage path, checksum, media interval, retention.'],
['memory_events','id','user_id, optional session_id. Unified real world event with start/end and summary.'],
['event_sources','composite','event_id + source_type + source_id. Evidence link without data duplication.'],
['transcript_segments','id','event_id optional, media_asset_id. Timestamped text, speaker label, confidence.'],
['visual_observations','id','event_id optional, media_asset_id. OCR, scene, object/face refs, confidence.'],
['embeddings','id','user_id, event_id, source ref. Modality, model, vector.'],
['facts','id','event_id. Structured assertions, confidence, source evidence, user confirmation.'],
['integration_connections','id','user_id. Provider, encrypted secret reference, scopes, status.'],
['integration_records','id','connection_id. Calendar/tasks notification context snapshots.'],
['proactive_candidates','id','user_id, event_id. Prompt, reason, policy outcome, response.'],
['agent_actions','id','user_id, event_id optional. Proposed/confirmed/executed action and result.'],
['audit_log','id','user_id. Immutable access/action/delete/export trail.']
],[1.45,1.1,4.55])
heading(doc,'7 Keys Constraints Indexes and Data Integrity')
bullets(doc,[
'Use UUID v7 or server generated UUID primary keys. The authenticated backend derives user_id from the token/device binding; clients never select another user_id.',
'Use foreign keys with restrictive deletion for evidence and events. Use soft deletion and retention jobs for user content. Do not cascade delete a source record if an audit record needs to remain.',
'Use composite uniqueness: devices(user_id, device_public_key), data_streams(device_id, sequence namespace), media_assets(storage_bucket, storage_path), embeddings(event_id, modality, model_name).',
'Use indexes: context_records(user_id, occurred_at DESC); memory_events(user_id, started_at DESC); transcript_segments(event_id, start_ms); media_assets(stream_id, occurred_at); proactive_candidates(user_id, status, priority DESC).',
'Use partial indexes for pending work and HNSW vector indexes partitioned/scoped by user_id. Partition high volume context_records and audit_log monthly after volume warrants it.',
'Store payloads in JSONB only for evolving source-specific detail. Promote query-critical values such as location, occurred_at, event_type, state, and confidence to typed columns.'
])
heading(doc,'8 Android Application')
para(doc,'The Android app is both user experience and edge gateway. Target Nothing Phone 2a Plus on Android 14. It owns runtime permission UX, Android foreground-service lifecycle, secure device pairing, live location, local encrypted buffering, notification context, and CalendarContract synchronization.')
table(doc,['Android module','Responsibility'],[
['app shell','Jetpack Compose UI, onboarding, authentication, profile, timeline, Ask screen, privacy, devices.'],
['capture gateway','BLE/Wi-Fi pairing with devices; authenticated chunk upload; work scheduling; connection health.'],
['location service','Foreground location service with adaptive sampling; persists location records with accuracy; respects pause and system permissions.'],
['notification context','NotificationListenerService captures only metadata explicitly enabled by user: package, title, sanitized text policy, posted/dismissed/acted time. Never capture secrets/OTP/password content.'],
['calendar adapter','Reads local calendar context and writes approved events with CalendarContract.'],
['voice experience','Audio playback, captions, push-to-talk, wake/session status.'],
['secure local store','Encrypted local queue/cache, device keys, upload retry metadata; purge according to retention.'],
['sync engine','WorkManager for retryable sync; foreground service only for live capture/session work.']
],[1.5,5.6])
heading(doc,'9 Android Calendar Sync Method')
para(doc,'Implement the requested Method 1 as the default Android action path: after explicit user confirmation, the app inserts/updates a row in Android CalendarContract.Events using ContentResolver. If the selected local calendar belongs to a Google account whose Android calendar sync is enabled, Android/Google Calendar syncs the event to the cloud. This is a local-provider integration, not a direct Google API write.')
table(doc,['Step','Implementation requirement'],[
['1 Permission','Request READ_CALENDAR for context and WRITE_CALENDAR only when the user enables creation. Explain why in product UI.'],
['2 Calendar selection','List writable calendars from CalendarContract.Calendars. User explicitly selects default calendar. Do not guess Google account or calendar ID.'],
['3 Agent proposal','Agent creates a draft with title, start/end, timezone, attendees only if confirmed, and source event ID.'],
['4 Confirmation','Show/speak a concise confirmation. No automatic calendar writes from ambient conversation unless a future explicit rule authorizes it.'],
['5 Insert or update','Use ContentResolver insert/update on CalendarContract.Events. Store returned event URI/ID in agent_actions and integration_records.'],
['6 Verification','Requery local provider; show the event as created locally. Do not claim cloud sync succeeded because the app cannot guarantee account/network sync state.'],
['7 Conflict handling','If time is ambiguous or conflicts, ask user. Do not invent a duration; use a configurable default only after confirmation.']
],[1.25,5.85])
code(doc,'Calendar action ledger: agent_actions.source_event_id -> local_calendar_id -> CalendarContract event_id -> local provider URI -> action status')
heading(doc,'10 Notification Context')
para(doc,'Notification context is useful for proactivity, but it is highly sensitive. Treat it as a separately permissioned source. Capture the minimal metadata required and create per app allowlists. Never process one-time passwords, authentication notices, financial secrets, or hidden/private notification content by default.')
table(doc,['Field','Store','Use'],[
['package_name and channel','context_records payload','Identify user approved source and notification category.'],
['posted_at dismissed_at','typed columns','Timeline and reminders; not message content by itself.'],
['title and sanitized body','encrypted payload, only allowlisted apps','Context/retrieval subject to redaction and retention.'],
['user interaction','context_records','Whether user opened, dismissed, replied, or acted.'],
['agent decision','proactive_candidates/audit_log','Explain why the agent surfaced or ignored it.']
],[1.8,2.15,3.1])
heading(doc,'11 Device Implementation Contracts')
heading(doc,'11 1 XIAO ESP32S3 Sense Camera and Microphone',2)
para(doc,'Role: low-power camera/audio sensing endpoint. It captures, buffers briefly to microSD when enabled, signs and transmits packets. It must not host the complete AI model. Its 8 MB PSRAM is reserved for camera buffers and lightweight signal processing.')
table(doc,['Component','Build requirement'],[
['Board','Seeed Studio XIAO ESP32S3 Sense; ESP32 S3 dual core LX7 up to 240 MHz; 8 MB flash; 8 MB OPI PSRAM.'],
['Camera','OV2640 pins exactly as supplied: XCLK 10; SIOD 40; SIOC 39; DVP Y9 48 Y8 11 Y7 12 Y6 14 Y5 16 Y4 18 Y3 17 Y2 15; VSYNC 38; HREF 47; PCLK 13.'],
['Microphone','PDM DIN GPIO 41; PDM CLK GPIO 42. Chunk, timestamp, encode, and transmit; never block camera loop for inference.'],
['MicroSD','CS GPIO 21 shared with active-low user LED; SCK 7; MISO 8; MOSI 9. Explicitly arbitrate CS/LED behavior.'],
['Build','PlatformIO Seeed XIAO ESP32S3, Arduino, COM9, monitor 115200, upload 921600; enable BOARD_HAS_PSRAM and OPI PSRAM; default 8 MB partition plan reviewed before media buffering.'],
['Transport','Mutual device authentication, encrypted payload, sequence number, occurred_at clock, retry/backoff, offline microSD queue with bounded retention.']
],[1.35,5.75])
heading(doc,'11 2 Xiaozhi N16R8 Speaker Board',2)
para(doc,'Role: output-only assistant endpoint. It receives authenticated low-latency TTS audio or playback commands from the phone/gateway. It reports volume, playback start/end, error, button state if present, and device health. Do not make it the source of private context beyond those operational records until its exact firmware and microphone capabilities are verified.')
heading(doc,'11 3 Nothing Phone 2a Plus Android 14',2)
para(doc,'Role: primary gateway and control surface. It owns pairing, location, notifications, CalendarContract adapter, credentials, encrypted offline storage, permission UX, assistant audio, and data upload. This is the first production client; do not depend on arbitrary Wi-Fi configured directly on the glasses.')
heading(doc,'12 Security Privacy and Consent')
bullets(doc,[
'Every device has a unique credential/key pair. Device registration requires a user authenticated pairing ceremony. Revoke lost devices immediately.',
'Use TLS in transit and application-level encryption for sensitive payloads. Do not expose Supabase service-role keys to Android or hardware.',
'Enable Row Level Security on every Supabase user table. Policies restrict access to auth.uid() owned rows or explicit short-scoped grants.',
'Physical capture pause and visible indicator are mandatory. The pause state is local first and synced second.',
'Audio/video raw retention, summaries, notification content, face/person features, and caregiver sharing are independently configurable.',
'Treat medical/elder support as assistive: no diagnosis, no hidden monitoring, no autonomous emergency claim without tested and consented safety workflow.',
'Audit every data read, model inference that writes a fact, prompt shown, calendar write, integration action, export, deletion, and caregiver access.'
])
heading(doc,'13 API and Event Contracts')
table(doc,['Endpoint or channel','Caller','Purpose'],[
['POST /v1/devices/pair','Android app','Registers device public key and binds it to authenticated user.'],
['POST /v1/streams','Android/hardware','Starts a source stream and returns scoped upload credentials.'],
['POST /v1/context','Android/integration worker','Writes a validated context envelope such as location/notification/app state.'],
['POST /v1/media/init and complete','Android/hardware','Creates media asset row and direct Storage upload; confirms checksum.'],
['WebSocket /v1/live','Phone gateway','Low latency audio/video/control stream and assistant response events.'],
['POST /v1/actions/confirm','Android app','Confirms/rejects calendar, reminder, share, or other agent proposal.'],
['GET /v1/timeline and /v1/search','Android/web','Evidence scoped retrieval with pagination and RLS.'],
['Worker queue topics','Backend workers','media.ready, context.received, event.fuse, embedding.create, proactive.evaluate, action.execute.']
],[2.0,1.6,3.5])
heading(doc,'14 SDLC and Agent Swarm Delivery Plan')
para(doc,'Use vertical slices. Each slice must include schema migration, backend contract, client behavior, tests, observability, and security review. No agent may bypass the contract tables in this document.')
table(doc,['Phase','Deliverable','Definition of done'],[
['0 Architecture baseline','Repository conventions, ADRs, API schemas, threat model, Supabase project setup','Reviewed schema; RLS test harness; no production secret committed.'],
['1 Foundation','Supabase migrations, Storage buckets, Auth, device pairing, ingestion gateway, queue','Phone can write authenticated location/context and media reference; RLS tests pass.'],
['2 Android core','Compose app, login, permissions, secure cache, adaptive location, device dashboard','Android 14 app uploads location offline/online and can pause all capture.'],
['3 Media pipeline','XIAO firmware transport, Storage uploads, ASR/OCR/frame pipeline, timeline UI','Selected source data becomes traceable event with source evidence.'],
['4 Memory and search','pgvector embeddings, transcript search, evidence retrieval, delete/retention jobs','User can ask/query and inspect exact sources; deleted data cannot be retrieved.'],
['5 Proactivity','Policy engine, candidate prompts, notification context, action confirmation','All prompts logged; quiet mode/budget/consent tests pass.'],
['6 Calendar integration','CalendarContract read/context/write adapter','Confirmed event appears in local selected calendar; action ledger retained.'],
['7 Live agent','MiniCPM o evaluation, realtime session, TTS, interruption handling','Latency/reliability benchmark met; fallback path works.'],
['8 Hardening','Load, security, privacy, firmware resilience, crash recovery, monitoring','Release checklist passed; rollback and incident playbooks tested.']
],[1.1,2.3,3.7])
heading(doc,'15 Agent Ownership and Interfaces')
table(doc,['Workstream','Owns','Must not change without review'],[
['Database agent','Migrations, RLS, indexes, retention, seed/test data','Public contracts, event semantics, access model.'],
['Backend agent','Ingestion, validation, queue, workers, retrieval, policy API','Schema migrations owned by database agent.'],
['Android agent','Permissions, location, notifications, CalendarContract, UX, local cache','Server authorization rules or service keys.'],
['Firmware agent','XIAO capture/transport, offline buffering, speaker protocol','Backend semantics except versioned client contract.'],
['AI agent','ASR/OCR/vision/MiniCPM o adapters, eval harness, structured outputs','Policy rules, user permissions, direct writes without service layer.'],
['Security/QA agent','Threat model, test plans, E2E tests, performance, release gate','Feature scope or user consent behavior.']
],[1.35,2.45,3.3])
heading(doc,'16 CI CD Quality Gates')
table(doc,['Gate','Required checks'],[
['Pull request','Formatting, type checking, unit tests, database migration validation, API schema compatibility.'],
['Integration','Ephemeral Supabase project or isolated schema; RLS negative tests; Storage authorization tests; Android emulator tests.'],
['End to end','Simulated phone location + audio + video sources fuse into event; calendar confirmation flow; pause/revoke/delete flow.'],
['AI evaluation','ASR WER samples, OCR samples, retrieval grounding, false proactive rate, latency, unsafe action refusal.'],
['Security','Secret scan, dependency scan, SAST, authenticated/unauthenticated endpoint tests, RLS policy regression.'],
['Release','Migration backup/rollback tested, observability dashboards live, incident runbook, privacy checklist, staged rollout.']
],[1.25,5.85])
heading(doc,'17 Acceptance Criteria for First End to End Milestone')
bullets(doc,[
'User signs in on Android, pairs a device, and sees a controllable active/paused status.',
'Android uploads authenticated live location context with occurred_at, received_at, accuracy, device_id, and stream_id.',
'Camera/audio device uploads an independently authenticated media asset and it is stored in Supabase Storage with a Postgres reference.',
'Workers create transcript/OCR/observation records and fuse them into one memory event with event_sources evidence links.',
'User can search the timeline and inspect the exact source records behind an answer.',
'A calendar proposal requires explicit confirmation; confirmed write goes through CalendarContract and is logged.',
'Notification context follows allowlist/redaction settings and can be disabled/deleted independently.',
'Hardware/app pause stops ingestion; device revocation blocks future upload; RLS prevents cross-user access.',
'Automated tests cover all primary paths and unauthorized access attempts.'
])
heading(doc,'18 Immediate Build Sequence')
para(doc,'Start in this order: (1) create Supabase schema and RLS migrations, (2) define versioned event schemas, (3) implement Android authentication/permission/location context client, (4) implement ingestion and Storage references, (5) add XIAO source adapter, (6) add workers and fusion, (7) add timeline/search, (8) add CalendarContract confirmation workflow, and only then (9) add continuous live multimodal interaction and advanced proactivity.')
para(doc,'The agent swarm should treat privacy, evidence links, timestamps, device identity, and action confirmation as architecture invariants. These are not later polish items; they are the conditions that make an always present personal assistant trustworthy.')

# Footer
for section in doc.sections:
    p=section.footer.paragraphs[0]; p.alignment=WD_ALIGN_PARAGRAPH.CENTER; r=p.add_run('Personal AI Architecture and SDLC Blueprint'); r.font.size=Pt(8); r.font.color.rgb=RGBColor(80,80,80)
doc.save(OUT)
print(OUT.resolve())
