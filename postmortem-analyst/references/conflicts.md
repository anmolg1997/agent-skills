# Conflicts — 11 postmortems

## Canonical patterns

- **Split brain from racing coordinators** — Two redundant automation actors or leaders operate concurrently on the same state without fencing, and one destroys or contradicts the other's work. (`amazon-7`, `github-7`)
- **The HA machinery causes the outage** — Failover automation (STONITH, MLAG, replica promotion) reacts to a brief transient by taking destructive action that is far worse than the transient itself. (`github-5`, `github-6`)
- **Failover exposes weaker guarantees than steady state** — Promotion of a standby surfaces properties invisible in normal operation — lost tail writes, sequence gaps — because replicas see a different state than the primary. (`github-6`, `incident-io`)
- **Version and namespace collisions** — Conflicting deployed code versions, colliding filenames, or colliding hashes make two different things be treated as one, with destructive results. (`knight-capital`, `ccp-games`, `webkit-code-repository`)
- **Lock conflict between maintenance and live workload** — A migration or bulk change contends with running queries or slow code paths, and the queueing semantics freeze everything behind it. (`gocardless-2`, `google-14`)
- **Degraded capacity is a conflict, not just a failure** — After losing a component, the surviving paths must absorb the full load; connectivity survives but contention and packet loss degrade service. (`google-15`)

## Entries

Fetch any entry's full text: `python3 scripts/pm.py fetch <id>`

### Amazon (`amazon-7`)
- tags: software-bug,automation-gone-wrong,cascading-failure | blast: regional-outage,prolonged-recovery
- A latent race condition in DynamoDB's DNS management left the regional endpoint `dynamodb.us-east-1.amazonaws.com` with an empty record. Two redundant "DNS Enactor" processes raced when one was unusually delayed; a second Enactor applied a newer plan and ran cleanup while the first overwrote the regional endpoint with a stale older plan, which the cleanup process then deleted. The DynamoDB outage cascaded into EC2 (DWFM "congestive collapse"), Network Load Balancer health-check flapping, and Lambda for ~15 hours.
- **Lesson:** Redundant automation actors need ordering and fencing guarantees — two uncoordinated enactors applying plans can delete the source of truth.
- <https://aws.amazon.com/message/101925/>

### CCP Games (`ccp-games`)
- tags: software-bug,human-operational-error | blast: data-loss
- A typo and a name conflict caused the installer to sometimes delete the *boot.ini* file on installation of an expansion for *EVE Online* - with [consequences.](https://www.youtube.com/watch?v=msXRFJ2ar_E)
- **Lesson:** Never write to paths that can collide with operating-system files — installer file operations need namespacing and real-OS testing.
- <https://community.eveonline.com/news/dev-blogs/about-the-boot.ini-issue/>

### GitHub (`github-5`)
- tags: network,automation-gone-wrong,cascading-failure | blast: global-outage,prolonged-recovery
- During an aggregation-switch ISSU upgrade, terminating an agent on one switch left the link up just long enough for the peer's MLAG failover to use the disruptive (rather than stateful) path, freezing the network for ~90 seconds. That spike caused fileserver Pacemaker/Heartbeat/DRBD pairs in different racks to exceed their heartbeats and STONITH each other, leaving many active/passive pairs with both nodes powered off; recovery required identifying the previously-active node from logs for each pair and took >5 hours.
- **Lesson:** HA automata (heartbeats, STONITH) tuned for steady state can mass-fence healthy nodes during a brief network freeze — bound their authority and rehearse pair-recovery.
- <https://github.blog/news-insights/the-library/downtime-last-saturday/>

### GitHub (`github-6`)
- tags: network,database,automation-gone-wrong | blast: prolonged-recovery,partial-degradation
- A 43 second network partition during maintenance caused MySQL master failover, but the new master didn't have several seconds of writes propogated to it because of cross-continent latency. 24+ hours of restoration work to maintain data integrity.
- **Lesson:** Automated failover to a lagging replica trades seconds of downtime for a day of data reconciliation — failover logic must be consistency-aware, not just liveness-aware.
- <https://blog.github.com/2018-10-30-oct21-post-incident-analysis/>

### GitHub (`github-7`)
- tags: automation-gone-wrong,config-change | blast: partial-degradation
- During routine ZooKeeper reprovisioning, replacement hosts were added too quickly and elected a second leader, creating two distinct ZooKeeper clusters. A Kafka broker for the background-job system connected to the new cluster and elected itself controller, so two Kafka clusters served conflicting state to clients; ~10% of background-job writes failed over 2h32m.
- **Lesson:** Membership changes to consensus systems must be serialized and quorum-verified — split brain arrives via routine reprovisioning, not just network partitions.
- <https://github.blog/news-insights/company-news/github-availability-report-october-2020/>

### GoCardless (`gocardless-2`)
- tags: database,deploy-process | blast: partial-degradation
- All queries on a critical PostgreSQL table were blocked by the combination of an extremely fast database migration and a long-running read query, causing 15 seconds of downtime.
- **Lesson:** DDL lock requests queue ahead of all new queries while waiting — run migrations with lock timeouts and retries so they yield instead of blocking the world.
- <https://gocardless.com/blog/zero-downtime-postgres-migrations-the-hard-parts/>

### Google (`google-14`)
- tags: software-bug,capacity-overload | blast: partial-degradation
- Many changes to a rarely modified load balancer were applied through a very slow code path. This froze all public addressing changes for ~2 hours.
- **Lesson:** Rarely exercised code paths have unknown performance envelopes — bulk operations through them can freeze a control plane for hours.
- <https://status.cloud.google.com/incident/compute/17003#5660850647990272>

### Google (`google-15`)
- tags: hardware-failure,network,capacity-overload | blast: partial-degradation
- A failure of a component on a fiber path from one of the central US gateway campuses in Google’s production backbone led to a decrease in available network bandwidth between the gateway and multiple edge locations, causing packet loss while the backbone automatically moved traffic onto remaining paths.
- **Lesson:** Automatic rerouting preserves connectivity but not capacity — provision for N-1 bandwidth, not just N-1 paths.
- <https://status.cloud.google.com/incidents/eo76pxZiDgWVz4z3kmUv>

### incident.io (`incident-io`)
- tags: database,software-bug | blast: partial-degradation
- Customers noticed their per-organization `INC-N` IDs jumping by exactly 32 (e.g. `#INC-7` directly to `#INC-39`) after a Postgres HA upgrade that promoted a follower to primary. Postgres's `nextval` pre-allocates `SEQ_LOG_VALS = 32` sequence values on the WAL to avoid logging every `nextval`; a follower sees the post-crash state, so when promoted the sequence jumps forward by up to 32. Fix was to replace `nextval` with a `SELECT MAX(external_id)+1` trigger.
- **Lesson:** Database sequences guarantee uniqueness, not contiguity — never build user-facing contiguous numbering directly on nextval across failovers.
- <https://incident.io/blog/one-two-skip-a-few>

### Knight Capital (`knight-capital`)
- tags: deploy-process,software-bug,human-operational-error | blast: financial-loss
- A combination of conflicting deployed versions and re-using a previously used bit caused a $460M loss. See also a [longer write-up](https://www.henricodolfing.com/2019/06/project-failure-case-study-knight-capital.html).
- **Lesson:** Reusing old feature flags plus non-atomic manual deploys is lethal — deployments must be automated, verified on every node, with a rehearsed kill switch.
- <https://dougseven.com/2014/04/17/knightmare-a-devops-cautionary-tale/>

### WebKit code repository (`webkit-code-repository`)
- tags: software-bug | blast: partial-degradation
- The WebKit repository, a Subversion repository configured to use deduplication, became unavailable after two files with the same SHA-1 hash were checked in as test data, with the intention of implementing a safety check for collisions. The two files had different md5 sums and so a checkout would fail a consistency check. For context, the first public SHA-1 hash collision had very recently been announced, with an example of two colliding files.
- **Lesson:** Any system keyed on a hash inherits that hash's collision resistance — know how your storage behaves when identifiers collide before someone makes them collide.
- <https://web.archive.org/web/20210306015541/https://digital.ai/catalyst-blog/subversion-sha1-collision-problem-statement-prevention-and-remediation-options>

