# -*- coding: utf-8 -*-
from __future__ import division, absolute_import
from __future__ import print_function

from os.path import join

import pytest

from xtgeo.grid3d import Grid
from xtgeo.well import Well
from xtgeo.grid3d import GridProperty
from xtgeo.common import XTGeoDialog

xtg = XTGeoDialog()
logger = xtg.basiclogger(__name__)

if not xtg.testsetup():
    raise SystemExit

TMPD = xtg.tmpdir

# =============================================================================
# Do tests
# =============================================================================

GRIDFILE = "../xtgeo-testdata/3dgrids/reek/reek_sim_grid.roff"
ZONEFILE = "../xtgeo-testdata/3dgrids/reek/reek_sim_zone.roff"
WELL1 = "../xtgeo-testdata/wells/reek/1/OP_1.w"
WELL2 = "../xtgeo-testdata/wells/reek/1/OP_2.w"
WELL3 = "../xtgeo-testdata/wells/reek/1/OP_3.w"
WELL4 = "../xtgeo-testdata/wells/reek/1/OP_4.w"
WELL5 = "../xtgeo-testdata/wells/reek/1/OP_5.w"
WELL6 = "../xtgeo-testdata/wells/reek/1/WI_1.w"
WELL7 = "../xtgeo-testdata/wells/reek/1/WI_3.w"

PWELL1 = "../xtgeo-testdata/wells/reek/1/OP1_perf.w"

MATCHD1 = {
    "WI_1": 75,
    "WI_3": 75,
    "OP_4": 78,
    "OP_5": 78,
    "OP_1": 80,
    "OP_2": 77,
    "OP_3": 77,
}

MATCHD2 = {
    "WI_1": 65,
    "WI_3": 40,
    "OP_4": 71,
    "OP_5": 69,
    "OP_1": 71,
    "OP_2": 65,
    "OP_3": 70,
}

# A problem here is that the OP wells has very few samples, which
# makes a assumed match of 100% (since only one point)
# Also, the match percent seems to be a bit unstable, hence
# the rounding to INT...


def test_report_zlog_mismatch():
    """Report zone log mismatch grid and well."""
    g1 = Grid()
    g1.from_file(GRIDFILE)

    zo = GridProperty()
    zo.from_file(ZONEFILE, name="Zone")

    w1 = Well(WELL1)
    w2 = Well(WELL2)
    w3 = Well(WELL3)
    w4 = Well(WELL4)
    w5 = Well(WELL5)
    w6 = Well(WELL6)
    w7 = Well(WELL7)

    wells = [w1, w2, w3, w4, w5, w6, w7]

    for wll in wells:
        response = g1.report_zone_mismatch(
            well=wll,
            zonelogname="Zonelog",
            zoneprop=zo,
            zonelogrange=(1, 3),
            depthrange=[1300, 9999],
        )

        match = int(float("{0:.4f}".format(response[0])))
        logger.info("Match for %s is %s", wll.wellname, match)
        assert match == MATCHD1[wll.name]

        # check also with resultformat=2
        res = g1.report_zone_mismatch(
            well=wll,
            zonelogname="Zonelog",
            zoneprop=zo,
            zonelogrange=(1, 3),
            depthrange=[1300, 9999],
            resultformat=2,
        )

        match = int(float("{0:.4f}".format(res["MATCH2"])))
        logger.info("Match for %s is %s", wll.wellname, match)
        assert match == MATCHD2[wll.name]


def test_report_zlog_mismatch_resultformat3():
    """Report zone log mismatch grid and well, export updated wellsegment"""
    g1 = Grid()
    g1.from_file(GRIDFILE)

    zo = GridProperty()
    zo.from_file(ZONEFILE, name="Zone")

    w1 = Well(WELL1)

    res = g1.report_zone_mismatch(
        well=w1,
        zonelogname="Zonelog",
        zoneprop=zo,
        zonelogrange=(1, 3),
        depthrange=[1300, 9999],
        resultformat=3,
    )
    mywell = res["WELLINTV"]
    logger.info("\n%s", mywell.dataframe.to_string())
    mywell.to_file(join(TMPD, "w1_zlog_report.rmswell"))


def test_report_zlog_mismatch_perflog():
    """Report zone log mismatch grid and well filter on PERF"""
    g1 = Grid()
    g1.from_file(GRIDFILE)

    zo = GridProperty()
    zo.from_file(ZONEFILE, name="Zone")

    w1 = Well(PWELL1)

    w1.dataframe.to_csv("TMP/testw1.csv")

    res = g1.report_zone_mismatch(
        well=w1,
        zonelogname="Zonelog",
        zoneprop=zo,
        zonelogrange=(1, 3),
        depthrange=[1580, 9999],
        perflogname="PERF",
        resultformat=2,
    )
    mywell = res["WELLINTV"]
    logger.info("\n%s", mywell.dataframe.to_string())
    mywell.to_file(join(TMPD, "w1_perf_report.rmswell"))

    assert res["MATCH2"] == pytest.approx(82.14, 0.001)
    assert res["TCOUNT2"] == 56
    assert res["MCOUNT2"] == 46

    w1 = Well(WELL1)

    # well is missing perflog; hence result shall be None
    res = g1.report_zone_mismatch(
        well=w1,
        zonelogname="Zonelog",
        zoneprop=zo,
        zonelogrange=(1, 3),
        depthrange=[1580, 9999],
        perflogname="PERF",
        resultformat=2,
    )

    # ask for perflogname but no such present
    assert res is None
