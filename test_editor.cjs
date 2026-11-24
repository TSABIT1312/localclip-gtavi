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

// Middle-cut range validation tests
assert.equal(ctx.rangeError(0, 30, 0, 60, 10, 15), '');
assert.ok(ctx.rangeError(0, 30, 0, 60, 15, 10)); // cutEnd <= cutStart
assert.ok(ctx.rangeError(0, 30, 0, 60, -1, 10)); // cutStart < start
assert.ok(ctx.rangeError(0, 30, 0, 60, 10, 31)); // cutEnd > end
assert.ok(ctx.rangeError(0, 30, 0, 60, 0.1, 10)); // cutStart - start < 0.2

// Captions with middle-cut:
// original: [1-4] and [5-8] in source (rel 100) -> abs [101-104] and [105-108]
// If start=100, end=110, cutStart=103, cutEnd=106:
// First caption [101-104] straddles cutStart: clipped to [101-103] -> rel [1-3]
// Second caption [105-108] straddles cutEnd: clipped to [106-108], shifted by cutDur(3) -> rel [3-5]
const withCut = JSON.parse(JSON.stringify(ctx.retimeCaptions(original, 100, 100, 110, 103, 106)));
assert.deepEqual(withCut, [{start: 1, end: 3, text: 'First'}, {start: 3, end: 5, text: 'Next'}]);

// Discard caption entirely inside cut zone
const discarded = JSON.parse(JSON.stringify(ctx.retimeCaptions([{start: 4, end: 5, text: 'Inside'}], 100, 100, 110, 103, 106)));
assert.deepEqual(discarded, []);

// UI structure tests for filmstrip, waveform, badge, and toast
assert.ok(html.includes('id="toast-container"'), 'Toast container must exist');
assert.ok(html.includes('id="timeline-filmstrip"'), 'Timeline filmstrip must exist');
assert.ok(html.includes('id="timeline-waveform"'), 'Timeline waveform must exist');
assert.ok(html.includes('id="clip-track-filename"'), 'Clip track filename badge must exist');
assert.ok(html.includes('id="clip-track-duration"'), 'Clip track duration badge must exist');
assert.ok(html.includes('function notify('), 'notify function must exist');

console.log('Editor timing checks and UI elements passed');
