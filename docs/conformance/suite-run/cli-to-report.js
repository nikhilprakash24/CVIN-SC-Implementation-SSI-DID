// Convert jest --json outputs of run-cvin-cli.js into the sanitized format that
// report/generate-report.js expects (same shape as services/sanitizeAllResults.js).
const fs = require('fs');
const out = [];
for (const s of ['did-identifier', 'did-core-properties', 'did-production', 'did-resolution']) {
  const j = JSON.parse(fs.readFileSync(`report/tmp/cvin-cli-${s}.json`, 'utf8'));
  const tests = j.testResults.flatMap((f) => f.assertionResults);
  out.push({ suite: tests[0].ancestorTitles[0],
    testResults: tests.map((t) => ({ ancestors: t.ancestorTitles, title: t.title, status: t.status })) });
}
out.sort((a, b) => JSON.stringify(a).localeCompare(JSON.stringify(b)));
fs.writeFileSync('report/tmp/did-spec-test-run.latest.json', JSON.stringify(out, null, 2));
console.log('suites:', out.map((o) => `${o.suite}(${o.testResults.length})`).join(', '));
