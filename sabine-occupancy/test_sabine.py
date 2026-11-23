"""Tests for sabine.py. Run: python -m unittest -v  (or pytest)."""

import math
import unittest

import numpy as np

import sabine

K = sabine.sabine_constant()

# King's Chamber, Great Pyramid (Petrie survey): 10.47 × 5.234 × 5.852 m, granite.
KC_DIMS = (10.47, 5.234, 5.852)
KC_GRANITE = {125: 0.01, 250: 0.01, 500: 0.01, 1000: 0.02, 2000: 0.02, 4000: 0.02}


def kings_chamber():
    L, W, H = KC_DIMS
    floor, perim = L * W, 2 * (L + W)
    volume = floor * H
    surfaces = [(floor, KC_GRANITE), (floor, KC_GRANITE), (perim * H, KC_GRANITE)]
    a_surf = sabine.absorption_from_surfaces(surfaces)
    a_air = sabine.air_absorption(volume)
    a_tot = {f: a_surf[f] + a_air[f] for f in a_surf}
    return dict(volume=volume, floor=floor, perim=perim, surface=2 * floor + perim * H,
                t_empty=sabine.sabine_t60(a_tot, volume))


class AnalyticChecks(unittest.TestCase):
    def test_constant(self):
        self.assertAlmostEqual(K, 0.1611, places=4)

    def test_shoebox_by_hand(self):
        # 10 × 8 × 4 m, uniform alpha 0.1: V = 320, S = 304, A = 30.4
        V, S = 320.0, 2 * (10 * 8 + 10 * 4 + 8 * 4)
        a = sabine.absorption_from_surfaces([(S, {500: 0.1})])
        self.assertAlmostEqual(a[500], 30.4)
        self.assertAlmostEqual(sabine.sabine_t60(a, V)[500], K * 320 / 30.4)

    def test_round_trip(self):
        t = {125: 2.1, 500: 1.7, 2000: 1.2}
        a = sabine.absorption_from_rt60(t, 900.0)
        back = sabine.sabine_t60(a, 900.0)
        for f in t:
            self.assertAlmostEqual(back[f], t[f])

    def test_eyring_converges_to_sabine_at_low_alpha(self):
        a = {500: 0.01 * 1000}
        ts = sabine.sabine_t60(a, 2000.0)[500]
        te = sabine.eyring_t60(a, 2000.0, 1000.0)[500]
        self.assertLess(abs(te / ts - 1), 0.006)
        a_hi = {500: 0.5 * 1000}
        self.assertLess(sabine.eyring_t60(a_hi, 2000.0, 1000.0)[500],
                        sabine.sabine_t60(a_hi, 2000.0)[500])


class SabineNumbers(unittest.TestCase):
    def test_sabine_audience_figure(self):
        self.assertAlmostEqual(sabine.person_absorption(1, "modern")[500], 0.44)

    def test_attire_factor(self):
        self.assertAlmostEqual(sabine.person_absorption(10, "light")[500], 10 * 0.44 * 0.70)

    def test_custom_table_overrides_attire(self):
        a = sabine.person_absorption(2, attire="light", per_person={500: 0.6})
        self.assertEqual(a, {500: 1.2})


class KingsChamberRegression(unittest.TestCase):
    """Pins the numbers in the ASA 191st meeting abstract. If these move, the
    published claim moved — find out why before changing the test."""

    def setUp(self):
        self.kc = kings_chamber()

    def test_geometry(self):
        self.assertAlmostEqual(self.kc["volume"], 320.7, places=1)
        self.assertAlmostEqual(self.kc["surface"], 293.4, places=1)

    def test_empty_t500(self):
        self.assertAlmostEqual(self.kc["t_empty"][500], 13.95, places=2)

    def test_chant_and_speech(self):
        kc = self.kc
        chant = sabine.solve_people(kc["t_empty"], kc["volume"], 3.0)
        speech = sabine.solve_people(kc["t_empty"], kc["volume"], 1.0)
        self.assertEqual(math.ceil(chant), 44)
        self.assertEqual(math.ceil(speech), 156)

    def test_capacity(self):
        cap = sabine.capacity(self.kc["floor"], self.kc["perim"])
        self.assertEqual(int(cap), 129)

    def test_modern_attire_flips_speech_finding(self):
        # Documented sensitivity: at Sabine's unscaled 0.44/person, speech
        # clarity needs fewer people than crush capacity. Keep this visible.
        kc = self.kc
        speech = sabine.solve_people(kc["t_empty"], kc["volume"], 1.0, attire="modern")
        self.assertEqual(math.ceil(speech), 110)
        self.assertLess(speech, sabine.capacity(kc["floor"], kc["perim"]))


class Monotonicity(unittest.TestCase):
    def test_occupied_t_decreases(self):
        t = {500: 4.0, 1000: 3.0}
        prev = None
        for n in range(0, 300, 10):
            cur = sabine.occupied_rt60(t, 1500.0, n)[500]
            if prev is not None:
                self.assertLess(cur, prev)
            prev = cur

    def test_zero_people_is_identity(self):
        t = {125: 3.0, 500: 2.0}
        self.assertEqual(sabine.occupied_rt60(t, 800.0, 0), pytest_approx(t))

    def test_solve_is_inverse(self):
        t = {500: 6.0}
        for target in (0.8, 1.5, 3.0, 5.0):
            n = sabine.solve_people(t, 2500.0, target)
            self.assertAlmostEqual(sabine.occupied_rt60(t, 2500.0, n)[500], target)

    def test_already_below_target(self):
        self.assertEqual(sabine.solve_people({500: 0.9}, 300.0, 1.0), 0.0)


class FailLoudly(unittest.TestCase):
    def test_missing_volume(self):
        with self.assertRaisesRegex(ValueError, "volume_m3"):
            sabine.occupied_rt60({500: 2.0}, None, 10)

    def test_band_without_person_data(self):
        with self.assertRaisesRegex(ValueError, "63"):
            sabine.occupied_rt60({63: 2.0}, 500.0, 10)

    def test_bad_attire(self):
        with self.assertRaisesRegex(ValueError, "attire"):
            sabine.person_absorption(5, "toga")

    def test_negative_people(self):
        with self.assertRaises(ValueError):
            sabine.person_absorption(-1)

    def test_capacity_needs_perimeter(self):
        with self.assertRaisesRegex(ValueError, "perimeter_m"):
            sabine.capacity(50.0, None)

    def test_no_silent_capacity_clamp(self):
        # 10,000 people in a 300 m³ room: physics answer, no clamp
        t = sabine.occupied_rt60({500: 5.0}, 300.0, 10_000)[500]
        self.assertGreater(t, 0)


class PresenceFilter(unittest.TestCase):
    fs = 16000

    def synthetic_ir(self, t_by_band, seconds=3.0, seed=0):
        """Exponentially decaying noise per band (via the module's own crossover
        so band content is known), plus a direct spike."""
        rng = np.random.default_rng(seed)
        n = int(seconds * self.fs)
        t = np.arange(n) / self.fs
        noise = rng.standard_normal(n)
        n_fft = 1 << int(math.ceil(math.log2(2 * n)))
        spec = np.fft.rfft(noise, n_fft)
        freqs = np.fft.rfftfreq(n_fft, 1 / self.fs)
        bands = sorted(t_by_band)
        ir = np.zeros(n)
        for f, w in zip(bands, sabine._band_weights(freqs, bands)):
            ir += np.fft.irfft(spec * w, n_fft)[:n] * np.exp(-math.log(1000) * t / t_by_band[f])
        ir[0] = 20 * np.max(np.abs(ir))
        return ir

    def band_t60(self, ir, band, bands):
        """Schroeder T20 (−5…−25 dB) of one band, extrapolated to 60 dB."""
        n = ir.size
        n_fft = 1 << int(math.ceil(math.log2(2 * n)))
        freqs = np.fft.rfftfreq(n_fft, 1 / self.fs)
        w = sabine._band_weights(freqs, bands)[bands.index(band)]
        x = np.fft.irfft(np.fft.rfft(ir, n_fft) * w, n_fft)[:n]
        x[:40] = 0  # drop the direct spike's band-limited ringing
        edc = np.cumsum((x ** 2)[::-1])[::-1]
        db = 10 * np.log10(edc / edc[0])
        i5, i25 = np.argmax(db <= -5), np.argmax(db <= -25)
        slope = (db[i25] - db[i5]) / ((i25 - i5) / self.fs)
        return -60 / slope

    def test_identity_when_unchanged(self):
        ir = self.synthetic_ir({125: 2.0, 500: 1.5, 2000: 1.0})
        t = {125: 2.0, 500: 1.5, 2000: 1.0}
        out = sabine.presence_filter(ir, self.fs, t, t)
        np.testing.assert_allclose(out, ir, atol=1e-10)

    def test_decay_reaches_target(self):
        bands = [125, 250, 500, 1000, 2000, 4000]
        t_emp = {f: 2.0 for f in bands}
        t_occ = {125: 1.6, 250: 1.4, 500: 1.2, 1000: 1.0, 2000: 0.9, 4000: 0.9}
        ir = self.synthetic_ir(t_emp)
        out = sabine.presence_filter(ir, self.fs, t_emp, t_occ)
        for f in (500, 1000, 2000):
            self.assertAlmostEqual(self.band_t60(out, f, bands) / t_occ[f], 1.0, delta=0.08)

    def test_direct_sound_preserved(self):
        ir = self.synthetic_ir({500: 2.0})
        out = sabine.presence_filter(ir, self.fs, {500: 2.0}, {500: 0.5})
        self.assertAlmostEqual(out[0], ir[0], places=6)

    def test_rejects_multichannel(self):
        with self.assertRaises(ValueError):
            sabine.presence_filter(np.zeros((2, 100)), 48000, {500: 1}, {500: 1})


def pytest_approx(d):
    """dict equality with float tolerance, without needing pytest."""
    class _A(dict):
        def __eq__(self, other):
            return set(self) == set(other) and all(
                math.isclose(self[k], other[k], rel_tol=1e-12) for k in self)
    return _A(d)


if __name__ == "__main__":
    unittest.main()
