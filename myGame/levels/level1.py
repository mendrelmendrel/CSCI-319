from utils import vec


# Hand-authored tree clusters for the first level.
# The layout keeps a clear center around the player's spawn,
# adds denser pockets near the edges, and leaves open movement lanes.
TREE_CLUSTER_SPECS = [
    {
        "origin": (170, 150),
        "offsets": [
            (-72, -18),
            (-28, -42),
            (18, -10),
            (62, 18),
            (-46, 38),
            (12, 54),
        ],
    },
    {
        "origin": (430, 230),
        "offsets": [
            (-54, -18),
            (-12, 18),
            (32, -28),
            (68, 22),
        ],
    },
    {
        "origin": (1170, 170),
        "offsets": [
            (-64, -20),
            (-18, -46),
            (26, -8),
            (68, 16),
            (-40, 42),
            (14, 56),
        ],
    },
    {
        "origin": (1410, 280),
        "offsets": [
            (-44, -12),
            (-6, 18),
            (34, -18),
            (56, 28),
        ],
    },
    {
        "origin": (180, 860),
        "offsets": [
            (-70, -16),
            (-26, -42),
            (18, -8),
            (64, 18),
            (-44, 42),
            (12, 58),
        ],
    },
    {
        "origin": (460, 1010),
        "offsets": [
            (-50, -18),
            (-8, 14),
            (34, -20),
            (64, 20),
        ],
    },
    {
        "origin": (1180, 930),
        "offsets": [
            (-60, -16),
            (-16, -44),
            (24, -10),
            (66, 20),
            (-42, 42),
            (12, 58),
        ],
    },
    {
        "origin": (1410, 1030),
        "offsets": [
            (-44, -10),
            (-6, 20),
            (34, -18),
            (58, 24),
        ],
    },
    {
        "origin": (760, 150),
        "offsets": [
            (-120, 0),
            (128, 0),
        ],
    },
    {
        "origin": (770, 1060),
        "offsets": [
            (-118, 0),
            (122, 0),
        ],
    },
    {
        "origin": (300, 560),
        "offsets": [
            (-70, -12),
            (-18, 22),
            (34, -18),
        ],
    },
    {
        "origin": (1280, 560),
        "offsets": [
            (-68, -14),
            (-16, 20),
            (36, -16),
        ],
    },
]

BOULDER_SPECS = [
    # Big landmarks near the outer corners
        {"fileName": "boulder2.png", "position": (118, 78), "collisionSize": (84, 68), "collisionScale": 0.70},
        {"fileName": "boulder2.png", "position": (1310, 92), "collisionSize": (84, 68), "collisionScale": 0.70},
        {"fileName": "boulder2.png", "position": (126, 980), "collisionSize": (84, 68), "collisionScale": 0.70},
        {"fileName": "boulder2.png", "position": (1320, 950), "collisionSize": (84, 68), "collisionScale": 0.70},

    # Mid-size blockers that shape the play lanes
        {"fileName": "Boulder.png", "position": (560, 300), "collisionSize": (17, 14), "collisionScale": 0.70},
        {"fileName": "Boulder.png", "position": (1030, 325), "collisionSize": (17, 14), "collisionScale": 0.70},
        {"fileName": "Boulder.png", "position": (585, 865), "collisionSize": (17, 14), "collisionScale": 0.70},
        {"fileName": "Boulder.png", "position": (1020, 835), "collisionSize": (17, 14), "collisionScale": 0.70},

    # Small cluster to create a subtle choke point without closing the lane
        {"fileName": "Boulder.png", "position": (730, 560), "collisionSize": (17, 14), "collisionScale": 0.70},
        {"fileName": "Boulder.png", "position": (780, 600), "collisionSize": (17, 14), "collisionScale": 0.70},

        # Small boulder variant using boulder2 source, scaled near bush size
        {"fileName": "boulder2.png", "position": (262, 300), "drawSize": (56, 56), "collisionSize": (40, 32), "collisionScale": 0.70},
        {"fileName": "boulder2.png", "position": (1240, 320), "drawSize": (56, 56), "collisionSize": (40, 32), "collisionScale": 0.70},
        {"fileName": "boulder2.png", "position": (286, 770), "drawSize": (56, 56), "collisionSize": (40, 32), "collisionScale": 0.70},
        {"fileName": "boulder2.png", "position": (1220, 770), "drawSize": (56, 56), "collisionSize": (40, 32), "collisionScale": 0.70},
]

BUSH_SPECS = [
    # Upper-left region clusters
    {"fileName": "bush_1.png", "position": (110, 132)},
    {"fileName": "bush2.png", "position": (150, 156)},
    {"fileName": "Bush3.png", "position": (190, 122)},
    {"fileName": "Bush4.png", "position": (226, 168)},
    {"fileName": "bush2.png", "position": (260, 132)},
    {"fileName": "Bush3.png", "position": (302, 162)},

    {"fileName": "bush_1.png", "position": (190, 220)},
    {"fileName": "bush2.png", "position": (230, 244)},
    {"fileName": "Bush3.png", "position": (270, 206)},
    {"fileName": "Bush4.png", "position": (306, 252)},
    {"fileName": "bush2.png", "position": (346, 220)},

    # Upper-mid lane clusters
    {"fileName": "bush_1.png", "position": (612, 148)},
    {"fileName": "bush2.png", "position": (652, 172)},
    {"fileName": "Bush3.png", "position": (692, 138)},
    {"fileName": "Bush4.png", "position": (730, 182)},
    {"fileName": "bush2.png", "position": (772, 148)},

    {"fileName": "bush_1.png", "position": (836, 156)},
    {"fileName": "bush2.png", "position": (878, 184)},
    {"fileName": "Bush3.png", "position": (918, 152)},
    {"fileName": "Bush4.png", "position": (958, 198)},

    # Upper-right region clusters
    {"fileName": "bush_1.png", "position": (1088, 136)},
    {"fileName": "bush2.png", "position": (1128, 164)},
    {"fileName": "Bush3.png", "position": (1168, 128)},
    {"fileName": "Bush4.png", "position": (1206, 174)},
    {"fileName": "bush2.png", "position": (1248, 142)},
    {"fileName": "Bush3.png", "position": (1290, 170)},

    {"fileName": "bush_1.png", "position": (1218, 224)},
    {"fileName": "bush2.png", "position": (1262, 248)},
    {"fileName": "Bush3.png", "position": (1304, 214)},
    {"fileName": "Bush4.png", "position": (1344, 258)},

    # Mid-left clusters
    {"fileName": "bush_1.png", "position": (182, 514)},
    {"fileName": "bush2.png", "position": (224, 542)},
    {"fileName": "Bush3.png", "position": (266, 508)},
    {"fileName": "Bush4.png", "position": (304, 554)},
    {"fileName": "bush2.png", "position": (346, 520)},

    # Mid-right clusters
    {"fileName": "bush_1.png", "position": (1180, 516)},
    {"fileName": "bush2.png", "position": (1222, 544)},
    {"fileName": "Bush3.png", "position": (1266, 510)},
    {"fileName": "Bush4.png", "position": (1302, 556)},
    {"fileName": "bush2.png", "position": (1344, 522)},

    # Lower-left region clusters
    {"fileName": "bush_1.png", "position": (130, 892)},
    {"fileName": "bush2.png", "position": (172, 920)},
    {"fileName": "Bush3.png", "position": (214, 886)},
    {"fileName": "Bush4.png", "position": (252, 932)},
    {"fileName": "bush2.png", "position": (294, 898)},
    {"fileName": "Bush3.png", "position": (336, 928)},

    {"fileName": "bush_1.png", "position": (240, 984)},
    {"fileName": "bush2.png", "position": (284, 1010)},
    {"fileName": "Bush3.png", "position": (324, 972)},
    {"fileName": "Bush4.png", "position": (364, 1018)},
    {"fileName": "bush2.png", "position": (406, 986)},

    # Lower-mid lane clusters
    {"fileName": "bush_1.png", "position": (626, 964)},
    {"fileName": "bush2.png", "position": (668, 992)},
    {"fileName": "Bush3.png", "position": (708, 958)},
    {"fileName": "Bush4.png", "position": (748, 1004)},
    {"fileName": "bush2.png", "position": (790, 970)},

    {"fileName": "bush_1.png", "position": (854, 976)},
    {"fileName": "bush2.png", "position": (896, 1004)},
    {"fileName": "Bush3.png", "position": (938, 968)},
    {"fileName": "Bush4.png", "position": (978, 1014)},

    # Lower-right region clusters
    {"fileName": "bush_1.png", "position": (1098, 886)},
    {"fileName": "bush2.png", "position": (1140, 914)},
    {"fileName": "Bush3.png", "position": (1182, 880)},
    {"fileName": "Bush4.png", "position": (1222, 926)},
    {"fileName": "bush2.png", "position": (1264, 894)},
    {"fileName": "Bush3.png", "position": (1306, 924)},

    {"fileName": "bush_1.png", "position": (1202, 996)},
    {"fileName": "bush2.png", "position": (1246, 1022)},
    {"fileName": "Bush3.png", "position": (1288, 986)},
    {"fileName": "Bush4.png", "position": (1328, 1032)},

    # Occasional singles for natural variation
    {"fileName": "bush2.png", "position": (510, 420)},
    {"fileName": "Bush4.png", "position": (920, 430)},
    {"fileName": "Bush3.png", "position": (560, 710)},
    {"fileName": "bush2.png", "position": (980, 690)},
    {"fileName": "Bush4.png", "position": (680, 332)},
    {"fileName": "Bush3.png", "position": (1042, 364)},
]


def get_level1_tree_positions():
    positions = []

    for cluster in TREE_CLUSTER_SPECS:
        origin = vec(*cluster["origin"])
        for dx, dy in cluster["offsets"]:
            positions.append(origin + vec(dx, dy))

    return positions


def get_level1_boulder_specs():
    return BOULDER_SPECS


def get_level1_bush_specs():
    return BUSH_SPECS
