"""Unit + property tests for the geometry-angles oracle (v1.0.0).

Covers the diagram-specific guarantees that the cross-language parity fixtures cannot:
committed-direction-table accuracy, the integer round-half-up rule, exact isosceles
legs, the non-blocking +/-0.5 deg to-scale diagnostic (the ONLY atan2 use here),
label-box <-> rendered-text agreement and non-overlap, monochrome output, and the
no-leakage / no-theorem-reveal invariants.

Run:  python oracle/tests/test_geometry.py
"""

import math
import os
import re
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))

from spi_oracle import geometry as geo                      # noqa: E402
from spi_oracle.geometry_misconceptions import MISCONCEPTIONS  # noqa: E402

PLACEHOLDER = re.compile(r"(?<![A-Za-z])[pqrtk](?![A-Za-z])")
TEXT_RE = re.compile(r'<text([^>]*)>([^<]*)</text>')


def parse_texts(svg):
    out = []
    for attrs, content in TEXT_RE.findall(svg):
        if 'class="gn"' in attrs:
            continue  # NOT TO SCALE caption (structural)
        x = int(re.search(r'x="(-?\d+)"', attrs).group(1))
        y = int(re.search(r'y="(-?\d+)"', attrs).group(1))
        anc = re.search(r'text-anchor="(\w+)"', attrs)
        out.append((x, y, anc.group(1) if anc else "start", content))
    return out


class TestDirTable(unittest.TestCase):
    def test_committed_table_matches_trig_within_tolerance(self):
        # The committed integer table reproduces cos/sin within the documented audit
        # tolerance. (atan2/trig appear ONLY in this audit, never in generation.)
        worst = 0.0
        for deg in range(360):
            dx, dy = geo.DIR[deg]
            ang = math.degrees(math.atan2(dy, dx)) % 360
            worst = max(worst, min(abs(ang - deg), 360 - abs(ang - deg)))
        self.assertLessEqual(worst, 0.05, f"worst direction error {worst:.4f} deg")

    def test_cardinals_are_exact(self):
        self.assertEqual(geo.DIR[0], [geo.R, 0])
        self.assertEqual(geo.DIR[90], [0, geo.R])
        self.assertEqual(geo.DIR[180], [-geo.R, 0])
        self.assertEqual(geo.DIR[270], [0, -geo.R])

    def test_grid_round_is_round_half_up(self):
        self.assertEqual(geo.grid_round(5, 2), 3)      # 2.5 -> 3
        self.assertEqual(geo.grid_round(-5, 2), -2)    # -2.5 -> -2 (half up toward +inf)
        self.assertEqual(geo.grid_round(7, 2), 4)      # 3.5 -> 4
        self.assertEqual(geo.grid_round(4, 2), 2)      # exact
        self.assertEqual(geo.grid_round(-7, 3), -2)    # -2.333 -> -2


class TestSolve(unittest.TestCase):
    def test_closure_answers(self):
        self.assertEqual(geo.solve({"task": "triangle_missing_angle", "A": 50, "B": 60}), 70)
        self.assertEqual(geo.solve({"task": "isosceles_base_angle", "apex": 40}), 70)
        self.assertEqual(geo.solve({"task": "vertically_opposite_angle", "theta": 115}), 115)
        self.assertEqual(geo.solve({"task": "straight_line_missing_angle", "regions": [40, 60, 80], "unknownIndex": 2}), 80)
        self.assertEqual(geo.solve({"task": "angles_at_point_missing", "regions": [120, 90, 150], "unknownIndex": 1}), 90)


class TestIsoscelesExactLegs(unittest.TestCase):
    def test_equal_legs_have_exactly_equal_squared_length(self):
        # Constructed symmetrically: the two equal sides must be EXACTLY equal in the
        # integer FigureModel (not merely close), so the tick marks are truthful.
        for apex in range(20, 161, 2):
            fig = geo._build_figure({"task": "isosceles_base_angle", "apex": apex})
            L, Rr, P = fig["points"]["L"], fig["points"]["R"], fig["points"]["P"]
            lp2 = (P[0] - L[0]) ** 2 + (P[1] - L[1]) ** 2
            rp2 = (P[0] - Rr[0]) ** 2 + (P[1] - Rr[1]) ** 2
            self.assertEqual(lp2, rp2, f"apex {apex}: legs {lp2} vs {rp2}")


class TestToScaleDiagnostic(unittest.TestCase):
    """Non-blocking: the rendered rays are within +/-0.5 deg of the intended angles.

    This is a *diagnostic*, not a generation/validation gate; it uses atan2 to recover
    drawn directions from the final SVG and confirms the integer pipeline stays visually
    faithful even though it never calls trig at runtime.
    """

    def _drawn_angle_at_O(self, svg, ox, oy):
        # angle of each segment endpoint away from the origin O, in degrees (y down -> up)
        out = []
        for m in re.finditer(r'<line class="gl" x1="(-?\d+)" y1="(-?\d+)" x2="(-?\d+)" y2="(-?\d+)"', svg):
            x1, y1, x2, y2 = map(int, m.groups())
            for (px, py) in ((x1, y1), (x2, y2)):
                if (px, py) != (ox, oy):
                    out.append(math.degrees(math.atan2(-(py - oy), px - ox)) % 360)
        return out

    def test_vertically_opposite_rays_match_within_half_degree(self):
        worst = 0.0
        for s in range(1, 600):
            item = geo.generate(s, {"task": "vertically_opposite_angle", "interactionType": "free-response"})
            theta = item["params"]["theta"]
            svg = item["media"][0]["svg"]
            o = re.search(r'class="gl" x1="(-?\d+)" y1="(-?\d+)" x2="(-?\d+)" y2="(-?\d+)"', svg)
            # O is the shared crossing point: recompute from the figure (origin maps via layout)
            P = geo._layout(geo._build_figure(item["params"])["points"])
            ox, oy = P["O"]
            drawn = self._drawn_angle_at_O(svg, ox, oy)
            for target in (0.0, 180.0, float(theta), float((theta + 180) % 360)):
                nearest = min(drawn, key=lambda a: min(abs(a - target), 360 - abs(a - target)))
                err = min(abs(nearest - target), 360 - abs(nearest - target))
                worst = max(worst, err)
        self.assertLessEqual(worst, 0.5, f"worst drawn-ray error {worst:.3f} deg")


class TestLabels(unittest.TestCase):
    def test_label_boxes_match_rendered_text_and_never_overlap(self):
        for s in range(1, 500):
            for mode in ("free-response", "multiple-choice"):
                item = geo.generate(s, {"interactionType": mode})
                svg = item["media"][0]["svg"]
                fig = geo._build_figure(item["params"])
                P = geo._layout(fig["points"])
                # the internal positions equal what is actually rendered as <text>
                internal = geo._text_label_positions(P, fig)
                rendered = parse_texts(svg)
                self.assertEqual(internal, rendered, f"seed {s} {mode}")
                # and the guard guarantees no overlap
                self.assertTrue(geo._labels_ok(item["params"]))

    def test_minimum_visible_region(self):
        for s in range(1, 800):
            g = geo._ctx(geo.generate(s, {"interactionType": "free-response"})["params"])
            self.assertTrue(all(v >= geo.MIN_ANGLE for v in g["givens"]))


class TestMonochromeAndNoReveal(unittest.TestCase):
    def test_no_colour_only_information(self):
        # The diagram is black-on-white; nothing carries meaning by colour alone.
        for s in range(1, 300):
            svg = geo.generate(s, {"interactionType": "multiple-choice"})["media"][0]["svg"]
            self.assertNotIn("stroke:red", svg)
            self.assertNotIn("fill:#", svg.replace("fill:#111", "").replace("fill:#444", ""))
            # only the two documented near-black inks appear
            for col in re.findall(r'(?:fill|stroke):(#[0-9a-fA-F]{3,6})', svg):
                self.assertIn(col, ("#111", "#444"))

    def test_vertically_opposite_has_no_equality_marks(self):
        # Must not betray the theorem: no tick/equal marks announcing the answer.
        for s in range(1, 300):
            fig = geo._build_figure(geo.generate(s, {"task": "vertically_opposite_angle", "interactionType": "free-response"})["params"])
            self.assertEqual(fig["ticks"], [])

    def test_unknown_labelled_x_only(self):
        for s in range(1, 400):
            for mode in ("free-response", "multiple-choice"):
                item = geo.generate(s, {"interactionType": mode})
                svg = item["media"][0]["svg"]
                texts = [t for (_, _, _, t) in parse_texts(svg)]
                self.assertEqual(texts.count("x"), 1, f"seed {s} {mode}")
                self.assertNotIn(item["answer"]["display"], item["accessibility"]["longDescription"])


class TestMisconceptions(unittest.TestCase):
    def test_distractors_match_rules_and_feedback_clean(self):
        for s in range(1, 400):
            item = geo.generate(s, {"interactionType": "multiple-choice"})
            ans = item["answer"]["canonical"]["num"]
            seen = {ans}
            for d in item["distractors"]:
                m = MISCONCEPTIONS[d["misconceptionId"]]
                self.assertEqual(m["wrong"](geo._ctx(item["params"])), d["value"])
                self.assertNotIn(d["value"], seen - {d["value"]})
                seen.add(d["value"])
                self.assertIsNone(PLACEHOLDER.search(m["feedback"]))
                self.assertEqual(d["rationale"], m["observableError"])


class TestValidation(unittest.TestCase):
    def test_sweep_passes(self):
        for s in range(1, 600):
            for mode in ("free-response", "multiple-choice"):
                self.assertEqual(geo.validate(geo.generate(s, {"interactionType": mode}))["status"], "pass")

    def test_tampered_svg_fails(self):
        item = geo.generate(3, {"interactionType": "free-response"})
        item["media"][0]["svg"] += "<!--x-->"
        v = geo.validate(item)
        self.assertEqual(v["status"], "fail")
        self.assertTrue(any(c["name"] == "svg-realises-data" and c["result"] == "fail" for c in v["checks"]))

    def test_tampered_answer_fails(self):
        item = geo.generate(3, {"interactionType": "multiple-choice"})
        item["answer"]["canonical"]["num"] += 1
        self.assertEqual(geo.validate(item)["status"], "fail")


def _arc_covers_sector(e1, e2, r, large, sweep, n=24):
    """Reconstruct the SVG elliptical-arc (rx=ry=r) and return the set of sampled
    points. Used as a NON-BLOCKING geometric diagnostic (atan2 here only)."""
    x1, y1 = e1
    x2, y2 = e2
    x1p = (x1 - x2) / 2.0
    y1p = (y1 - y2) / 2.0
    num = r * r * r * r - r * r * y1p * y1p - r * r * x1p * x1p
    den = r * r * y1p * y1p + r * r * x1p * x1p
    co = math.sqrt(max(num / den, 0.0))
    if large == sweep:
        co = -co
    cxp = co * (r * y1p / r)
    cyp = co * (-r * x1p / r)
    cx = cxp + (x1 + x2) / 2.0
    cy = cyp + (y1 + y2) / 2.0
    t1 = math.atan2((y1p - cyp) / r, (x1p - cxp) / r)
    t2 = math.atan2((-y1p - cyp) / r, (-x1p - cxp) / r)
    d = t2 - t1
    if sweep == 0 and d > 0:
        d -= 2 * math.pi
    if sweep == 1 and d < 0:
        d += 2 * math.pi
    return [(cx + r * math.cos(t1 + d * i / n), cy + r * math.sin(t1 + d * i / n)) for i in range(n + 1)]


class TestReflexAndArcSemantics(unittest.TestCase):
    ARC_RE = re.compile(r'<path class="ga" d="M (-?\d+) (-?\d+) A (\d+) (\d+) 0 (\d) (\d) (-?\d+) (-?\d+)"/>')

    def test_owner_cited_reflex_cases_validate(self):
        a = geo.generate(1, {"task": "angles_at_point_missing", "interactionType": "multiple-choice"})
        self.assertEqual(a["answer"]["canonical"]["num"], 263)               # reflex UNKNOWN
        self.assertEqual(geo.validate(a)["status"], "pass")
        b = geo.generate(26, {"task": "angles_at_point_missing", "interactionType": "free-response"})
        self.assertIn(248, geo._ctx(b["params"])["givens"])                  # reflex GIVEN
        self.assertEqual(geo.validate(b)["status"], "pass")

    def test_large_and_sweep_flags_match_measure_everywhere(self):
        seen_reflex = 0
        for s in range(1, 1500):
            for task in ("straight_line_missing_angle", "angles_at_point_missing"):
                it = geo.generate(s, {"task": task, "interactionType": "free-response"})
                fig = geo._build_figure(it["params"])
                arcs = self.ARC_RE.findall(it["media"][0]["svg"])
                self.assertEqual(len(arcs), len(fig["arcs"]))
                for (vn, start, measure), a in zip(fig["arcs"], arcs):
                    large, sweep = int(a[4]), int(a[5])
                    self.assertEqual(large, 1 if measure > 180 else 0, f"{task} s{s} m{measure}")
                    self.assertEqual(sweep, 0)
                    if measure > 180:
                        seen_reflex += 1
        self.assertGreater(seen_reflex, 20, "reflex regions must be exercised")

    def test_rendered_arc_geometrically_covers_its_sector(self):
        # Non-blocking diagnostic: the actual SVG arc stays within [start, start+measure]
        # and passes through the bisector — for minor AND reflex regions.
        TOL = 1.5
        for s in range(1, 400):
            it = geo.generate(s, {"interactionType": "free-response"})
            fig = geo._build_figure(it["params"])
            P = geo._layout(fig["points"])
            for (vn, start, measure) in fig["arcs"]:
                V = P[vn]
                e1 = geo._ray_at(V, start, geo.ARC_R)
                e2 = geo._ray_at(V, start + measure, geo.ARC_R)
                large = 1 if measure > 180 else 0
                rel = [(math.degrees(math.atan2(-(py - V[1]), px - V[0])) - start) % 360
                       for (px, py) in _arc_covers_sector(e1, e2, geo.ARC_R, large, 0)]
                for a in rel:                       # every point inside the sector (wrap-aware)
                    self.assertTrue(a <= measure + TOL or a >= 360 - TOL, f"s{s} m{measure}: {a:.2f} outside")
                mid = rel[len(rel) // 2]            # the arc midpoint sits near the bisector
                self.assertLess(abs(mid - measure / 2.0), TOL, f"s{s} m{measure}: bisector off")

    def test_boundary_179_180_181(self):
        for measure, exp_large in ((179, 0), (180, 0), (181, 1)):
            other = (360 - measure)
            params = {"task": "angles_at_point_missing", "regions": [measure, other - 10, 10], "unknownIndex": 2}
            fig = geo._build_figure(params)
            svg = geo.canonical_svg(fig, "a", "t", "d")
            first = self.ARC_RE.findall(svg)[0]
            self.assertEqual(int(first[4]), exp_large, f"measure {measure}")
            self.assertEqual(int(first[5]), 0)

    def test_tamper_large_flag_on_reflex_fails(self):
        it = geo.generate(1, {"task": "angles_at_point_missing", "interactionType": "free-response"})
        svg = it["media"][0]["svg"]
        bad = re.sub(r"(A 70 70 0 )1( 0 )", r"\g<1>0\g<2>", svg, count=1)
        self.assertNotEqual(bad, svg)
        it["media"][0]["svg"] = bad
        names = [c["name"] for c in geo.validate(it)["checks"] if c["result"] == "fail"]
        self.assertIn("arc-large-flag-correct", names)
        self.assertIn("reflex-region-rendered-correctly", names)

    def test_tamper_sweep_fails(self):
        it = geo.generate(5, {"task": "triangle_missing_angle", "interactionType": "free-response"})
        it["media"][0]["svg"] = it["media"][0]["svg"].replace("A 70 70 0 0 0", "A 70 70 0 0 1", 1)
        names = [c["name"] for c in geo.validate(it)["checks"] if c["result"] == "fail"]
        self.assertIn("arc-sweep-correct", names)

    def test_label_inside_every_sector(self):
        for s in range(1, 600):
            for m in ("free-response", "multiple-choice"):
                v = geo.validate(geo.generate(s, {"interactionType": m}))
                ok = {c["name"]: c["result"] for c in v["checks"]}
                self.assertEqual(ok.get("label-inside-intended-region"), "pass", f"s{s} {m}")
                self.assertEqual(ok.get("reflex-region-rendered-correctly"), "pass")


class TestVerticallyOppositeMarking(unittest.TestCase):
    def test_neutral_leader_no_matching_arc(self):
        for s in range(1, 400):
            it = geo.generate(s, {"task": "vertically_opposite_angle", "interactionType": "free-response"})
            svg = it["media"][0]["svg"]
            self.assertEqual(svg.count('<path class="ga"'), 1, "only the given angle has an arc")
            self.assertEqual(svg.count('class="gt"'), 0, "no congruence tick marks")
            self.assertEqual(svg.count('class="gx"'), 1, "exactly one neutral target leader")
            ok = {c["name"]: c["result"] for c in geo.validate(it)["checks"]}
            self.assertEqual(ok.get("no-theorem-revealing-markers"), "pass", f"s{s}")
            self.assertEqual(ok.get("target-region-unambiguous"), "pass", f"s{s}")


class TestA11yEquivalence(unittest.TestCase):
    LEAK = {
        "straight_line_missing_angle": "The angles sum to 180 degrees, so x is the rest.",
        "triangle_missing_angle": "The angles sum to 180 degrees; x = 70.",
        "isosceles_base_angle": "The base angles are equal in an isosceles triangle.",
        "vertically_opposite_angle": "Vertically opposite angles are equal, so x equals the given.",
        "angles_at_point_missing": "Angles around a point add up to 360 degrees.",
    }

    def test_generated_descriptions_are_equivalent_not_easier(self):
        for s in range(1, 400):
            for m in ("free-response", "multiple-choice"):
                it = geo.generate(s, {"interactionType": m})
                ok = {c["name"]: c["result"] for c in geo.validate(it)["checks"]}
                self.assertEqual(ok.get("a11y-equivalent-information"), "pass", f"s{s} {m}")

    def test_theorem_leaking_text_is_rejected(self):
        for task, leak in self.LEAK.items():
            params = ({"task": task, "A": 50, "B": 60} if task == "triangle_missing_angle"
                      else {"task": task, "apex": 108} if task == "isosceles_base_angle"
                      else {"task": task, "theta": 40} if task == "vertically_opposite_angle"
                      else {"task": task, "regions": [40, 60, 80], "unknownIndex": 2})
            acc = geo._accessibility(params)
            self.assertTrue(geo._a11y_equivalent_ok(params, acc), f"{task} clean desc accepted")
            bad = dict(acc, desc=leak)
            self.assertFalse(geo._a11y_equivalent_ok(params, bad), f"{task} leak rejected")


if __name__ == "__main__":
    unittest.main(verbosity=2)
