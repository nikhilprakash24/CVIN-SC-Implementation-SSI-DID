// Defence deck for the V2V identity visual layer (Phase 6, docs/visual/VISUAL_PHASES_PROMPTS.md).
//
//   node docs/visual/deck/build_deck.js ASSETS_JSON OUT_PPTX
//
// ASSETS_JSON lists each committed figure's absolute path and aspect ratio and
// the create-identity gas values read from 4_comparison-framework/results/
// gas_benchmark.json (register #25). Every data slide uses a committed figure
// PNG unchanged; the gas slide is a native chart from that file. Style:
// docs/visual/VISUAL_PLAN.md §4 (paper, ink, SSI blue, PKI ochre, one spray
// accent for alerts; stencil monospace titles, sans body).
const pptxgen = require("pptxgenjs");
const fs = require("fs");
const path = require("path");

const [, , assetsPath, outPath] = process.argv;
const A = JSON.parse(fs.readFileSync(assetsPath, "utf8"));
const SKILL = process.env.PPTX_SKILL_DIR;

const THEME = {
  name: "CVIN Academic Urban",
  headFontFace: "Courier New",
  bodyFontFace: "Arial",
  colors: {
    dk1: "0B0B0B", lt1: "FCFCFB", dk2: "52514E", lt2: "F1F0EB",
    accent1: "2A78D6", accent2: "C99228", accent3: "FF3D00",
    accent4: "898781", accent5: "D03B3B", accent6: "0CA30C",
    hlink: "2A78D6", folHlink: "52514E",
  },
};
const HEX = THEME.colors;

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.333 x 7.5 in
pres.author = "Nikhil Prakash";
pres.title = "Self-Sovereign Identity for Connected Vehicles: the V2V message path, shown";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;
const W = 13.333, H = 7.5, M = 0.6;

// ------------------------------------------------------------------ layouts
const FOOT = "CVIN-SC · V2V identity · every figure regenerates from a committed trace (docs/visual/FIGURES.md)";
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: HEX.lt1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 0.35, w: W - 2 * M, h: 0.75,
        fontSize: 32, bold: true, color: C.text1, valign: "top", margin: 0 }, text: "" } },
    { text: { text: FOOT, options: { x: M, y: H - 0.42, w: 10.5, h: 0.28, fontSize: 10, color: C.text2,
        fontFace: THEME.bodyFontFace, margin: 0 } } },
  ],
  slideNumber: { x: W - M - 0.6, y: H - 0.42, w: 0.6, h: 0.28, fontSize: 10, color: C.text2, align: "right" },
});
pres.defineSlideMaster({
  title: "DARK",
  background: { color: HEX.dk1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: M, y: 1.0, w: W - 2 * M, h: 1.9,
        fontSize: 40, bold: true, color: C.background1, valign: "top", margin: 0 }, text: "" } },
    { placeholder: { options: { name: "body", type: "body", x: M, y: 3.0, w: 9.0, h: 1.2,
        fontSize: 18, color: C.background2, valign: "top", margin: 0 }, text: "" } },
  ],
});

// ------------------------------------------------------------------ helpers
function fit(key, x, y, maxW, maxH) {
  const ar = A[key].ar;
  let w = maxW, h = maxW / ar;
  if (h > maxH) { h = maxH; w = maxH * ar; }
  return { path: A[key].path, x, y, w, h };
}
function img(slide, key, x, y, maxW, maxH, alt) {
  const f = fit(key, x, y, maxW, maxH);
  slide.addImage({ ...f, altText: alt, objectName: `fig_${key}` });
  return f;
}
function stat(slide, x, y, w, big, small, color, name) {
  slide.addText(big, { x, y, w, h: 0.95, fontSize: 48, bold: true, color, fontFace: THEME.headFontFace,
    margin: 0, isTextBox: true, objectName: `${name}_value` });
  slide.addText(small, { x, y: y + 0.95, w, h: 0.75, fontSize: 14, color: C.text2, margin: 0, valign: "top",
    isTextBox: true, objectName: `${name}_label` });
}
function para(slide, text, x, y, w, h, opts = {}) {
  slide.addText(text, { x, y, w, h, fontSize: 16, color: C.text1, margin: 0, valign: "top", isTextBox: true,
    paraSpaceAfter: 8, ...opts });
}
function stamp(slide, text, x, y, name) {
  slide.addText(text, { x, y, w: 2.3, h: 0.5, fontSize: 18, bold: true, color: C.accent3,
    fontFace: THEME.headFontFace, align: "center", valign: "middle", rotate: -6, margin: 0, isTextBox: true,
    line: { color: HEX.accent3, width: 2 }, objectName: name });
}
function road(slide, x, y, w, name) {
  // the deck's motif: three lanes with vehicles by identity layer (decorative)
  const lane = 0.32;
  for (let i = 0; i < 3; i++) {
    slide.addShape(pres.shapes.RECTANGLE, { x, y: y + i * (lane + 0.08), w, h: lane,
      fill: { color: "2A2A27" }, line: { color: "2A2A27", width: 0 }, objectName: `${name}_lane${i}` });
  }
  const cars = [[0.04, 0, 1], [0.13, 1, 0], [0.22, 2, 1], [0.31, 0, 1], [0.42, 1, 1], [0.5, 2, 0], [0.58, 0, 1],
    [0.66, 1, 1], [0.74, 2, 1], [0.83, 0, 0], [0.9, 1, 1], [0.96, 2, 1]];
  cars.forEach(([fx, ln, ssi], i) => {
    slide.addShape(pres.shapes.RECTANGLE, { x: x + fx * w, y: y + ln * (lane + 0.08) + 0.08, w: 0.42, h: 0.16,
      fill: { color: ssi ? HEX.accent1 : HEX.accent2 }, line: { color: HEX.dk1, width: 0.5 },
      objectName: `${name}_car${i}` });
  });
}

// ------------------------------------------------------------------ slides
// 1 Title
pres.addSection({ title: "Opening" });
let s = pres.addSlide({ masterName: "DARK", sectionTitle: "Opening" });
s.addText("SELF-SOVEREIGN IDENTITY FOR CONNECTED VEHICLES", { placeholder: "title" });
s.addText([
  { text: "Every V2V message signed, every receiver verifying: the identity layer, shown", options: { breakLine: true } },
  { text: "Nikhil Prakash · MASc, Electrical and Computer Engineering, UBC", options: { fontSize: 14, color: HEX.accent4 } },
], { placeholder: "body" });
road(s, M, 5.2, W - 2 * M, "motif");
s.addText("blue = SSI / MOBI VID   ochre = PKI", { x: M, y: 6.55, w: 6, h: 0.3, fontSize: 11, color: C.accent4,
  margin: 0, isTextBox: true, objectName: "motif_legend" });
s.addNotes("Title. The road at the bottom is the deck's motif: blue vehicles carry an SSI / MOBI VID identity (W3C credential, secp256k1), ochre ones a PKI pseudonym certificate (X.509, ECDSA P-256).");

// 2 Questions
pres.addSection({ title: "Questions" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Questions" });
s.addText("FOUR QUESTIONS", { placeholder: "title" });
const rq = [
  ["RQ1", "Cost", "What does a vehicle identity cost on chain, standard by standard?"],
  ["RQ2", "Security", "Which architecture rejects the V2X attacks of the threat model?"],
  ["RQ3", "Compliance", "Can a blockchain identity layer meet W3C DID and VC and MOBI VID?"],
  ["RQ4", "Real time", "Does credential verification fit the 100 ms V2V safety budget?"],
];
rq.forEach(([id, head, q], i) => {
  const cx = M + (i % 2) * 6.2, cy = 1.45 + Math.floor(i / 2) * 2.6, cw = 5.9, ch = 2.3;
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: cx, y: cy, w: cw, h: ch, rectRadius: 0.08,
    fill: { color: HEX.lt2 }, line: { color: "E1E0D9", width: 1 }, objectName: `rq${i + 1}_card` });
  s.addShape(pres.shapes.OVAL, { x: cx + 0.3, y: cy + 0.3, w: 0.8, h: 0.8,
    fill: { color: i === 3 ? HEX.accent1 : HEX.dk1 }, line: { color: HEX.dk1, width: 0 }, objectName: `rq${i + 1}_dot` });
  s.addText(id, { x: cx + 0.3, y: cy + 0.3, w: 0.8, h: 0.8, fontSize: 16, bold: true, color: C.background1,
    align: "center", valign: "middle", fontFace: THEME.headFontFace, margin: 0, isTextBox: true, objectName: `rq${i + 1}_id` });
  s.addText(head, { x: cx + 1.35, y: cy + 0.35, w: cw - 1.6, h: 0.5, fontSize: 22, bold: true, color: C.text1,
    margin: 0, isTextBox: true, objectName: `rq${i + 1}_head` });
  s.addText(q, { x: cx + 1.35, y: cy + 0.95, w: cw - 1.6, h: 1.2, fontSize: 16, color: C.text2, margin: 0,
    valign: "top", isTextBox: true, objectName: `rq${i + 1}_q` });
});
s.addNotes("RQ4 is highlighted: the rest of the deck shows the V2V message path that answers it, plus the attacks (RQ2) and the gas costs (RQ1).");

// 3 Message path
pres.addSection({ title: "The message path" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "The message path" });
s.addText("THE ROAD, 100 MS AT A TIME", { placeholder: "title" });
img(s, "f1_t0", M, 1.3, 8.4, 2.75, "Road frame at t = 0 s: first contacts, cold verifications");
img(s, "f1_t15", M, 4.15, 8.4, 2.75, "Road frame at t = 15 s: steady state, warm verifications");
para(s, [
  { text: "t = 0 s", options: { bold: true, breakLine: true } },
  { text: "Every neighbour is a first contact: links are cold, full credential verification.", options: { breakLine: true } },
  { text: "t = 15 s", options: { bold: true, breakLine: true } },
  { text: "Steady state: one signature check against a cached key per message.", options: { breakLine: true } },
  { text: "50 vehicles, 10 Hz, seed 6 of the registered N = 30 set; mock mobility, no radio channel.", options: { color: HEX.dk2, fontSize: 14 } },
], 9.3, 1.4, 3.45, 5.4);
s.addNotes("Figures V-1 and V-2 (docs/visual/FIGURES.md). Each link is a verification that ran. Command: thesis_figures.py traces/sim_50v_20s_seed6.jsonl.gz --t 0 15.");

// 4 Verify once
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "The message path" });
s.addText("VERIFY ONCE, CHECK EVERY MESSAGE", { placeholder: "title" });
img(s, "f2", M, 1.3, W - 2 * M, 4.75, "Contact matrix: one receiver's peers over time, cold at first contact then warm");
para(s, "PKI peers re-enter cold at every pseudonym-certificate rotation (every 100 messages); an SSI peer's DID binding is verified once per encounter.",
  M, 6.25, W - 2 * M, 0.7, { fontSize: 15, color: C.text2 });
s.addNotes("Figure V-5. A finding the tables did not show: the PKI design pays the full chain check again at each rotation.");

// 5 Budget
pres.addSection({ title: "Results" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Results" });
s.addText("EVERY VERIFICATION, AGAINST THE BUDGET", { placeholder: "title" });
img(s, "f3", M, 1.35, 8.6, 5.4, "All 50,818 verifications of seed 6 on a log scale against 10 ms and 100 ms");
stat(s, 9.55, 1.5, 3.2, "0.142 ms", "SSI warm verify, median of 30 run-medians (register #27)", C.accent1, "warm");
stat(s, 9.55, 3.45, 3.2, "100 ms", "SAE J2945/1-derived V2V budget", C.accent3, "budget");
para(s, "Compute latency only: no radio, MAC or channel loss is modelled.", 9.55, 5.4, 3.2, 1.0, { fontSize: 14, color: C.text2 });
s.addNotes("Figure V-6. The headline number is the result of record (#27, 0.142 ms [0.141, 0.143]); the figure illustrates one seed.");

// 6 Cold cost
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Results" });
s.addText("WHERE COLD LATENCY GOES", { placeholder: "title" });
img(s, "f8", M, 1.35, W - 2 * M, 3.3, "Median ms per stage of first-contact verification, SSI and PKI");
stat(s, M, 4.95, 3.6, "0.259 ms", "SSI credential step: W3C VC verify + DID binding", C.accent1, "ssi_cred");
stat(s, M + 4.1, 4.95, 3.6, "0.126 ms", "PKI credential step: X.509 chain + validity + CRL", C.accent2, "pki_cred");
para(s, "Measured with stage timers on, so these are proportions; results of record stay #27.", M + 8.2, 5.05, 3.9, 1.4, { fontSize: 14, color: C.text2 });
s.addNotes("Figure V-15 (F8), from the uncredentialed-rogue trace with --stage-timers.");

// 7 Attack board
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Results" });
s.addText("SEVEN ATTACKS, SEVEN REJECTIONS", { placeholder: "title" });
img(s, "f4", M, 1.3, 6.9, 5.55, "Attack board: tampered, stale, replayed and uncredentialed messages, each rejected");
para(s, [
  { text: "Injected after every run, in both populations:", options: { breakLine: true } },
  { text: "tampered, stale and replayed BSMs, and a sender with a key and a DID but no credential.", options: { breakLine: true } },
  { text: "Pass or fail is computed by the receiver's real verification path, not asserted.", options: { breakLine: true } },
  { text: "30 / 30 runs in the register.", options: { bold: true } },
], 7.9, 1.6, 4.8, 3.5);
stamp(s, "REJECTED", 8.2, 5.4, "stamp_rejected");
s.addNotes("Figure V-8. The infrastructure attacks (I2, register #45) are drawn by the trunk renderer.");

// 8 Rogue
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Results" });
s.addText("AN ATTACKER ON THE ROAD", { placeholder: "title" });
img(s, "f1_rogue", M, 1.3, 8.4, 3.15, "Road frame at t = 12 s with the rogue vehicle and its rejected links");
img(s, "f9_replay", M, 4.55, 8.4, 2.4, "Replay-mode rejections over time and the 17 accepted relays");
stat(s, 9.4, 1.45, 3.3, "617", "of 617 uncredentialed rogue messages rejected", C.text1, "uncred");
stat(s, 9.4, 3.35, 3.3, "17", "replays accepted: fresh genuine messages relayed to receivers that missed the original", C.accent3, "relay");
para(s, "Authenticity holds; reach is extended. A position-plausibility check would close it.", 9.4, 5.45, 3.3, 1.2, { fontSize: 14, color: C.text2 });
s.addNotes("Figures V-13 and V-14. Seed 6, rogue from t = 10 s. Tamper mode: 517 / 517 rejected (signature, binding). The relay limit applies to SSI and PKI alike and is proposed for docs/THREAT_MODEL.md.");

// 9 Packet
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Results" });
s.addText("ONE MESSAGE, ANATOMISED", { placeholder: "title" });
img(s, "f7", M, 1.3, W - 2 * M, 4.5, "Bytes per field of one signed SSI and one signed PKI BSM");
para(s, "The 1,408 B credential rides on every SSI message as the harness packages it, though a receiver needs it only at first contact. Compact-JSON sizes, not over-the-air ASN.1.",
  M, 6.0, W - 2 * M, 0.85, { fontSize: 15, color: C.text2 });
s.addNotes("Figure V-11 (F7), packet_anatomy.py --seed 1. A bandwidth point for chapter 6.");

// 10 Gas
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Results" });
s.addText("WHAT AN IDENTITY COSTS ON CHAIN", { placeholder: "title" });
const gas = A._gas;
s.addChart(pres.charts.BAR, [{ name: "createIdentity gas", labels: gas.map(g => g[0]), values: gas.map(g => g[1]) }], {
  x: M, y: 1.3, w: 8.6, h: 5.55, barDir: "bar", chartColors: [HEX.accent1],
  showValue: true, dataLabelPosition: "outEnd", dataLabelFormatCode: "#,##0", dataLabelFontSize: 11,
  dataLabelColor: HEX.dk2, dataLabelFontFace: "+mn-lt",
  catAxisLabelColor: HEX.dk2, catAxisLabelFontSize: 12, catAxisLabelFontFace: "+mn-lt",
  valAxisLabelColor: HEX.dk2, valAxisLabelFontSize: 11, valAxisLabelFontFace: "+mn-lt", valAxisLabelFormatCode: "#,##0",
  valGridLine: { color: "E1E0D9", size: 0.75 }, catGridLine: { style: "none" },
  showLegend: false, showTitle: true, title: "createIdentity, gas (Hardhat local, solc 0.8.24, cancun)",
  titleFontSize: 13, titleColor: HEX.dk1, titleFontFace: "+mn-lt", objectName: "gas_chart",
});
stat(s, 9.55, 1.5, 3.2, "33.7×", "spread, ERC-735 against CVIN-Combined", C.text1, "spread");
para(s, `Source: 4_comparison-framework/results/gas_benchmark.json (register #25, commit ${A._gas_meta.commit}). MOBI-VID-V2 is an application profile, not a base standard.`,
  9.55, 3.55, 3.2, 2.6, { fontSize: 13, color: C.text2 });
s.addNotes("Native chart from the results of record. The README key-results table still shows pre-2026-10-09 cells for ERC-721, ERC-735, ERC-1155, LSP8 and MOBI-VID-V2; this chart follows the results file and register #25.");

// 11 Limits
pres.addSection({ title: "Close" });
s = pres.addSlide({ masterName: "CONTENT", sectionTitle: "Close" });
s.addText("WHAT THE PICTURES MAY CLAIM", { placeholder: "title" });
const hdr = { bold: true, color: HEX.lt1, fill: { color: HEX.dk1 }, fontSize: 14 };
const rows = [
  [{ text: "In the pictures", options: hdr }, { text: "Real or mock", options: hdr }, { text: "A caption may say", options: hdr }],
  ["Signing of each BSM", "Real: ECDSA P-256 (PKI), secp256k1 EIP-191 (SSI)", "each message is actually signed"],
  ["Cold and warm verification", "Real: X.509 chain and CRL; W3C VC and signature recovery", "every link drawn is a verification that ran"],
  ["Latency on any axis", "Real: time.perf_counter around the cryptographic call", "compute latency of identity verification only"],
  ["Vehicle motion", "Mock kinematic model, or SUMO 1.28 over TraCI", "the mobility source, always"],
  ["Radio channel", "Mock: in-process delivery to the 8 nearest within 300 m", "no radio, MAC or channel loss"],
  ["The blockchain", "Not in the V2V loop: credentials verified off chain", "never a chain read per message"],
];
s.addTable(rows, { x: M, y: 1.35, w: W - 2 * M, colW: [3.0, 5.3, 3.83], fontSize: 13, color: HEX.dk1,
  fontFace: THEME.bodyFontFace, border: { type: "solid", color: "E1E0D9", pt: 0.75 }, fill: { color: HEX.lt1 },
  rowH: 0.62, valign: "middle", objectName: "claims_table" });
s.addNotes("docs/visual/VISUAL_PLAN.md §1. Every figure footer carries the mobility source, seed, commit and the radio caveat.");

// 12 Next
s = pres.addSlide({ masterName: "DARK", sectionTitle: "Close" });
s.addText("WHAT IS NEXT", { placeholder: "title" });
s.addText([
  { text: "Decide N-4: SUMO for illustrations only, or S1–S3 at N = 30 in TraCI mode", options: { bullet: true, breakLine: true } },
  { text: "State the relay limit in the threat model, with a position-plausibility check as the remedy", options: { bullet: true, breakLine: true } },
  { text: "Send the credential on first contact, not on every message, and measure the bandwidth", options: { bullet: true } },
], { x: M, y: 2.4, w: 11.5, h: 2.4, fontSize: 20, color: C.background1, margin: 0, valign: "top",
  paraSpaceAfter: 14, isTextBox: true, objectName: "next_list" });
road(s, M, 5.5, W - 2 * M, "motif_end");
s.addNotes("Decisions for the author: N-4 / P2-D4 on the decision sheet; the relay finding (Phase 5); the packet-size finding (F7).");

(async () => {
  await pres.writeFile({ fileName: outPath });
  if (SKILL) {
    const { applyTheme } = require(path.join(SKILL, "scripts", "apply_theme.js"));
    await applyTheme(outPath, THEME);
  }
  console.log("wrote", outPath);
})();
