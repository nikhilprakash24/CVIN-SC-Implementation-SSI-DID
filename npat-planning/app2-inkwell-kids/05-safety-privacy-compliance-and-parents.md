# App 2 "Inkwell Kids": Safety, Privacy, Compliance and Parents

**Read this if...** you are responsible for making sure the kids app is lawful, passes App Review in the Kids Category, and earns parents' trust: COPPA as it actually applies to a zero-collection app, Apple's Kids Category rules by section number, third-party analytics and advertising rules, age rating, parental gate requirements, data minimization design (what is stored, where, for how long), no accounts for kids, Family Sharing and purchases, GDPR-K and the UK Children's Code for a later international launch, the privacy policy outline, the App Privacy label plan, incident response, local-only moderation of typed words, a compliance checklist mapped to features, and the parent-facing Trust page outline.

**Document status:** Draft v0.1, 2026-10-04, owner **[KIDS — Child UX & Learning Specialist, "Dr. Amara Nwosu"]** with **[QA — Quality & Release Lead, "Lena Fischer"]** and **[ARCH — Principal Architect, "Priya Raman"]**.

This is a planning document written by a product team, not legal advice. A children's privacy lawyer reviews the privacy policy, the App Privacy label and the COPPA position before submission (budgeted in doc 03, Phase 3).

---

## Table of contents

1. The compliance strategy in one sentence
2. COPPA: what it requires and how it applies to us
3. Apple App Store Review Guidelines for the Kids Category
4. Third-party analytics and advertising
5. Age rating and the Kids Category band
6. Parental gate requirements
7. Data minimization design: what is stored, where, retention
8. No accounts for kids
9. Family Sharing, purchases and monetization
10. GDPR-K and the UK Age Appropriate Design Code
11. Privacy policy outline
12. App Privacy label plan
13. Incident response
14. Content moderation of user-typed words (local-only)
15. Compliance checklist mapped to features
16. Trust page content outline
17. Team debates, decisions and open questions
18. Sources

---

## 1. The compliance strategy in one sentence

Collect nothing, transmit nothing, and make that verifiable by anyone with a network proxy.

> **[ARCH]** Most kids-app compliance work is about managing data you chose to collect. We choose not to collect. The app has no network entitlement use in v1: no analytics, no sync, no content downloads, no crash SDK, no remote configuration. Every compliance question below gets simpler because of that one architectural decision.

> **[KIDS]** It also changes the conversation with parents from "trust our policy" to "check for yourself." That is the Trust page's core claim.

---

## 2. COPPA: what it requires and how it applies to us

The Children's Online Privacy Protection Rule (16 CFR Part 312) is enforced by the FTC. The FTC's business guidance hub is https://www.ftc.gov/business-guidance/privacy-security/childrens-privacy, the FAQ is https://www.ftc.gov/business-guidance/resources/complying-coppa-frequently-asked-questions, and the six-step compliance plan is https://www.ftc.gov/business-guidance/resources/childrens-online-privacy-protection-rule-six-step-compliance-plan-your-business.

### 2.1 Does COPPA apply to us?

Yes. COPPA covers operators of online services directed to children under 13 and general-audience services with actual knowledge they collect from children. The "directed to children" test in 312.2 weighs subject matter, visual content, animated characters, child-oriented activities, music, age of models and evidence about the audience. A word game with a mascot in the Kids Category is directed to children by every factor; we do not argue otherwise and we design as a child-directed service.

### 2.2 What COPPA regulates

COPPA regulates the collection, use and disclosure of personal information from children under 13. "Personal information" is defined broadly and includes first and last name, online contact information, a persistent identifier that can be used to recognize a user over time and across different services, photos, video or audio containing a child's image or voice, geolocation, and more. Operators must post a privacy policy, give direct notice to parents, obtain verifiable parental consent before collection (with narrow exceptions), honor parental access and deletion rights, keep data secure, and retain it only as long as reasonably necessary.

### 2.3 The 2025 amendments

The FTC finalized amendments to the COPPA Rule in 2025 (published in the Federal Register April 22, 2025, effective June 23, 2025, with a compliance date of April 22, 2026 for most provisions; summaries at https://www.jonesday.com/en/insights/2025/05/ftc-finalizes-amendments-to-coppa--rule and https://www.hunton.com/privacy-and-cybersecurity-law-blog/ftc-publishes-final-coppa-rule-amendments). Key changes relevant to us: separate opt-in parental consent is required before disclosing children's personal information to third parties for targeted advertising; operators must maintain a written data retention policy and an information security program and publish the retention policy in the privacy notice; new consent methods are recognized (knowledge-based authentication, government ID matching, facial age estimation, text-plus in some cases); and the definition of personal information is expanded to cover biometric identifiers. **[KIDS]** will confirm the exact operative text against the Rule itself before legal review; the FTC's own page says to review the revised Rule for current requirements.

### 2.4 How it applies to a zero-collection app

The FTC FAQ states plainly: "You are not collecting personal information simply because your app interacts with personal information that is stored on the device and is never transmitted." Our design keeps every piece of child-related data (nickname, avatar, word history, stickers) on the device and never transmits it. Therefore:

| COPPA obligation | Our position |
|---|---|
| Privacy policy | Required anyway by Apple (5.1.4) and good practice; we publish one that says we collect nothing and explains the on-device data |
| Direct notice to parents | Not triggered by collection, but we provide the equivalent in the Trust page and the first-run parent setup |
| Verifiable parental consent | Not required because no personal information is collected. If voice input ships, on-device recognition with no audio stored or transmitted keeps us outside collection; this is the central question of the voice spike |
| Parental access and deletion | Provided on the device: the parent area shows all stored data and deletes it in one tap |
| Data retention policy | Written and published; trivially: data lives on the device until the parent deletes it or uninstalls |
| Security program | Written; on-device data is protected by iOS data protection; no servers |
| Third-party disclosure | None; no third parties receive anything |
| "Support for internal operations" exception for persistent identifiers | Not needed; we use no persistent identifiers |

Things that would change this analysis, and are therefore prohibited without a full compliance redesign: any analytics SDK, any crash SDK that sends device identifiers, iCloud sync of kid profiles, any server, any upload of typed words, any audio leaving the device, any advertising identifier use, any account.

> **[QA]** The verification method is a network audit. On a test device behind a proxy, we exercise every screen for an hour and assert zero outbound connections from the app's process other than Apple system services that the OS makes on its own. That audit runs before every release.

> **[DATA]** The one planned exception is the optional "suggest this word" feature where a parent sends a single dictionary word to us so we can consider it for the global allow-list. The payload is the word and nothing else, sent by the parent, from the gated parent area, through a mail-compose sheet so the parent sees exactly what goes out and uses their own email. No app network call. **OPEN** whether to include it in v1 at all.

**DECISION:** Zero collection in v1; network audit as a release gate; "suggest this word" is OPEN and, if included, uses a parent-initiated mail sheet rather than an app network call.

---

## 3. Apple App Store Review Guidelines for the Kids Category

Source: https://developer.apple.com/app-store/review/guidelines/ (verified 2026-10-04). Relevant sections, paraphrased closely with the key sentences quoted:

- **1.3 Kids Category.** Apps in the Kids Category "must not include links out of the app, purchasing opportunities, or other distractions to kids unless reserved for a designated area behind a parental gate." Once customers expect an app to follow Kids Category requirements, "it will need to continue to meet these guidelines in subsequent updates, even if you decide to deselect the category." Apps must comply with applicable children's privacy laws, "may not send personally identifiable information or device information to third parties," and "should not include third-party analytics or third-party advertising." In limited cases, third-party analytics may be permitted if the services do not collect or transmit the IDFA or any identifiable information about children, their location, or their devices, "including any device, network, or other information that could be used directly or combined with other information to identify users and their devices." Third-party contextual advertising may also be permitted in limited cases if the ad service has publicly documented Kids Category practices including human review of ad creatives.
- **5.1.4 Kids.** Developers must carefully review requirements under COPPA, GDPR and other laws. Apps may ask for birthdate and parental contact information "only for the purpose of complying with these statutes, but must include some useful functionality or entertainment value regardless of a person's age." Apps intended primarily for kids should not include third-party analytics or advertising; limited exceptions mirror 1.3. Apps in the Kids Category or that collect or share personal information from a minor "must include a privacy policy and must comply with all applicable children's privacy statutes." Notably: "the parental gate requirement for the Kid's Category is generally not the same as securing parental consent to collect personal data under these privacy statutes."
- **2.3.8.** Metadata must be appropriate for all audiences and adhere to a 4+ age rating. "Use of terms like 'For Kids' and 'For Children' in app metadata is reserved in the App Store for the Kids Category."
- **2.3.6.** Answer the age rating questions honestly so the app aligns with parental controls.
- **4.7.5** (age restriction mechanism for apps that contain software exceeding the app's rating) does not apply to us; we contain no such software.

Apple's Kids apps page (https://developer.apple.com/app-store/kids-apps/) adds: select an age band in App Store Connect (5 and under, 6 to 8, 9 to 11); provide parental gates for purchases, link-outs and permission requests; consider a voice prompt for pre-literate children; "Kids apps should not transmit personally identifiable information or device information to third parties, even in sections intended for adults, unless the parent explicitly consents"; advertising, if any, must be human-reviewed for age appropriateness.

> **[IOS]** The sentence about "even in sections intended for adults" is the one teams miss. Our parent area must also be free of third-party SDKs. The "Rate the app" prompt uses Apple's own StoreKit review request, which is fine; a link to the Trust page on our website is a link-out and sits behind the gate; the mail-compose sheet for support is a link-out and sits behind the gate.

**DECISION:** Kids Category, guidelines 1.3 and 5.1.4 treated as hard requirements across the whole binary including the parent area.

---

## 4. Third-party analytics and advertising

| Question | Answer |
|---|---|
| Any advertising? | No, including house ads for App 1. The Kids Category exception for contextual ads exists, and we decline it. |
| Any third-party analytics? | No. The exception exists for services that do not collect identifiers, and we decline it because verifying a vendor's behavior is harder than not having a vendor. |
| Crash reporting? | Apple's crash reports, visible in Xcode Organizer, which rely on the device owner's opt-in to share analytics with developers. No SDK. |
| Attribution or ad-network SDKs (SKAdNetwork)? | None. |
| Privacy manifest | `PrivacyInfo.xcprivacy` declares `NSPrivacyTracking` false, no tracking domains, no collected data types, and required-reason API usage (for example `UserDefaults` and file timestamp APIs) with the standard reason codes (https://developer.apple.com/documentation/bundleresources/privacy-manifest-files.md). |
| Dependency audit | The build pipeline lists every linked framework and fails if any non-Apple dynamic framework or unknown Swift package is linked. Allowed third-party packages must be source-only, offline and reviewed (for example a font or a phonetic algorithm). |

**DECISION:** No advertising, no third-party analytics, no third-party SDK with network behavior. Dependency audit in CI.

---

## 5. Age rating and the Kids Category band

Apple revised its age rating system in 2025, adding 13+, 16+ and 18+ tiers alongside 4+ and 9+, with a longer questionnaire in App Store Connect that developers had to complete by January 31, 2026 (press coverage: https://www.iphoneincanada.ca/2025/07/25/updated-app-store-age-ratings and https://www.businesstoday.in/amp/technology/news/story/apple-overhauls-app-store-age-ratings-adds-new-13-16-and-18-categories-486587-2025-07-28). We will answer the current questionnaire honestly: no violence, no mature themes, no gambling, no unrestricted web access, no user-generated content shared beyond the device, no in-app purchases in v1, no messaging. Expected result: 4+.

Kids Category band: one of 5 and under, 6 to 8, 9 to 11. Doc 01 leaves the choice OPEN between 6 to 8 (broadest parental browsing for our Sprouts and Explorers) and 9 to 11. The app's own band selector covers 5 to 13 regardless of the store band.

Note on Apple's newer age-assurance work: Apple announced a Declared Age Range API that lets apps ask a parent to share a child account's age range (not the birthdate) (https://9to5mac.com/2025/02/27/apple-age-verification-child-safety-features/). We do not need it in v1 because the parent sets the band locally; **[ARCH]** will evaluate it post-launch as an optional, parent-consented way to suggest a band, and only if it does not introduce any collection.

**DECISION:** Target 4+; band choice deferred to Phase 3; Declared Age Range API not used in v1.

---

## 6. Parental gate requirements

Requirement (Apple): a gate before link-outs, purchases and permission requests in a Kids Category app. Our implementation (doc 04 section 9): spelled-out arithmetic with rotating problems and a spoken "ask a grown-up" prompt, optional device authentication for shared devices, wrapping the entire parent area, every external link, every mail sheet, the StoreKit review request, and any system permission prompt (microphone, if voice ships).

Clarification from 5.1.4: the parental gate is not parental consent under COPPA. Our gate protects children from leaving the app or changing settings; it is not used as a consent mechanism for data collection, because there is no collection.

Gate policy details:
- The gate is re-asked after 5 minutes of inactivity in the parent area or on returning to the kid area.
- The gate never stores the answer.
- Failed attempts have no lockout (a child cannot lock a parent out) but after 3 failures the prompt reads "Still here? Ask a grown-up to help" and is spoken.
- The gate is tested against random tapping and replay (doc 03).

**DECISION:** As specified; ParentalGate package is the single implementation.

---

## 7. Data minimization design: what is stored, where, retention

| Data | Why | Where | Identifiable? | Retention | Parent control |
|---|---|---|---|---|---|
| Profile nickname | Handoff screen, Name category | On device, app container, iOS data protection | A nickname could be a real first name; it never leaves the device | Until parent deletes | View, edit, delete |
| Avatar choice | Handoff screen | On device | No | Until deleted | Edit, delete |
| Band and settings | Gameplay configuration | On device | No | Until deleted | Edit |
| Stickers, creatures, badges | Progression | On device | No | Until deleted | Delete with profile |
| Word history (valid words produced, counts, first-seen dates) | Learning signals shown to the parent; new-word celebrations | On device | Low; it is a list of dictionary words | Until deleted; parent can clear history without deleting the profile | View, clear |
| Misspelling pairs (child's attempt and corrected word), capped at 50 most recent per profile | Parent "spelled a new way" view; adaptive hint pre-fill | On device | Low | Rolling 50; cleared with history | View, clear |
| Parent-approved words | Validity for that profile | On device | No | Until deleted | View, remove |
| Safety-filter skip count | Parent visibility | On device, counter only, never the words | No | Weekly reset | View |
| Rounds played, hints used, chain bests | Parent dashboard and personal bests | On device | No | Until deleted | View, clear |
| Playtest data (notes) | Research | Off-product, pseudonymous, researcher-held | Pseudonymous | Deleted 30 days after analysis; recordings only with explicit consent | Consent form |
| Crash reports | Stability | Apple, under the device owner's opt-in | Apple's handling | Apple's retention | iOS Settings |

What is explicitly never stored: birthdates, real names as a required field, email addresses, photos, audio, location, device identifiers, advertising identifiers, contacts, any server-side record of any kind, the text of inappropriate words a child typed.

Storage technology: the shared Persistence package (SQLite or SwiftData per App 1's decision) in the app's container, protected by iOS data protection class Complete Until First User Authentication at minimum. No iCloud container entitlement in v1. Backups: the container is included in the user's own iCloud or local device backup like any app; this is the device owner's backup, not our collection, and the Trust page says so plainly.

> **[ARCH]** Excluding the kid profile store from backups would protect against one edge (a parent's backup containing a child's nickname) at the cost of the most common support request ("we got a new iPad and lost the stickers"). I recommend leaving it in the device backup and explaining it.

> **[KIDS]** Agreed, with the explanation on the Trust page. iCloud sync between devices is a different matter: that is us moving data through our own CloudKit container, and it is out for v1.

**DECISION:** Data map as tabled. Device backup included; no iCloud sync; no server.

---

## 8. No accounts for kids

There is no sign-in, no account creation, no email, no password, no Sign in with Apple, no Game Center. Profiles are local names and avatars. Reasons: COPPA (accounts collect online contact information), Apple's guidance that kids apps must include functionality regardless of age and should only collect birthdate or parental contact for compliance purposes, and simply that a word game does not need one.

The one account-like concept is the parent's App Store account, which Apple manages; purchases (if ever) and Ask to Buy flow through it without us seeing anything beyond StoreKit's transaction data.

**DECISION:** No accounts, no Game Center, no Sign in with Apple, in v1 or in any planned version of App 2.

---

## 9. Family Sharing, purchases and monetization

Options for App 2 monetization, mapped against Kids Category constraints:

| Option | Kids Category fit | Parent reaction (interviews) | Revenue | Recommendation |
|---|---|---|---|---|
| Paid up front (one price) | Best: no purchase surfaces inside the app at all | Strongly positive: "I know what I am paying" | Lower volume, no ongoing | Recommended for v1 |
| Free with one-time "Full" unlock behind the gate | Allowed with a gate; the free portion must be genuinely useful | Mixed: parents dislike children hitting a wall | Higher volume | Parallel pass for v2 if downloads are weak |
| Free with cosmetic theme packs behind the gate | Allowed with a gate | Neutral | Small | Possible later (Direction A theme pack from doc 04) |
| Subscription | Allowed with a gate | Negative for a small game | Ongoing | Rejected |
| Ads | Effectively rejected by our own refusal list | Strongly negative | | Rejected |
| Bundle with App 1 | App Store bundles are allowed; a kids app in a bundle is fine | Positive for App 1 owners | | Recommended as a cross-sell on App 1's side, not inside App 2 |

Family Sharing: paid apps can be shared with up to six family members through Family Sharing (https://support.apple.com/119854). Ask to Buy is on by default for children under 13 in a family group, so a child's download request goes to the organizer (https://support.apple.com/en-gu/105055). Both work in our favor: a parent buys once and every child's device gets the app. If a Full unlock ever exists, it must support Family Sharing for in-app purchases so siblings are not charged twice.

Children under 13 in Family Sharing have Apple accounts created and consented to by the family organizer; this is Apple's consent process for Apple's account, not ours, and does not change our zero-collection posture.

> **[JOBS]** Paid up front. One price, no surfaces, nothing to gate except settings. It is also the cleanest App Review story: "there is nothing to buy in this app."

> **[ARCH]** And no StoreKit code in v1 beyond the review request. Fewer moving parts.

**DECISION:** Paid up front for v1; Family Sharing enabled; no in-app purchases in v1. Free-with-unlock survives as a parallel pass for v2.

---

## 10. GDPR-K and the UK Age Appropriate Design Code

For a later international launch:

**GDPR Article 8** sets the digital consent age at 16 with member states allowed to lower it to 13; thresholds vary by country (13 in several, 14, 15 and 16 elsewhere; https://presencis.com/questions/gdpr-children-data-age-consent/ and the article text at https://gdpr-text.com/read/article-8/). Because we process no personal data off-device, Article 8 consent is not triggered by our v1 architecture. We still publish a GDPR-compliant privacy notice naming the controller and stating that no personal data is processed by us.

**UK Age Appropriate Design Code (Children's Code)** from the ICO applies to online services likely to be accessed by under-18s in the UK and sets 15 standards (https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/childrens-information/childrens-code-guidance-and-resources/age-appropriate-design-a-code-of-practice-for-online-services/). Mapping:

| Standard | Our position |
|---|---|
| 1 Best interests of the child | Design principles in doc 01; no engagement maximization |
| 2 Data protection impact assessments | A short DPIA is written before UK launch even though processing is nil; it documents why |
| 3 Age appropriate application | Bands and parent-set age; no age verification data collected |
| 4 Transparency | Trust page in child-readable and parent language; the data map above |
| 5 Detrimental use of data | No data use at all |
| 6 Policies and community standards | We do what the policy says; the network audit proves it |
| 7 Default settings | High privacy by default is automatic; there is nothing to turn down |
| 8 Data minimisation | The data map; nothing beyond gameplay needs |
| 9 Data sharing | None |
| 10 Geolocation | None |
| 11 Parental controls | Parent area with clear scope; the child can see that a parent area exists (the gate is visible, not hidden) |
| 12 Profiling | None |
| 13 Nudge techniques | No streaks, no timed rewards, no "are you sure you want to leave"; the refusal list in doc 01 |
| 14 Connected toys and devices | Not applicable |
| 15 Online tools | The parent area offers a clear path to delete and to contact us |

> **[KIDS]** The Children's Code is the clearest external articulation of what we already believe: standard 13 on nudges and standard 7 on defaults. Even in the US launch we meet it, which makes the UK launch a documentation exercise rather than a redesign.

**DECISION:** Design to the Children's Code from v1; write the DPIA and GDPR notice before any UK or EU launch; legal review per territory.

---

## 11. Privacy policy outline

Written in plain language, under 800 words, with a kid-readable summary at the top.

1. Who we are and how to contact us (support email; postal address as required).
2. The short version: "This app does not collect, store on our servers, or share any information about you or your child. Everything stays on your device."
3. What the app stores on your device, and why (the data map, in prose).
4. What the app never does: no accounts, no ads, no analytics, no tracking, no location, no microphone (or: microphone only if you turn on voice hints, processed on the device, never recorded).
5. Device backups: your own iCloud or computer backup may include this app's data, under Apple's terms, controlled by you.
6. Your controls: view, clear, delete, in the parent area; uninstalling removes everything.
7. Children's privacy: statement that the app is directed to children under 13, that we do not collect personal information from children, and how to contact us with questions (COPPA-aligned notice).
8. Crash reports: Apple may share crash data with us if you have opted in on your device; it does not identify your child.
9. Purchases: handled by Apple; we receive no payment details.
10. Changes to this policy and effective date; data retention statement (data lives on your device until you delete it; we hold nothing).
11. International: GDPR and UK notice sections added at launch in those territories.

---

## 12. App Privacy label plan

Apple's App Privacy details on the App Store (https://developer.apple.com/support/app-privacy-on-the-app-store/) require declaring collected data types in three groups: Data Used to Track You, Data Linked to You, Data Not Linked to You. Apple's definition of "collect" is transmitting data off the device in a way that allows access beyond the time it takes to service the request. Data processed only on device is not collected under that definition.

Plan: **"Data Not Collected"** for v1. Conditions that must hold, verified by the network audit and dependency audit: no analytics, no crash SDK (Apple's opt-in crash reporting is covered by Apple's own disclosure), no network calls, no third-party SDKs that collect. If "suggest this word" ships via mail-compose, the parent sends an email from their own account; the app collects nothing. If voice hints ship with on-device recognition and no audio leaving the device, the label remains "Data Not Collected" but the microphone usage string must be honest.

> **[QA]** The label is a legal statement by the developer. It is reviewed against the network audit at every release, and any new dependency triggers a label review.

**DECISION:** "Data Not Collected"; label review is part of the release checklist.

---

## 13. Incident response

Even a zero-collection app can have incidents: a content error (an inappropriate word in an allow-list), a safety-filter bypass, a gate bypass, a bug that transmits data unexpectedly (for example a debug flag left on), or an accessibility failure that harms a child's experience.

| Incident type | Severity | Response target | Actions |
|---|---|---|---|
| Inappropriate word discovered in an allow-list or picture hint | P1 | Hotfix build submitted within 48 hours; expedited review requested | Remove word, re-run collision audit, review the batch it came from, note in content changelog, Trust page update if a parent could have seen it |
| Parental gate bypass found | P1 | 48 hours | Fix, extend gate robustness test, review notes updated |
| Unexpected network traffic from the app | P0 | 24 hours: pull the build if needed via App Store Connect "remove from sale" while fixing | Identify the source; if any child data could have left a device, assess COPPA notification obligations with counsel; publish a plain statement on the Trust page |
| Safety filter bypass (typed text shown to another child in pass-and-play) | P2 | Next release | Extend sensitive list, add test |
| Crash cluster on a device model | P2 | Next release | Standard |
| Parent reports distress (a child upset by a failure state) | P2 | Review within one week | Audit the state against doc 02 rules |

Roles: **[QA]** owns the incident log and release actions; **[KIDS]** owns content and parent communication; **[ARCH]** owns technical root cause; **[JOBS]** approves any public statement. Parent communication channel: the support email and the Trust page's "Updates" section, written plainly, within the response target.

**DECISION:** Incident matrix as tabled; expedited review path pre-arranged knowledge in the release runbook.

---

## 14. Content moderation of user-typed words (local-only)

Design (detailed in doc 02 section 12.5):
- Validity is allow-list only; unknown words are simply "not known yet" and may be queued for parent approval on the device.
- A local sensitive list selects a flat, boring response ("Let's try a different word") for inappropriate input; the typed text is never stored, logged or transmitted; only a weekly count is shown to the parent.
- In pass-and-play, any text shown to another player (phrase categories in Explorers and Navigators, nicknames) passes the local filter before display.
- There is no reporting mechanism, no server-side moderation, no human review of what children type, because nothing is uploaded. The parent is the only moderator and has the only view, which contains no text.
- Nicknames: filtered at creation; a parent can override for their own device, with the override flagged so the nickname is never shown in nearby play if that ships.

> **[DATA]** The sensitive list must be maintained carefully: it is the only block-list in the app and it must not contain words that are legitimate kid vocabulary. It is reviewed by KIDS before every content release.

> **[KIDS]** A note on dignity: children test boundaries, and the correct response is uninteresting. We do not tell the parent what the child typed because that would turn a game into surveillance. The count is enough to prompt a conversation if a parent wants one.

**DECISION:** Local-only moderation as specified; no text of filtered input is ever stored.

---

## 15. Compliance checklist mapped to features

| Feature | Requirement | Source | Verification |
|---|---|---|---|
| Kid home and play screens | No link-outs, purchases or distractions | Guideline 1.3 | No-escape UI test |
| Parent area | Behind a parental gate; adult-level task; spoken prompt for pre-readers | 1.3; Apple Kids page | Gate robustness test; manual review |
| Trust page link, support mail, rate prompt | Behind the gate | 1.3 | UI test |
| Whole binary | No third-party analytics or advertising | 1.3, 5.1.4 | Dependency audit; network audit |
| Whole binary | No PII or device info to third parties, including adult sections | 1.3; Apple Kids page | Network audit |
| App Store metadata | Privacy policy URL; "Kids" wording only as permitted; 4+ appropriate screenshots | 5.1.4; 2.3.8 | Release checklist |
| Age rating | Honest questionnaire; 4+ | 2.3.6 | Release checklist |
| Privacy manifest | Present; no tracking; required-reason APIs declared | Apple privacy manifest docs | Build check |
| App Privacy label | "Data Not Collected" consistent with audits | Apple App Privacy details | Release checklist |
| Profiles | No accounts, no contact info, no birthdates | COPPA; 5.1.4 | Design review |
| Word history, misspellings, counters | On device only; parent view, clear, delete | COPPA FAQ (on-device data is not collected) | Network audit; parent area test |
| Safety filter | Local; nothing stored or transmitted | Design decision | Code review; test |
| Pass-and-play text | Filtered before display | Design decision | Test |
| Voice hint (if shipped) | On-device recognition; no audio stored or transmitted; microphone permission behind gate; honest usage string | COPPA (audio is personal information if collected); Apple Kids page (permissions behind gate) | Spike review; network audit |
| Nearby play (if shipped) | Only nicknames and answers over local network; no server; nicknames filtered | COPPA; design | Review before enabling |
| Purchases | None in v1; if ever, behind gate, Family Sharing enabled | 1.3; Apple Kids page | Release checklist |
| Progression | No streaks, timed rewards, currency or nudges | ICO Children's Code standard 13; FTC dark patterns report | Design review against doc 01 refusal list |
| Notifications | None | Design decision | No entitlement; no permission prompt |
| Playtests | Written parental consent, child assent, pseudonymous notes, recordings only with consent, 30-day deletion | NN/g testing with minors; research ethics | Consent forms on file |
| Privacy policy | Published; plain language; retention statement | COPPA 2025 amendments; 5.1.4 | Legal review |
| UK and EU launch | DPIA; GDPR notice; Children's Code mapping | ICO; GDPR Art. 8 | Legal review per territory |

---

## 16. Trust page content outline

The Trust page is a public web page linked from the App Store listing and from the gated parent area, and its core content is also embedded in the app for offline reading. Audience: a parent deciding in two minutes.

1. **Headline promise.** "Nothing your child types ever leaves the device. No ads. No accounts. No tracking. Check for yourself."
2. **What this app is.** Two classic word games adapted for ages 5 to 13, in three bands; a 60-second video with no implied features.
3. **What we do not do.** The refusal table from doc 01, verbatim.
4. **What the app stores on your device, and why.** The data map in parent language, with screenshots of the parent area's "What this app stores" screen.
5. **How to check.** A plain explanation that the app makes no network connections, and how a technically minded parent could verify it (for example with a network monitoring tool); an invitation to email us if they ever see otherwise.
6. **The grown-ups area and the gate.** What it is for, why the math question, how to set up profiles and bands.
7. **How we handle words.** Allow-lists, how we chose them, what happens if a child types something rude (nothing much, on purpose), how to approve a word the app does not know.
8. **How spelling is treated.** Why we accept "elefant" and always show "elephant"; what the parent view of "spelled a new way" is for; a short note on invented spelling with a link to Reading Rockets.
9. **Accessibility.** Friendlier letters, big targets, no time pressure, VoiceOver, Reduce Motion.
10. **Screen time.** A short, non-preachy note: sessions are designed to end naturally; a link to the AAP Family Media Plan (https://www.healthychildren.org/English/fmp/Pages/MediaPlan.aspx).
11. **For teachers.** The classroom preset, big-letter mode, Shared iPad notes, a printable one-pager.
12. **Compliance, plainly.** "We built to Apple's Kids Category rules and to COPPA. Here is our privacy policy. Here is what the App Privacy label says and why." Links to the official pages so parents can read the rules themselves.
13. **Updates and incidents.** A dated log of content fixes and any incident statements, kept honest even when quiet.
14. **Contact.** Support email with a stated response target; who we are, in two sentences.

> **[JOBS]** Section 5 is the one that makes this page different from every other kids-app privacy page. We are inviting an audit. If we cannot write that section with a straight face, we have not built the app we said we would.

> **[DESIGN]** The Trust page is designed in the parent area's adult language, not the kid system, and it is short enough to read on a phone in a school pickup line.

---

## 17. Team debates, decisions and open questions

### 17.1 Debate: iCloud sync of kid profiles

> **[ARCH]** Parents will ask why stickers do not follow the child from the iPad to the phone. CloudKit private database would keep the data in the family's own iCloud account, not on our servers.

> **[KIDS]** Even in a private CloudKit database, we are the operator moving a child's nickname and word history through a service we chose. That is collection in the COPPA sense and changes the privacy label, the policy and the notice obligations. For v1 the answer is no.

> **[JOBS]** No. "Everything stays on this device" is a sentence we can say. "It stays in your private iCloud, which we configure but cannot read" is a paragraph.

**DECISION:** No sync in v1. Revisit only with counsel and with the Trust page rewritten.

### 17.2 Debate: voice input

> **[IOS]** On-device speech recognition exists and needs no network. The audio is processed and discarded.

> **[KIDS]** A child's voice is personal information under COPPA if it is collected. If nothing is stored or transmitted, it is not collected. The compliance question is therefore technical: can we prove the audio never leaves the device, and can we write a microphone usage string that is honest?

> **[QA]** The network audit would cover it. The accuracy question is the bigger risk: poor recognition of young children's speech would produce frustration, which is a doc 02 failure.

**DECISION:** Phase 2 spike; ship only if on-device-only is enforced in code, the network audit stays clean, accuracy is acceptable in testing with Sprouts, and the microphone permission prompt sits behind the gate. **OPEN** pending the spike.

### 17.3 Debate: should the parent see what the child typed when the filter fires?

> **[GAME]** Some parents will want to know.

> **[KIDS]** Showing it turns the app into a monitoring tool and teaches the child that the app reports on them. A count is enough to start a conversation. The dignity of the child is a design value here.

> **[JOBS]** Count only. If a parent writes in asking for more, we have our answer ready.

**DECISION:** Count only; the text is never stored.

### 17.4 Debate: "suggest this word" to improve the global allow-list

> **[DATA]** The best source of missing words is real children. One word, sent by a parent, is low risk and high value.

> **[ARCH]** Any app network call breaks the "zero connections" audit and the label story. A mail-compose sheet from the gated parent area keeps the app at zero and lets the parent see the exact payload.

> **[KIDS]** Acceptable only as mail-compose, parent-initiated, with no profile information attached.

**DECISION:** If shipped, mail-compose only. **OPEN** whether it is worth the UI in v1.

### 17.5 Collected decisions

- Zero collection; zero network connections; network and dependency audits are release gates.
- Kids Category, 1.3 and 5.1.4 applied to the whole binary.
- No ads, no third-party analytics or SDKs with network behavior.
- Target 4+; band selection deferred to Phase 3.
- Parental gate as specified; not used as COPPA consent because there is no collection.
- Data map as tabled; device backup included; no iCloud sync; no server; no accounts.
- Paid up front; Family Sharing enabled; no IAP in v1.
- Design to the UK Children's Code from v1; DPIA and GDPR notice before international launch.
- "Data Not Collected" label with release-time review.
- Incident matrix with 24 to 48 hour targets for P0 and P1.
- Local-only moderation; filtered text never stored; count only to parents.

### 17.6 Open questions

- Voice hint spike outcome.
- "Suggest this word" inclusion in v1.
- Store band selection.
- Exact 2025 COPPA Rule text review with counsel (effective and compliance dates confirmed against the Federal Register).
- Whether to pursue a third-party kids-privacy certification (for example a COPPA Safe Harbor program) for the Trust page, weighed against cost for a zero-collection app.

---

## 18. Sources

- FTC, Children's Privacy business guidance hub: https://www.ftc.gov/business-guidance/privacy-security/childrens-privacy
- FTC, Complying with COPPA: Frequently Asked Questions: https://www.ftc.gov/business-guidance/resources/complying-coppa-frequently-asked-questions
- FTC, COPPA Six-Step Compliance Plan: https://www.ftc.gov/business-guidance/resources/childrens-online-privacy-protection-rule-six-step-compliance-plan-your-business
- FTC, COPPA Rule page: https://www.ftc.gov/enforcement/rules/rulemaking-regulatory-reform-proceedings/childrens-online-privacy-protection-rule
- 2025 COPPA amendments summaries: Jones Day https://www.jonesday.com/en/insights/2025/05/ftc-finalizes-amendments-to-coppa--rule ; Hunton https://www.hunton.com/privacy-and-cybersecurity-law-blog/ftc-publishes-final-coppa-rule-amendments
- FTC, Bringing Dark Patterns to Light (2022): https://www.ftc.gov/system/files/ftc_gov/pdf/P214800%20Dark%20Patterns%20Report%209.14.2022%20-%20FINAL.pdf
- Apple, App Store Review Guidelines (1.3, 2.3.6, 2.3.8, 4.7.5, 5.1.4): https://developer.apple.com/app-store/review/guidelines/
- Apple, Design safe and age-appropriate experiences (Kids apps): https://developer.apple.com/app-store/kids-apps/
- Apple, App privacy details on the App Store: https://developer.apple.com/support/app-privacy-on-the-app-store/
- Apple, Privacy manifest files: https://developer.apple.com/documentation/bundleresources/privacy-manifest-files.md
- Apple age rating changes 2025 (press): https://www.iphoneincanada.ca/2025/07/25/updated-app-store-age-ratings ; https://www.businesstoday.in/amp/technology/news/story/apple-overhauls-app-store-age-ratings-adds-new-13-16-and-18-categories-486587-2025-07-28
- Apple Declared Age Range API (press): https://9to5mac.com/2025/02/27/apple-age-verification-child-safety-features/
- Apple Support, Family Sharing overview for kids and teens: https://support.apple.com/119854 ; Ask to Buy: https://support.apple.com/en-gu/105055
- ICO, Age appropriate design: a code of practice for online services: https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/childrens-information/childrens-code-guidance-and-resources/age-appropriate-design-a-code-of-practice-for-online-services/
- GDPR Article 8 text: https://gdpr-text.com/read/article-8/ ; member state ages summary: https://presencis.com/questions/gdpr-children-data-age-consent/
- Kendrick, Usability Testing with Minors: 16 Tips (NN/g): https://www.nngroup.com/articles/usability-testing-minors/
- AAP Family Media Plan: https://www.healthychildren.org/English/fmp/Pages/MediaPlan.aspx
- Reading Rockets, invented spelling: https://www.readingrockets.org/topics/spelling-and-word-study/articles/invented-spelling-and-spelling-development
