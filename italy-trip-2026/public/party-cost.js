/* ============================================================================
 * party-cost.js — turn an adventure's free-text `k` cost into a party-of-6 total
 * ----------------------------------------------------------------------------
 * The `k` field in adventures-data.js is human-written and wildly inconsistent
 * ("~€10pp", "Under-18 free · adults ~€18", "~€680-760 for 6", "varies").
 * This parses the patterns that ARE machine-readable and returns a total for
 * the whole family. Anything it cannot parse confidently returns null so the
 * page can fall back to the original string — a wrong number is worse than none.
 *
 * THE PARTY (6): Dan + Kei (always adults) · Rhys 18 · Jude 16 · Grey 12 · Keir 9
 *
 * Age rules that actually bite:
 *  - Italian STATE museums are free for under-18s of any nationality, so
 *    Jude/Grey/Keir never pay those. Rhys turns 18 on SEP 18 (leg 3), so he is
 *    free on legs 1–2 and pays from leg 3 on. That makes paying adults 2 → 3.
 *  - "under-11/under-14 free" style notes are handled per-row where stated.
 * ==========================================================================*/
(function (root) {
  var PEOPLE = 6;

  // Rhys is 17 for legs 1–2, turns 18 on Sep 18 (during leg 3) → count him
  // as paying from leg 3 onward. Conservative: never under-quote.
  function payingAdults(leg) { return (leg && leg <= 2) ? 2 : 3; }

  var CUR = { '€': '€', 'EUR': '€', '$': '$', 'USD': '$' };

  function currencyOf(s) {
    if (/EUR|€/.test(s)) return '€';
    if (/\$|USD/.test(s)) return '$';
    return '€';
  }

  // "12", "12.50", "1,200" → number
  function num(x) { return parseFloat(String(x).replace(/,/g, '')); }

  function fmt(cur, lo, hi) {
    var r = function (n) { return n % 1 ? n.toFixed(2) : String(Math.round(n)); };
    return (hi != null && hi !== lo) ? cur + r(lo) + '–' + r(hi) : cur + r(lo);
  }

  /**
   * @param {string} k     the raw cost string
   * @param {number} leg   1..7, used only for the Rhys-turns-18 rule
   * @returns {{text:string, lo:number, hi:number, cur:string, basis:string}|null}
   */
  function partyCost(k, leg) {
    if (!k) return null;
    var s = String(k).trim();
    var cur = currencyOf(s);
    var adults = payingAdults(leg);

    // ── 1. explicitly already a party total: "~€680-760 for 6", "(~€45-60/6)"
    var forSix = s.match(/(?:€|EUR|\$|USD)\s*(\d[\d.,]*)\s*(?:[-–]\s*(\d[\d.,]*)\s*)?(?:for six|for 6|\/\s*6\b)/i);
    if (forSix) {
      return { text: fmt(cur, num(forSix[1]), forSix[2] ? num(forSix[2]) : null),
               lo: num(forSix[1]), hi: forSix[2] ? num(forSix[2]) : num(forSix[1]),
               cur: cur, basis: 'quoted for 6' };
    }
    var sixParen = s.match(/\(~?\s*(?:€|EUR|\$|USD)\s*(\d[\d.,]*)(?:\s*[-–]\s*(\d[\d.,]*))?\s*for six\)/i);
    if (sixParen) {
      return { text: fmt(cur, num(sixParen[1]), sixParen[2] ? num(sixParen[2]) : null),
               lo: num(sixParen[1]), hi: sixParen[2] ? num(sixParen[2]) : num(sixParen[1]),
               cur: cur, basis: 'quoted for 6' };
    }

    // ── 2. free, with nothing else priced in the string
    if (/free/i.test(s) && !/(?:€|EUR|\$|USD)\s*\d/.test(s)) {
      return { text: 'Free', lo: 0, hi: 0, cur: cur, basis: 'free' };
    }

    // ── 3. under-18 free + an adult price → only the adults pay
    //    "Under-18 free · adults ~€18", "~€16pp · under-18 free", "~€9pp · under-18 free"
    if (/under[- ]?18[^·]*free|under[- ]?18 EU free/i.test(s)) {
      var ad = s.match(/adults?\s*~?\s*(?:€|EUR|\$|USD)\s*(\d[\d.,]*)/i)
            || s.match(/~?\s*(?:€|EUR|\$|USD)\s*(\d[\d.,]*)\s*pp/i);
      if (ad) {
        var each = num(ad[1]);
        return { text: fmt(cur, each * adults), lo: each * adults, hi: each * adults,
                 cur: cur, basis: adults + ' paying (under-18s free)' };
      }
    }

    // ── 4. explicit under-N free with an adult price → count who actually pays
    var underN = s.match(/under[- ]?(\d{1,2})s?\s*(?:free|FREE)/i);
    if (underN) {
      var cut = parseInt(underN[1], 10);
      var AGES = [40, 40, (leg && leg <= 2) ? 17 : 18, 16, 12, 9]; // Dan,Kei,Rhys,Jude,Grey,Keir
      var payers = AGES.filter(function (a) { return a >= cut; }).length;
      var ad2 = s.match(/(?:€|EUR|\$|USD)\s*(\d[\d.,]*)\s*(?:adult|pp)/i)
             || s.match(/adults?\s*~?\s*(?:€|EUR|\$|USD)\s*(\d[\d.,]*)/i);
      if (ad2) {
        var e2 = num(ad2[1]);
        return { text: fmt(cur, e2 * payers), lo: e2 * payers, hi: e2 * payers,
                 cur: cur, basis: payers + ' paying (under-' + cut + ' free)' };
      }
    }

    // ── 5. plain per-person, optionally a range: "~€10pp", "~€40–60pp", "from ~€15pp"
    var pp = s.match(/(?:€|EUR|\$|USD)\s*(\d[\d.,]*)\s*(?:[-–]\s*(?:€|EUR|\$|USD)?\s*(\d[\d.,]*)\s*)?pp/i);
    if (pp) {
      var lo = num(pp[1]) * PEOPLE;
      var hi = pp[2] ? num(pp[2]) * PEOPLE : lo;
      return { text: fmt(cur, lo, hi), lo: lo, hi: hi, cur: cur, basis: '6 × per-person' };
    }

    // ── 6. bare range/amount with no unit marker we trust → don't guess
    return null;
  }

  root.partyCost = partyCost;
  root.PARTY_SIZE = PEOPLE;
})(typeof window !== 'undefined' ? window : globalThis);
