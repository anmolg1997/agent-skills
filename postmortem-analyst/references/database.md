# Database, 12 postmortems

## Canonical patterns

- **Connection and pool exhaustion presents as diffuse slowness**: Connections, file descriptors, or pool slots run out under peak or amplified load, degrading every endpoint at once and hiding the single responsible operation. (`github-9`, `github-11`, `incident-io-2`, `github-12`)
- **Schema migrations trigger novel failure modes at scale**: Routine DDL (renames, index creation) interacts with locks, replicas, or extensions in ways never seen on smaller tables, deadlocking or crashing the fleet. (`github-14`, `github-8`, `incident-io-3`)
- **Integer key-space exhaustion**: An auto-increment or foreign-key column reaches its type's maximum (or a narrower referencing type overflows first), instantly breaking all writes through it. (`github-10`, `heroku-3`)
- **Post-failover/upgrade database is alive but not performant**: Cutover succeeds mechanically but the new primary has cold caches, stale planner statistics, or detached replicas, so it cannot actually serve production load. (`circleci-4`, `github-8`, `github-12`)
- **Saturation beyond the point of no return**: Once queues and write amplification pass the tipping point, rolling back the triggering change no longer helps; only shedding or draining load recovers the system. (`circleci-3`, `github-13`)
- **Retry and cache-policy amplification**: Retry-on-timeout callers and shortened cache TTLs multiply load precisely when the database is weakest, converting a slowdown into an outage. (`github-12`, `github-13`)

## Entries

Fetch any entry's full text: `python3 scripts/pm.py fetch <id>`

### CircleCI (`circleci-3`)
- tags: capacity-overload,database,cascading-failure | blast: prolonged-recovery,partial-degradation
- At peak Wednesday-afternoon load, the primary database backed up with queued operations to the point that it stopped catching up; rolling back recent changes had no isolated effect because the queue depth had already saturated the system, and a primary failover to kill queued ops only bought temporary headroom. After the runnable-queue was drained, builds were stuck in the prior queue stage; manually promoting them flooded the next queue, and the build-scheduler's failure-mode throttles fired on what were actually normal conditions and backed off precisely when more throughput was needed. CircleCI rebuilt tooling on the fly to clear a 17-hour backlog.
- **Lesson:** Past the saturation tipping point rollbacks no longer help, shed load before the cliff, and make sure failure-mode throttles can tell a recovery surge from an attack.
- <https://status.circleci.com/incidents/8rklh3qqckp1>

### CircleCI (`circleci-4`)
- tags: deploy-process,database | blast: partial-degradation
- A blue/green upgrade of the workflows database succeeded mechanically, but the post-cutover database was running every query against disk because its statistics tables had not been updated. The team ran `ANALYZE` early in the upgrade procedure, but a second major-version upgrade in the same deployment then made those statistics stale, leaving the planner without usable indexes after the cutover. Workflows latency spiked, jobs were dropped after exhausting their 10-minute retry, and the team eventually re-promoted the old (blue) database to recover.
- **Lesson:** A database that starts is not a database that performs, re-run and verify planner statistics and cache warmth as the final gate before cutover.
- <https://discuss.circleci.com/t/post-incident-report-april-4-2025-delays-in-starting-workflows/53113>

### GitHub (`github-8`)
- tags: database,automation-gone-wrong,cascading-failure | blast: data-leak,partial-degradation
- A schema migration produced enough load that Percona Replication Manager failed the MySQL master over to a node with a cold InnoDB buffer pool, which then failed back. Disabling Pacemaker `maintenance-mode` the next day triggered a Pacemaker segfault that produced a partition; two simultaneous master elections occurred and the elected primary was the stale node, allowing 7 minutes of data drift in which 16 private repositories were briefly routed to the wrong owners.
- **Lesson:** Split brain in the failover manager is worse than the failure it manages, a stale elected master can silently serve other tenants' data.
- <https://github.blog/news-insights/the-library/github-availability-this-week/>

### GitHub (`github-9`)
- tags: config-change,capacity-overload,database | blast: partial-degradation
- The `mysql1` cluster experienced four ProxySQL meltdowns over nine days: an analytics query hitting the master instead of replicas, a planned promotion that recreated the failure, and then two load-driven incidents revealing that systemd had silently capped `LimitNOFILE` from 1,073,741,824 to 65,536 because of a kernel-level limit of 1,048,576. Total impact was 8h14m across the four incidents.
- **Lesson:** Verify effective runtime limits, not configured ones, init systems silently clamp values above kernel maxima and the truncation only shows at peak load.
- <https://github.blog/news-insights/company-news/february-service-disruptions-post-incident-analysis/>

### GitHub (`github-10`)
- tags: software-bug,database | blast: partial-degradation
- A foreign key on the scoped-tokens table hit max INT32, causing high failure rates for Actions and Pages and breaking scoped-token Git operations for 9h48m. Mitigation required a long-running schema migration to INT64. Linting that would have caught the column predated the column itself; one Action briefly received unauthorized access grants that were then revoked.
- **Lesson:** Integer-key exhaustion is a scheduled outage visible years in advance, monitor key headroom fleet-wide and apply new lint rules retroactively to columns that predate them.
- <https://github.blog/news-insights/company-news/github-availability-report-may-2021/>

### GitHub (`github-11`)
- tags: capacity-overload,database | blast: partial-degradation
- Peak-hour load on the shared `mysql1` cluster repeatedly exhausted ProxySQL connections over a week, requiring four primary failovers plus an emergency index and proactive throttling of webhooks and Actions. Memory profiling turned on to debug performance later triggered another connection failure, requiring yet another failover.
- **Lesson:** Shared mothership clusters accumulate tenants until peak load is an incident, partition workloads before hitting the ceiling, and remember debugging tools (memory profiling) add load of their own.
- <https://github.blog/2022-03-23-an-update-on-recent-service-disruptions/>

### GitHub (`github-12`)
- tags: config-change,software-bug,database | blast: partial-degradation,prolonged-recovery
- May 9: a connection-saturation config rollout to the Git database triggered a failover; the rollback then failed due to an internal infrastructure error, causing >10h of degraded pull-request/push consistency. May 10: an inefficient GitHub App permissions API endpoint with a retry-on-timeout caller produced a 7× write-latency spike on the auth-token cluster, peaking at 76% token-issuance failure. May 11: a Git database crash auto-failed-over but the read replicas weren't reattached, leaving the primary unable to serve full read load.
- **Lesson:** Retry-on-timeout callers turn one slow endpoint into a write storm, and a failover is not complete until replicas are reattached and the rollback path is proven to work.
- <https://github.blog/news-insights/company-news/addressing-githubs-recent-availability-issues/>

### GitHub (`github-13`)
- tags: capacity-overload,config-change,cascading-failure | blast: global-outage
- Two popular client apps had been quietly increasing read traffic 10×, then a Saturday change shortened a user-settings cache TTL from 12h to 2h. On Monday's peak, the combined write amplification from cache rewrites plus read load overwhelmed the core auth/user-management database cluster, cascading through every service that depends on it (github.com, API, Actions, Git over HTTPS, Copilot, etc.).
- **Lesson:** Cache-policy changes are capacity changes, model the added reads and write amplification at peak before shortening TTLs, and alert on silent client traffic growth.
- <https://github.blog/news-insights/company-news/addressing-githubs-recent-availability-issues-2/>

### GitHub (`github-14`)
- tags: database,software-bug,cascading-failure | blast: partial-degradation
- The GitHub platform encountered a novel failure mode when processing a schema migration on a large MySQL table. Schema migrations are a common task at GitHub and often take weeks to complete. The final step in a migration is to perform a rename to move the updated table into the correct place. During the final step of this migration a significant portion of our MySQL read replicas entered a semaphore deadlock. Our MySQL clusters consist of a primary node for write traffic, multiple read replicas for production traffic, and several replicas that serve internal read traffic for backup and analytics purposes. The read replicas that hit the deadlock entered a crash-recovery state causing an increased load on healthy read replicas. Due to the cascading nature of this scenario, there were not enough active read replicas to handle production requests which impacted the availability of core GitHub services.
- **Lesson:** Routine operations hit novel failure modes at sufficient scale, bound replica-loss cascades with admission control so the healthy remainder is not stampeded.
- <https://github.blog/2021-12-01-github-availability-report-november-2021/>

### Heroku (`heroku-3`)
- tags: software-bug,database | blast: global-outage
- At 15:05 UTC on June 8, 2023, a database error occurred where a foreign key used a smaller data type than the primary key that it referenced. This error caused an overflow when the primary key exceeded the allowable value, resulting in an inability to create new authorizations within Heroku. This error also prevented customers from creating new deployments. The oncall operations then triggered the Heroku API full outage.
- **Lesson:** Referencing and referenced columns must share a type, a width mismatch is a delayed-action outage that detonates exactly when the sequence crosses the smaller bound.
- <https://status.heroku.com/incidents/2558>

### incident.io (`incident-io-2`)
- tags: software-bug,capacity-overload,database | blast: partial-degradation
- Two weeks of intermittent app timeouts, with traces showing requests waiting up to 20s for a connection from Go's `database/sql` pool, but contention spread across many endpoints rather than a single slow query. After 24 deploys' worth of fixes (materialized views, indexes, lock timeouts, async Slack-webhook handling, and a custom `ngrok/sqlmw` middleware to attribute connection-pool hold time per operation), the root cause turned out to be an unnecessary transaction wrapping every Slack modal submission, many small fast transactions were in aggregate exhausting the pool.
- **Lesson:** Pool exhaustion presents as everything being slightly slow rather than one slow query, instrument which operation holds each connection and for how long, and never open transactions you don't need.
- <https://incident.io/blog/database-performance>

### incident.io (`incident-io-3`)
- tags: dependency-failure,database,deploy-process | blast: partial-degradation
- After a Postgres 17 upgrade the weekend before, PGAudit was re-enabled based on staging testing. A routine migration to create an empty table and add an index triggered a pathological interaction with PGAudit: the extension hung while holding critical locks, ignored timeout signals, and blocked other DB operations across the dashboard, mobile app, Slack app, and API. The primary was restarted to break the deadlock (~2 minutes hard outage), then PGAudit was removed entirely.
- **Lesson:** Extensions run inside your database's blast radius, revalidate each one against the new major version in production-like conditions, and prefer a fast deliberate restart over prolonged lock paralysis.
- <https://status.incident.io/incidents/01JRDFKAGE07YYDY0KZR137BX3/write-up>

