# Time — 5 postmortems

## Canonical patterns

- **Leap second violates monotonic-time assumptions** — Code assuming time never goes backwards receives a negative interval or rewound clock, producing panics, deadlocks, or spinloops in rarely exercised paths. (`cloudflare-10`, `linux`, `linux-2`)
- **Rare time events execute untested privileged code** — Leap-second and edge-date handlers run once every few years, often in interrupt context or holding core locks, so bugs survive years of normal operation before firing simultaneously everywhere. (`linux`, `linux-2`, `azure`)
- **Hand-rolled calendar arithmetic fails on edge dates** — Computing expiries as 'now plus N' instead of using a date library produces invalid dates on leap days, which downstream validation then rejects at scale. (`azure`)
- **Certificate expiry as a scheduled global outage** — An unmonitored certificate in the trust chain expires, and everything that validates against it fails closed at the same instant across the entire fleet or user base. (`mozilla`, `azure`)

## Entries

Fetch any entry's full text: `python3 scripts/pm.py fetch <id>`

### Azure (`azure`)
- tags: time-handling,software-bug | blast: global-outage
- Certificates that were valid for one year were created. Instead of using an appropriate library, someone wrote code that computed one year to be the current date plus one year. On February 29th 2012, this resulted in the creation of certificates with an expiration date of February 29th 2013, which were rejected because of the invalid date. This caused an Azure global outage that lasted for most of a day.
- **Lesson:** Never hand-roll calendar arithmetic — leap days break naive year+1 logic, and certificate-creation code turns that into a fleet-wide trust failure.
- <https://azure.microsoft.com/en-us/blog/summary-of-windows-azure-service-disruption-on-feb-29th-2012/>

### Cloudflare (`cloudflare-10`)
- tags: time-handling,software-bug | blast: partial-degradation
- Backwards time flow from tracking [the 27th leap second on 2016-12-31T23:59:60Z](https://hpiers.obspm.fr/iers/bul/bulc/bulletinc.52) caused the weighted round-robin selection of DNS resolvers (RRDNS) to panic and fail on some CNAME lookups. Go's `time.Now()` was incorrectly assumed to be monotonic; this injected negative values into calls to `rand.Int63n()`, which panics in that case.
- **Lesson:** Wall clocks go backwards — use monotonic clocks for durations and clamp negative deltas before they reach code that assumes non-negative time.
- <https://web.archive.org/web/20211104160742/https://blog.cloudflare.com/how-and-why-the-leap-second-affected-cloudflare-dns/>

### Linux (`linux`)
- tags: time-handling,software-bug | blast: partial-degradation
- Leap second code was called from the timer interrupt handler, which held `xtime_lock`. That code did a `printk` to log the leap second. `printk` wakes up `klogd`, which can sometimes try to get the time, which waits on `xtime_lock`, causing a deadlock.
- **Lesson:** Do no side effects while holding core locks — rare-path code running in interrupt context needs the same lock discipline as hot paths, and gets far less testing.
- <https://web.archive.org/web/20220427012208/https://lkml.org/lkml/2009/1/2/373>

### Linux (`linux-2`)
- tags: time-handling,software-bug,cascading-failure | blast: global-outage
- When a leap second occurred, `CLOCK_REALTIME` was rewound by one second. This was not done via a mechanism that would update `hrtimer base.offset`. This meant that when a timer interrupt happened, TIMER_ABSTIME CLOCK_REALTIME timers got expired one second early, including timers set for less than one second. This caused applications that used sleep for less than one second in a loop to spinwait without sleeping, causing high load on many systems. This caused a large number of web services to go down in 2012.
- **Lesson:** Clock adjustments must update every derived timekeeping structure atomically — a one-second skew in timer bases melted CPU across much of the internet in 2012.
- <https://web.archive.org/web/20220320100036/https://lkml.org/lkml/2012/7/1/203>

### Mozilla (`mozilla`)
- tags: time-handling,process-gap | blast: global-outage,data-loss
- Most Firefox add-ons stopped working around May 4th 2019 when a certificate expired. Firefox requires a valid certificate chain to prevent malware. About nine hours later, Mozilla pushed a privileged add-on that injected a valid certificate into Firefox's certificate store, creating a valid chain and unblocking add-ons. This disabled effectively all add-ons, about 15,000, and the resolution took approximately 15-21 hours for most users. Some user data was lost. Previously Mozilla [posted](https://web.archive.org/web/20250408175304/https://hacks.mozilla.org/2019/05/technical-details-on-the-recent-firefox-add-on-outage/) about the technical details.
- **Lesson:** Inventory and alarm on every certificate expiry in the chain, and keep an emergency delivery channel that does not depend on the system the expiry just broke.
- <https://web.archive.org/web/20250303152906/https://hacks.mozilla.org/2019/07/add-ons-outage-post-mortem-result/>

