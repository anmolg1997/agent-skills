# Failure-Mode Taxonomy

Controlled vocabulary used in `data/postmortems.json` tags, with corpus counts.

## Root-cause classes

### software-bug (84 incidents)
- `cloudflare-6`: External data feeds (like the DNS root zone) are untrusted input to your parsers, bound-check and fuzz them before a growth or format change does it for you.
- `cloudflare-7`: Treat internally generated config artifacts as untrusted input: validate size and shape before global propagation, and make consumers fail open on limit breaches.
- `firefox`: A client monoculture means one latent protocol bug plus one server-side change can brick every install at once, ship remote kill switches for risky subsystems.
- `google-8`: Individually-benign misconfigurations combine catastrophically; control-plane jobs must survive maintenance events and emergency tooling must work over a congested network.

### config-change (58 incidents)
- `allegro`: Autoscaling limits in cluster config must be load-tested, or real traffic will find the ceiling before you do.
- `amazon`: Validate configs semantically (safe minimums, invariants), not just syntactically, and make fallback defaults fail-safe rather than minimal.
- `circleci-2`: Changes made outside infrastructure-as-code are invisible to responders and poison diagnosis, enforce least-privilege IAM and continuous drift detection.
- `cloudflare`: A config rule deployed everywhere simultaneously fails everywhere simultaneously, stage and validate router config like code.

### cascading-failure (58 incidents)
- `cloudflare`: A config rule deployed everywhere simultaneously fails everywhere simultaneously, stage and validate router config like code.
- `cloudflare-7`: Treat internally generated config artifacts as untrusted input: validate size and shape before global propagation, and make consumers fail open on limit breaches.
- `datadog`: A config error in a shared discovery layer converts one component's failure into a global one, partition blast domains in foundational services.
- `facebook`: The safety tooling that audits dangerous commands is itself critical-path code, and recovery access (badges, tools, consoles) must not depend on the network being repaired.

### capacity-overload (51 incidents)
- `allegro`: Autoscaling limits in cluster config must be load-tested, or real traffic will find the ceiling before you do.
- `google-7`: A capacity-mitigation change needs its own capacity model, under overload, retries amplify the problem and cascade to every dependent service.
- `google-11`: Serialize risky upgrades away from concurrent repair work, and design QoS tiers so inevitable capacity loss lands on batch traffic instead of users.
- `google-14`: Rarely exercised code paths have unknown performance envelopes, bulk operations through them can freeze a control plane for hours.

### process-gap (49 incidents)
- `amazon`: Validate configs semantically (safe minimums, invariants), not just syntactically, and make fallback defaults fail-safe rather than minimal.
- `circleci-2`: Changes made outside infrastructure-as-code are invisible to responders and poison diagnosis, enforce least-privilege IAM and continuous drift detection.
- `cloudflare-4`: Test environments must exercise production topology (tiered/cache paths); a change can pass every test and still fail 5% of live traffic for hours.
- `enom`: Rehearse complex cutovers end-to-end with explicit go/no-go rollback criteria; extending a maintenance window repeatedly is a sign the abort path was never designed.

### database (41 incidents)
- `circleci`: Schema changes must be backwards- and forwards-compatible; once new-format rows exist, rollback is no longer a safe recovery path.
- `gocardless`: Failover configuration must be exercised under realistic combined failure modes, single-fault testing leaves the deadly combinations unproven.
- `razorpay`: Durability and replication settings must be proven in failover drills, an actual hardware failure is the worst possible moment to discover the config was wrong.
- `github-6`: Automated failover to a lagging replica trades seconds of downtime for a day of data reconciliation, failover logic must be consistency-aware, not just liveness-aware.

### dependency-failure (30 incidents)
- `datadog`: A config error in a shared discovery layer converts one component's failure into a global one, partition blast domains in foundational services.
- `firefox`: A client monoculture means one latent protocol bug plus one server-side change can brick every install at once, ship remote kill switches for risky subsystems.
- `github-3`: Automated policy enforcement needs a pre-flight impact assessment and a fast human override; your cloud provider's automation can be the root cause of your outage.
- `google-4`: Shared internal services like quota fan failure out to every consumer, dependents should degrade open (fail permissive) when a policy service is down.

### deploy-process (27 incidents)
- `circleci`: Schema changes must be backwards- and forwards-compatible; once new-format rows exist, rollback is no longer a safe recovery path.
- `cloudflare-3`: The order of operations in a network config rollout is itself a correctness property, model and verify sequences, not just end states.
- `cloudflare-5`: Shared auth/token infrastructure is a single point of failure across product lines, release changes to it with extra staging and instant rollback.
- `enom`: Rehearse complex cutovers end-to-end with explicit go/no-go rollback criteria; extending a maintenance window repeatedly is a sign the abort path was never designed.

### human-operational-error (27 incidents)
- `circleci-2`: Changes made outside infrastructure-as-code are invisible to responders and poison diagnosis, enforce least-privilege IAM and continuous drift detection.
- `cloudflare-2`: Backbone routing changes need automated review and dry-run simulation, because a one-line typo can redirect a continent's traffic to one datacenter.
- `google-5`: Validate config entries against absurd-match invariants, an entry that matches everything is almost never intended and should be rejected automatically.
- `keepthescore`: Backup frequency must match your data-loss tolerance, and destructive commands need environment-distinct credentials so 'wrong terminal' cannot reach production.

### network (21 incidents)
- `cloudflare-2`: Backbone routing changes need automated review and dry-run simulation, because a one-line typo can redirect a continent's traffic to one datacenter.
- `etsy`: Verify the network fabric's configuration supports a new traffic pattern before shipping it, switches are part of your deployment surface.
- `google-11`: Serialize risky upgrades away from concurrent repair work, and design QoS tiers so inevitable capacity loss lands on batch traffic instead of users.
- `stack-overflow`: Firewall changes deserve the same review and staged application as code, one rule can silently block all production traffic.

### hardware-failure (21 incidents)
- `razorpay`: Durability and replication settings must be proven in failover drills, an actual hardware failure is the worst possible moment to discover the config was wrong.
- `amazon-2`: Backup power has its own control-logic failure modes, test the switchover chain (PLCs, breakers), not just the generators.
- `amazon-3`: Passing periodic load tests does not guarantee performance during a real failover, validate backups under production-like load and duration.
- `amazon-4`: Protection systems tuned to expected failure signatures miss real ones, design isolation to fail safe on ambiguous signals rather than drain reserves into a dead grid.

### security (19 incidents)
- `sentry`: Backups inherit the full sensitivity of the primary data, continuously audit storage ACLs rather than trusting the setting made at creation time.
- `turso`: Multi-tenant identifiers must be provably collision-free, and a remediation for a leak must itself be verified non-destructive before it runs.
- `basecamp`: Communicate during an attack, not after; same-day transparency preserved trust through a 100-minute outage.
- `bintray`: Package repositories need namespace/identity verification, because impersonation attacks compromise every downstream build silently.

### automation-gone-wrong (17 incidents)
- `github`: Recovery and rebuild tooling must not depend on the system being recovered, a zone rebuild that needs working DNS will corrupt the zone during a DNS outage.
- `github-3`: Automated policy enforcement needs a pre-flight impact assessment and a fast human override; your cloud provider's automation can be the root cause of your outage.
- `google`: Deprecated options with destructive end-of-life behavior must be removed or loudly flagged, silent automatic deletion should never be a default anywhere.
- `google-2`: Generated network configs need invariant checks like 'never announce dramatically fewer prefixes than yesterday' before they reach routers.

### data-corruption-loss (14 incidents)
- `travisci-2`: Cleanup automation needs protection tags or allowlists for artifacts still in use, plus a dry-run mode, 'old' is not the same as 'unused'.
- `travisci-4`: Test contexts must be physically unable to reach production data, separate credentials and network paths per environment, not just different env-var values.
- `tui`: Cross-check derived safety-critical values against independent estimates, a data-mapping bug in back-office software can become a physical aviation risk.
- `turso`: Multi-tenant identifiers must be provably collision-free, and a remediation for a leak must itself be verified non-destructive before it runs.

### dns-bgp (9 incidents)
- `cloudflare-3`: The order of operations in a network config rollout is itself a correctness property, model and verify sequences, not just end states.
- `cloudflare-6`: External data feeds (like the DNS root zone) are untrusted input to your parsers, bound-check and fuzz them before a growth or format change does it for you.
- `facebook`: The safety tooling that audits dangerous commands is itself critical-path code, and recovery access (badges, tools, consoles) must not depend on the network being repaired.
- `github`: Recovery and rebuild tooling must not depend on the system being recovered, a zone rebuild that needs working DNS will corrupt the zone during a DNS outage.

### time-handling (5 incidents)
- `azure`: Never hand-roll calendar arithmetic, leap days break naive year+1 logic, and certificate-creation code turns that into a fleet-wide trust failure.
- `cloudflare-10`: Wall clocks go backwards, use monotonic clocks for durations and clamp negative deltas before they reach code that assumes non-negative time.
- `linux`: Do no side effects while holding core locks, rare-path code running in interrupt context needs the same lock discipline as hot paths, and gets far less testing.
- `linux-2`: Clock adjustments must update every derived timekeeping structure atomically, a one-second skew in timer bases melted CPU across much of the internet in 2012.

## Blast-radius vocabulary

- **partial-degradation**: 95 incidents
- **global-outage**: 59 incidents
- **prolonged-recovery**: 44 incidents
- **regional-outage**: 33 incidents
- **data-loss**: 20 incidents
- **data-leak**: 17 incidents
- **financial-loss**: 9 incidents
- **safety-incident**: 8 incidents

## Cross-category canonical patterns

- (config-errors) **Single config push with global blast radius**: One bad rule, file, or generated artifact is propagated to the entire fleet at once (no canary, no staged rollout), so validation failure anywhere becomes failure everywhere. (`cloudflare`, `cloudflare-7`, `facebook`, `facebook-2`, `microsoft`, `google-3`, `google-5`, `etsy`)
- (config-errors) **Broken or bypassed guardrail**: The audit tool, staged-rollout policy, test environment, or IAM boundary that was supposed to stop the bad change was itself buggy, bypassed, or blind, so the safety net failed exactly when needed. (`facebook`, `microsoft`, `cloudflare-4`, `circleci-2`, `pagerduty`, `amazon`)
- (config-errors) **Rollback or recovery path fails or depends on the broken system**: Reverting the change makes things worse (mixed-format data, broken rollback tooling) or recovery tooling depends on the very system that is down, extending the outage well past detection. (`circleci`, `github`, `travisci-3`, `facebook`, `turso`)
- (config-errors) **Automated or generated config without semantic validation**: Machine-generated configs, automated cleanup jobs, and auto-applied policies run unchecked against invariants (size, prefix counts, match scope, in-use status), automating the outage instead of the operations. (`google-2`, `google-3`, `cloudflare-7`, `travisci-2`, `github-3`, `heroku`, `google`)
- (config-errors) **Config change activates a latent software bug or hard limit**: The change is benign in itself but trips a dormant bug, hidden state reset, or hard-coded limit in consuming software, so the failure appears far from the change that caused it. (`cloudflare-6`, `cloudflare-7`, `firefox`, `google-8`, `google-9`, `google-10`, `npm`)
- (config-errors) **Wrong-scope settings and credential bleed**: Configuration or credentials reach the wrong environment, tenant, or physical system, test hits prod, backups leak across tenants, durability settings are wrong, a control acts on the wrong target, yielding data loss, leaks, or safety incidents rather than downtime. (`travisci-4`, `sentry`, `turso`, `keepthescore`, `razorpay`, `owasa`, `tui`)
- (hardware-power-failures) **Backup power fails at the moment of truth**: Generators, breakers, and PLCs pass routine tests but fail during a real utility-power failover, when load and switching conditions differ from the test. (`amazon-2`, `amazon-3`, `amazon-4`, `amazon-5`)
- (hardware-power-failures) **Facility control-plane failure disables cooling or power**: A bug or hang in datacenter control software (cooling controllers, automated power management) converts a recoverable event into thermal shutdown or extended power loss. (`amazon-6`, `google-13`, `amazon-5`)
- (hardware-power-failures) **Correlated failure defeats redundancy**: Nominally redundant components share a stressor (heat, storm, one facility, one provider) or a capacity ceiling, so they fail together or overload each other sequentially. (`google-13`, `amazon-5`, `cloudflare-9`)
- (hardware-power-failures) **Byzantine partial failure propagates plausible garbage**: A half-alive device (switch, IMP, alarm system) keeps emitting corrupt-but-valid-looking signals that healthy systems trust and propagate, cascading far beyond the device. (`cloudflare-8`, `arpanet`, `firstenergy-general-electric`)
- (hardware-power-failures) **Power loss surfaces persistence and durability gaps**: Extended power failure or missing error correction reveals that data believed durable (write caches, single volumes, non-ECC memory) was not. (`google-12`, `sun`, `pythonanywhere`)
- (hardware-power-failures) **HA design drift: new services never joined the redundant cluster**: The high-availability architecture was real, but services added after its design carried non-obvious dependencies on a single facility, discovered only during the outage. (`cloudflare-9`, `github-4`)
- (conflicts) **Split brain from racing coordinators**: Two redundant automation actors or leaders operate concurrently on the same state without fencing, and one destroys or contradicts the other's work. (`amazon-7`, `github-7`)
- (conflicts) **The HA machinery causes the outage**: Failover automation (STONITH, MLAG, replica promotion) reacts to a brief transient by taking destructive action that is far worse than the transient itself. (`github-5`, `github-6`)
- (conflicts) **Failover exposes weaker guarantees than steady state**: Promotion of a standby surfaces properties invisible in normal operation, lost tail writes, sequence gaps, because replicas see a different state than the primary. (`github-6`, `incident-io`)
- (conflicts) **Version and namespace collisions**: Conflicting deployed code versions, colliding filenames, or colliding hashes make two different things be treated as one, with destructive results. (`knight-capital`, `ccp-games`, `webkit-code-repository`)
- (conflicts) **Lock conflict between maintenance and live workload**: A migration or bulk change contends with running queries or slow code paths, and the queueing semantics freeze everything behind it. (`gocardless-2`, `google-14`)
- (conflicts) **Degraded capacity is a conflict, not just a failure**: After losing a component, the surviving paths must absorb the full load; connectivity survives but contention and packet loss degrade service. (`google-15`)
- (time) **Leap second violates monotonic-time assumptions**: Code assuming time never goes backwards receives a negative interval or rewound clock, producing panics, deadlocks, or spinloops in rarely exercised paths. (`cloudflare-10`, `linux`, `linux-2`)
- (time) **Rare time events execute untested privileged code**: Leap-second and edge-date handlers run once every few years, often in interrupt context or holding core locks, so bugs survive years of normal operation before firing simultaneously everywhere. (`linux`, `linux-2`, `azure`)
- (time) **Hand-rolled calendar arithmetic fails on edge dates**: Computing expiries as 'now plus N' instead of using a date library produces invalid dates on leap days, which downstream validation then rejects at scale. (`azure`)
- (time) **Certificate expiry as a scheduled global outage**: An unmonitored certificate in the trust chain expires, and everything that validates against it fails closed at the same instant across the entire fleet or user base. (`mozilla`, `azure`)
- (database) **Connection and pool exhaustion presents as diffuse slowness**: Connections, file descriptors, or pool slots run out under peak or amplified load, degrading every endpoint at once and hiding the single responsible operation. (`github-9`, `github-11`, `incident-io-2`, `github-12`)
- (database) **Schema migrations trigger novel failure modes at scale**: Routine DDL (renames, index creation) interacts with locks, replicas, or extensions in ways never seen on smaller tables, deadlocking or crashing the fleet. (`github-14`, `github-8`, `incident-io-3`)
- (database) **Integer key-space exhaustion**: An auto-increment or foreign-key column reaches its type's maximum (or a narrower referencing type overflows first), instantly breaking all writes through it. (`github-10`, `heroku-3`)
- (database) **Post-failover/upgrade database is alive but not performant**: Cutover succeeds mechanically but the new primary has cold caches, stale planner statistics, or detached replicas, so it cannot actually serve production load. (`circleci-4`, `github-8`, `github-12`)
- (database) **Saturation beyond the point of no return**: Once queues and write amplification pass the tipping point, rolling back the triggering change no longer helps; only shedding or draining load recovers the system. (`circleci-3`, `github-13`)
- (database) **Retry and cache-policy amplification**: Retry-on-timeout callers and shortened cache TTLs multiply load precisely when the database is weakest, converting a slowdown into an outage. (`github-12`, `github-13`)
- (uncategorized) **Latent bug triggered by first-time conditions**: A defect lies dormant for months until an unprecedented condition (scale threshold, rare packet signature, elapsed time, dependency loss) activates it, often simultaneously across a homogeneous fleet. Staging never reproduced the trigger because it lacked production's scale or soak time. (`amazon-11`, `amazon-17`, `amazon-18`, `appnexus`, `at-t`, `ccp-games-3`, `amazon-14`)
- (uncategorized) **Retry storm / thundering herd cascade**: A transient failure or recovery event unleashes synchronized reconnects and retries that overload a shared component (queue, database, network layer, lock service), making the overload self-sustaining and turning a blip into an hours-long outage. (`amazon-13`, `amazon-15`, `discord`, `circleci-5`, `bbc-online`, `duo`, `amazon-19`)
- (uncategorized) **Operator action with over-broad blast radius**: A human runs a legitimate command or script whose scope is wider than intended, a typo'd argument, wrong ID list, or maintenance job pointed at production, and tooling lacks guardrails (rate limits, soft delete, minimum-capacity floors) to contain it. (`amazon-8`, `amazon-10`, `amazon-12`, `atlassian`)
- (uncategorized) **Upgrade or auto-update silently changes behavior**: A routine dependency, OS, or platform upgrade changes defaults or creates version skew (JVM pool sizing, RabbitMQ ack timeout, kube-proxy iptables format, wiped network rules), and the change is undocumented or mis-documented, so it manifests only in production. (`circleci-8`, `circleci-9`, `circleci-10`, `datadog-2`, `dropbox`, `ccp-games-2`)
- (uncategorized) **Credential exposure and supply-chain compromise**: Secrets living where they should not (source repos, forgotten hosts, vendor databases) or unverified third-party artifacts give attackers a path in; the breach surface is an asset or vendor outside the primary security perimeter. (`bitly`, `browserstack`, `circleci-6`, `circleci-7`, `bintray`)
- (uncategorized) **Operator error on production data/fleets**: Fat-fingered or mis-scoped manual actions (wrong host, missing flag, wrong directory, wrong filesystem) during maintenance or incident response destroy or disable production, amplified by lax tooling validation and untested backups. (`gitlab`, `gitlab-2`, `joyent-2`, `mailgun`, `heroku-4`)
- (uncategorized) **Latent bug armed by config/policy data**: Code ships with a dormant defect that QA never exercises; a later, individually valid configuration or policy change becomes the trigger, often replicating globally faster than any rollback. (`fastly`, `google-20`, `github-16`, `heroku-5`)
- (uncategorized) **Credential and supply-chain compromise**: Leaked or stolen tokens and account credentials (npm, GitHub org, Jenkins, OAuth integrations) give attackers publish or push rights, turning one credential into an ecosystem-wide attack. (`eslint`, `gentoo`, `homebrew`, `heroku-7`)
- (uncategorized) **Database maintenance debt and hidden limits**: Known-but-deferred database ceilings, XID/ID wraparound, 32-bit id overflow, memory working sets, managed-service size caps, eventually arrive on their own schedule and fail catastrophically rather than gracefully. (`mandrill`, `joyent`, `etsy-2`, `instapaper`, `foursquare`)
- (uncategorized) **Upstream dependency cascade and recovery-induced storms**: Third-party or shared-cloud failures propagate through transitive dependencies, and the recovery phase itself (cold caches, client retries, thundering-herd restarts) triggers a second, often longer outage. (`incident-io-6`, `launchdarkly-2`, `github-18`, `google-20`, `heroku-6`)
- (uncategorized) **Retry/reconnect storms turn a blip into a cascading outage -**: Retry/reconnect storms turn a blip into a cascading outage, clients without backoff or admission control amplify the initial failure (`slack`, `slack-2`, `spotify`, `square`, `twilio`, `stackdriver`)
- (uncategorized) **Observability that depends on the failing system blinds resp**: Observability that depends on the failing system blinds responders and multiplies time-to-recover (`roblox`, `slack-2`, `north-american-electric-power-system`, `yeller`)
- (uncategorized) **Redundancy defeated by hidden shared coupling, 'independent**: Redundancy defeated by hidden shared coupling, 'independent' paths share a peering point, cluster, or vendor (`pagerduty-2`, `pagerduty-3`, `salesforce`, `zerodha-2`, `roblox`)
- (uncategorized) **Slow-burning resource/limit exhaustion (integer keys, Postgr**: Slow-burning resource/limit exhaustion (integer keys, Postgres XIDs, disk from unbounded logs, memory leaks) with a computable failure date nobody monitored (`strava`, `sentry-2`, `tarsnap`, `skyliner`, `platform-sh`)
- (uncategorized) **Routine manual operations on production without guardrails -**: Routine manual operations on production without guardrails, a repetitive task or ad-hoc DB op done wrong once takes everything down (`stripe`, `trivago`, `reddit`, `salesforce-2`)
