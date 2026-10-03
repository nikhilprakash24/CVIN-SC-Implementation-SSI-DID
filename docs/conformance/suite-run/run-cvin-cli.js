// Runs the W3C DID test suites through the suite's documented path
// (`npm test` == jest CLI, see packages/did-core-test-server/README.md), with
// each suite's default.js temporarily narrowed to the requested implementation
// files. The narrowed default.js is `require`d inside the jest test realm, so
// the suite's `toBeInfraMap` (`instanceof Object`) matcher works; passing the
// config through jest `globals` (services/runSuite.js) JSON-serialises it into
// another realm and makes every `toBeInfraMap` assertion fail on Node 22, for
// the WG example implementation as well (see W3C_DID_TEST_SUITE.md).
//
//   node run-cvin-cli.js cvin      -> CVIN implementations only
//   node run-cvin-cli.js control   -> WG example implementation only
//
// Outputs (report/tmp/):
//   <mode>-cli-<suite>.json   jest --json output (assertionResults incl. failureMessages)
//   <mode>-cli-<suite>.txt    jest verbose terminal output
// The original default.js files are restored afterwards.
const fs = require('fs');
const path = require('path');
const { spawnSync } = require('child_process');

const mode = process.argv[2] || 'cvin';
const methods = ['ethr', 'mobi', 'nft'];
const lists = {
  cvin: {
    didMethods: methods.map((m) => `cvin-did-${m}`),
    resolvers: methods.map((m) => `cvin-resolver-${m}`),
  },
  control: {
    didMethods: ['did-example-didwg'],
    resolvers: ['resolver-example-didwg'],
  },
}[mode];

const suites = [
  { dir: 'did-identifier', name: 'did-identity', key: 'didMethods' },
  { dir: 'did-core-properties', name: 'did-spec', key: 'didMethods' },
  { dir: 'did-production', name: 'did-production', key: 'didMethods', v11: true },
  { dir: 'did-consumption', name: 'did-consumption', key: 'didMethods' },
  { dir: 'did-resolution', name: '7.1 DID Resolution', key: 'resolvers' },
];

const tmp = path.resolve(__dirname, 'report/tmp');
fs.mkdirSync(tmp, { recursive: true });

const backups = [];
try {
  for (const s of suites) {
    const file = path.resolve(__dirname, `suites/${s.dir}/default.js`);
    const original = fs.readFileSync(file, 'utf8');
    backups.push([file, original]);
    const reqs = lists[s.key].map((n) => `    require('../implementations/${n}.json'),`).join('\n');
    const list = s.v11 ? `addDidv11Implementations([\n${reqs}\n  ])` : `[\n${reqs}\n  ]`;
    const header = s.v11 ? `const { addDidv11Implementations } = require("../utils");\n` : '';
    fs.writeFileSync(file, `${header}module.exports = {\n  name: '${s.name}',\n  ${s.key}: ${list},\n};\n`);
  }
  for (const s of suites) {
    const out = `${tmp}/${mode}-cli-${s.dir}.json`;
    const r = spawnSync(process.execPath, [
      path.resolve(__dirname, 'node_modules/.bin/jest'),
      `suites/${s.dir}`, '--verbose', '--json', `--outputFile=${out}`,
    ], { cwd: __dirname, encoding: 'utf8', maxBuffer: 1 << 28 });
    fs.writeFileSync(`${tmp}/${mode}-cli-${s.dir}.txt`, (r.stdout || '') + (r.stderr || ''));
    const j = JSON.parse(fs.readFileSync(out, 'utf8'));
    console.log(`${mode} ${s.dir}: total=${j.numTotalTests} passed=${j.numPassedTests} failed=${j.numFailedTests} pending=${j.numPendingTests} todo=${j.numTodoTests} (jest exit ${r.status})`);
  }
} finally {
  for (const [file, original] of backups) fs.writeFileSync(file, original);
  console.log('default.js files restored');
}
