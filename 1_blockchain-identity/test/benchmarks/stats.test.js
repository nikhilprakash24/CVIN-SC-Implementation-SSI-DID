const { expect } = require("chai");
const { normalCdf, mannWhitneyU, percentile } = require("../../benchmarks/lib/stats");

// Review 02, H-5: normalCdf mixed two erf approximations (Φ(1.96) = 0.981).
describe("Benchmark stats library", function () {
  it("normalCdf matches standard normal reference values", function () {
    expect(normalCdf(0)).to.be.closeTo(0.5, 1e-7);
    expect(normalCdf(1)).to.be.closeTo(0.841345, 1e-4);
    expect(normalCdf(1.96)).to.be.closeTo(0.975, 1e-3);
    expect(normalCdf(1.96)).to.be.closeTo(0.9750021, 1e-5);
    expect(normalCdf(2.576)).to.be.closeTo(0.995, 1e-4);
    expect(normalCdf(-1.96)).to.be.closeTo(0.0249979, 1e-5);
  });

  it("normalCdf is symmetric and monotone", function () {
    for (const x of [0.1, 0.5, 1, 2, 3.5]) {
      expect(normalCdf(-x) + normalCdf(x)).to.be.closeTo(1, 1e-9);
      expect(normalCdf(x)).to.be.greaterThan(normalCdf(x - 0.05));
    }
  });

  it("Mann–Whitney U normal approximation gives the textbook p for full separation", function () {
    const xs = Array.from({ length: 10 }, (_, i) => i + 1);
    const ys = Array.from({ length: 10 }, (_, i) => i + 11);
    const r = mannWhitneyU(xs, ys);
    expect(r.U).to.equal(0);
    // z = (0 - 50) / sqrt(10*10*21/12) = -3.7796; p = 2(1 - Φ(3.7796)) = 1.571e-4
    expect(r.z).to.be.closeTo(-3.78, 1e-3);
    expect(r.p).to.be.closeTo(1.571e-4, 5e-6);
  });

  it("percentile interpolates linearly", function () {
    expect(percentile([1, 2, 3, 4], 0.5)).to.equal(2.5);
    expect(percentile([5], 0.95)).to.equal(5);
  });
});
