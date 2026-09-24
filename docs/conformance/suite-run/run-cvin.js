// Runs the W3C DID test suites against ONLY the CVIN implementation files
// (cvin-*.json) and writes:
//   report/tmp/did-spec-test-run.latest.json   - suite-native sanitized results
//                                                (input for report/generate-report.js)
//   report/tmp/cvin-detailed-results.json      - every test with status and the
//                                                full jest failure messages
//   report/tmp/cvin-jest-output.txt            - raw jest terminal output
//
// The suite's own scripts (report/generate-test-data.js) run every registered
// implementation (~130 files); this runner passes a systemSuiteConfig that
// overrides the didMethods / resolvers lists with the CVIN entries only.
// Test code is untouched.
const fs = require('fs');
const path = require('path');
const runSuite = require('./services/runSuite');
const sanitizeAllResults = require('./services/sanitizeAllResults');
const { addDidv11Implementations } = require('./suites/utils');

// deep clone: addDidv11Implementations mutates the objects it is given
const impl = (n) => JSON.parse(JSON.stringify(require(`./suites/implementations/${n}.json`)));
const methods = ['ethr', 'mobi', 'nft'];
const didMethods = () => methods.map((m) => impl(`cvin-did-${m}`));
const resolvers = () => methods.map((m) => impl(`cvin-resolver-${m}`));

const suites = [
  { suite_name: 'did-identifier', name: 'did-identity', didMethods: didMethods() },
  { suite_name: 'did-core-properties', name: 'did-spec', didMethods: didMethods() },
  // did-production/default.js wraps its list with addDidv11Implementations
  // (runs every method twice: once as-is "(DID v1.0)", once with the @context
  // rewritten to did/v1.1 "(DID v1.1)"); replicate that here.
  { suite_name: 'did-production', name: 'did-production', didMethods: addDidv11Implementations(didMethods()) },
  { suite_name: 'did-consumption', name: 'did-consumption', didMethods: didMethods() },
  { suite_name: 'did-resolution', name: '7.1 DID Resolution', resolvers: resolvers() },
  // did-url-dereferencing: nothing registered - the project has no
  // dereference() function, so the suite is not run.
];

const tmp = path.resolve(__dirname, 'report/tmp');
fs.mkdirSync(tmp, { recursive: true });

(async () => {
  const all = [];
  const detailed = [];
  let terminal = '';
  const origWrite = process.stderr.write.bind(process.stderr);
  process.stderr.write = (chunk, ...rest) => { terminal += chunk.toString(); return origWrite(chunk, ...rest); };
  for (const s of suites) {
    const r = await runSuite(s.suite_name, s);
    const res = r.results;
    const tests = res.testResults.flatMap((f) => f.testResults);
    const summary = {
      suite: s.suite_name,
      total: res.numTotalTests, passed: res.numPassedTests, failed: res.numFailedTests,
      pending: res.numPendingTests, todo: res.numTodoTests,
      tests: tests.map((t) => ({
        ancestors: t.ancestorTitles, title: t.title, status: t.status,
        failureMessages: t.failureMessages,
      })),
    };
    detailed.push(summary);
    // the stock report generator expects ancestorTitles[0] to be "suites/<name>";
    // did-consumption's spec file does not follow that convention, so it is
    // kept in the detailed file only.
    if (s.suite_name !== 'did-consumption') all.push(r);
  }
  process.stderr.write = origWrite;
  fs.writeFileSync(`${tmp}/did-spec-test-run.latest.json`, JSON.stringify(sanitizeAllResults(all), null, 2));
  fs.writeFileSync(`${tmp}/cvin-detailed-results.json`, JSON.stringify(detailed, null, 2));
  fs.writeFileSync(`${tmp}/cvin-jest-output.txt`, terminal);
  for (const d of detailed) {
    console.log(`${d.suite}: total=${d.total} passed=${d.passed} failed=${d.failed} pending=${d.pending} todo=${d.todo}`);
  }
})();
