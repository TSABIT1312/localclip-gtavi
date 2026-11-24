// Run: node test_editor.cjs
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const html = fs.readFileSync('index.html', 'utf8');
const helpers = html.match(/\/\/ TIMING_HELPERS_START([\s\S]*?)\/\/ TIMING_HELPERS_END/);
assert.ok(helpers, 'Timing helpers must exist');
const ctx = vm.createContext({});
vm.runInContext(helpers[1], ctx);
assert.equal(ctx.parseTime('02:15.5'), 135.5);
assert.equal(ctx.parseTime('01:02:03'), 3723);
assert.equal(ctx.parseTime('9.25'), 9.25);
for (const value of ['', '-1', '1:60', '1:2:3:4', 'Infinity', 'a', '1:99:00']) {
  assert.ok(Number.isNaN(ctx.parseTime(value)), value);
}
assert.equal(ctx.timecode(135.5), '02:15.500');
assert.equal(ctx.timecode(3599.9999), '01:00:00.000');
const original = [{start: 1, end: 4, text: 'First'}, {start: 5, end: 8, text: 'Next'}];
const rebased = JSON.parse(JSON.stringify(ctx.retimeCaptions(original, 100, 102, 106)));
assert.deepEqual(rebased, [{start: 0, end: 2, text: 'First'}, {start: 3, end: 4, text: 'Next'}]);
assert.deepEqual(JSON.parse(JSON.stringify(ctx.retimeCaptions(original, 100, 109, 111))), []);
assert.equal(original[0].start, 1);
assert.equal(ctx.rangeError(0, 1, 0, 60), '');
assert.ok(ctx.rangeError(0, 61, 0, 100));
assert.ok(ctx.rangeError(4, 3, 0, 100));
assert.ok(ctx.rangeError(NaN, 5, 0, 100));
assert.ok(ctx.rangeError(0, 4, 1, 10));
console.log('Editor timing checks passed');
