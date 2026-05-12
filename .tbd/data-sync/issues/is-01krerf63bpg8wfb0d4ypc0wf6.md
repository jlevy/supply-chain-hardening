---
type: is
id: is-01krerf63bpg8wfb0d4ypc0wf6
title: Verify all Go incident rows in compromised-packages.md
kind: task
status: closed
priority: 1
version: 3
labels:
  - validation
  - go
dependencies: []
created_at: 2026-05-12T18:51:26.186Z
updated_at: 2026-05-12T18:58:05.141Z
closed_at: 2026-05-12T18:58:05.140Z
close_reason: "Verified all 5 Go incident rows. BoltDB (2021-11..2025-02, v1.3.1, RCE backdoor): confirmed via Socket. hypert/layout (2025-01..02, 7 modules, RCE loader): confirmed via Socket. Fake x/crypto (2025-02, Rekoobe): confirmed via Socket. Disk-wiper (2025-05, 3 modules): confirmed via Socket/BleepingComputer. Fixed qmgo date from 2025-05 to 2025-06 per GitLab timeline (reported June 1, second variant June 5)."
---
For each Go row: BoltDB typosquat (2021-11..2025-02), hypert/layout typosquats (2025-01..02), Fake x/crypto Rekoobe (2025-02), disk-wiper modules (2025-05), MongoDB qmgo typosquat (2025-05). Verify dates, module paths, scale, vector, references. Use Go security advisories + Socket + GitLab.
