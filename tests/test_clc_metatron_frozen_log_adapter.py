import itertools
import unittest


def warrant_live(entries):
    revoked = {rev for _premises, rev in entries if rev is not None}
    live = []
    live_set = set()
    for i, (premises, revokes) in enumerate(entries):
        if revokes is not None:
            continue
        if i in revoked:
            continue
        if all(p in live_set for p in premises):
            live.append(i)
            live_set.add(i)
    return tuple(live)


def snapshot(entries):
    return {
        "live": frozenset(warrant_live(entries)),
        "revoked": frozenset(
            rev for _premises, rev in entries if rev is not None
        ),
    }


def normalize(family):
    family = set(family)
    return {s for s in family if not any(t < s for t in family)}


def live_view_nonempty(live, family):
    return any(s <= live for s in normalize(family))


class CLCMetatronFrozenLogAdapterTests(unittest.TestCase):
    def test_exhaustive_support_liveness_2048(self):
        tokens = (0, 1, 2)
        supports = tuple(
            frozenset(tokens[i] for i in range(3) if bits & (1 << i))
            for bits in range(8)
        )
        checked = 0
        for live_bits in range(8):
            live = frozenset(
                tokens[i] for i in range(3) if live_bits & (1 << i)
            )
            for family_bits in range(256):
                family = {
                    supports[i] for i in range(8) if family_bits & (1 << i)
                }
                lhs = live_view_nonempty(live, family)
                rhs = any(s <= live for s in family)
                self.assertEqual(lhs, rhs)
                checked += 1
        self.assertEqual(checked, 2048)

    def test_baseline_and_future_revocation(self):
        baseline = (
            ((), None),
            ((0,), None),
            ((1,), None),
            ((), None),
        )
        self.assertEqual(warrant_live(baseline), (0, 1, 2, 3))
        revoked = baseline + (((), 1),)
        self.assertEqual(warrant_live(revoked), (0, 3))
        snap = snapshot(revoked)
        self.assertEqual(snap["live"], frozenset({0, 3}))
        self.assertEqual(snap["revoked"], frozenset({1}))
        self.assertTrue(snap["live"].isdisjoint(snap["revoked"]))

    def test_raw_out_of_range_revocation_target_is_retained(self):
        malformed = ((((), 99)),)
        snap = snapshot(malformed)
        self.assertEqual(snap["live"], frozenset())
        self.assertEqual(snap["revoked"], frozenset({99}))
        self.assertTrue(snap["live"].isdisjoint(snap["revoked"]))

    def test_support_fallback_after_revocation(self):
        baseline = (
            ((), None),
            ((0,), None),
            ((1,), None),
            ((), None),
        )
        revoked = baseline + (((), 1),)
        live = snapshot(revoked)["live"]
        self.assertFalse(live_view_nonempty(live, {frozenset({1})}))
        self.assertTrue(
            live_view_nonempty(
                live,
                {frozenset({1}), frozenset({3})},
            )
        )
        self.assertTrue(live_view_nonempty(live, {frozenset()}))

    def test_boolean_flip_is_not_continuation_neutral(self):
        flip = lambda b: not b
        observe = lambda b: b
        self.assertTrue(any(observe(flip(b)) != observe(b) for b in (False, True)))


if __name__ == "__main__":
    unittest.main()
