#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
import os.path
# Third-party
import ggplot

args = None
graphs = dict()
ruleset = os.path.basename(__file__).split(".")[0]
srand = None

title = "Star Wars: Edge of the Empire"
limits = (-1, 30)
vlab = "Symbol"
buckets = {"fs": ("1 Failure", "2 Success"), "d": ("5 Despair", ),
           "ta": ("3 Threat", "4 Advantage"), "t": ("6 Triumphs", )}
# (failure, threat, despair)
d12_chall = {1: (0, 0, 0), 2: (1, 0, 0), 3: (1, 0, 0), 4: (2, 0, 0),
             5: (2, 0, 0), 6: (0, 1, 0), 7: (0, 1, 0), 8: (0, 1, 0),
             9: (1, 1, 0), 10: (0, 2, 0), 11: (0, 2, 0), 12: (0, 0, 1)}
# (failure, threat)
d8_diff = {1: (0, 0), 2: (1, 0), 3: (2, 0), 4: (0, 1), 5: (0, 1), 6: (0, 1),
           7: (1, 1), 8: (0, 2)}
# (failure, threat)
d6_setb = {1: (0, 0), 2: (0, 0), 3: (1, 0), 4: (1, 0), 5: (0, 1), 6: (0, 1)}
# (success, advantage, triumph)
d12_prof = {1: (0, 0, 0), 2: (1, 0, 0), 3: (1, 0, 0), 4: (2, 0, 0),
            5: (2, 0, 0), 6: (0, 1, 0), 7: (1, 1, 0), 8: (0, 1, 0),
            9: (1, 1, 0), 10: (0, 2, 0), 11: (0, 2, 0), 12: (0, 0, 1)}
# (success, advantage)
d8_abil = {1: (0, 0), 2: (1, 0), 3: (1, 0), 4: (2, 0), 5: (0, 1), 6: (0, 1),
           7: (0, 2), 8: (1, 1)}
# (success, advantage)
d6_boost = {1: (0, 0), 2: (0, 0), 3: (1, 0), 4: (1, 1), 5: (0, 2), 6: (0, 1)}
# (challenge, difficulty, setback, proficiency, ability, boost, title)
dice_combos = {0: (0, 2, 0, 0, 2, 0, "Unskilled PC vs Average Difficulty"),
               1: (0, 3, 0, 0, 2, 0, "Unskilled PC vs Hard Difficulty"),
               2: (2, 1, 1, 0, 2, 0, "Unskilled PC vs Advesary NPC"),
               3: (0, 2, 0, 0, 4, 0, "Talented PC vs Average Difficulty"),
               4: (0, 3, 0, 0, 4, 0, "Talented PC vs Hard Difficulty"),
               5: (2, 1, 1, 0, 4, 0, "Talented PC vs Advesary"),
               6: (0, 2, 0, 3, 1, 1, "Pro PC vs Average Difficulty"),
               7: (0, 3, 0, 3, 1, 1, "Pro PC vs Hard Difficulty"),
               8: (2, 1, 1, 3, 1, 1, "Pro PC vs Advesary NPC")}
custom_combo = False


def setup(subparser):
    def intreg(num):
        global custom_combo
        num = int(num)
        custom_combo = True
        return num
    """Set up the sub-command parser"""
    sub = subparser.add_parser(ruleset, help="%s ruleset" % title)
    sub.add_argument("-c", "--challenge-dice", default=0, type=intreg,
                     metavar="INT", dest="dice_chall")
    sub.add_argument("-d", "--difficulty-dice",  default=0, type=intreg,
                     metavar="INT",  dest="dice_diff")
    sub.add_argument("-s", "--setback-dice",  default=0, type=intreg,
                     metavar="INT", dest="dice_setb")
    sub.add_argument("-p", "--proficiency-dice",  default=0, type=intreg,
                     metavar="INT", dest="dice_prof")
    sub.add_argument("-a", "--ability-dice",  default=0, type=intreg,
                     metavar="INT", dest="dice_abil")
    sub.add_argument("-b", "--boost-dice",  default=0, type=intreg,
                     metavar="INT", dest="dice_boost")
    sub.add_argument("-t", "--title",  default="Custom Graph",
                     metavar="STRING", dest="desc")
    sub.add_argument("-l", "--limit",  metavar="INT", type=int)


def prepare(parent_args, parent_srand):
    global args, dice_combos, graphs, srand, variables
    args = parent_args
    srand = parent_srand
    if custom_combo:
        dice_combos = {0: (args.dice_chall, args.dice_diff, args.dice_setb,
                           args.dice_prof, args.dice_abil, args.dice_boost,
                           args.desc)}
        variables = (0, )
    else:
        variables = dice_combos.keys()
    # Graphs
    for variable in variables:
        graphs[variable] = dict()
        graph = graphs[variable]
        graph["color_list"] = ["#4B0082", "#008000", "#000000", "#87CEFA"]
        dice_chall, dice_diff, dice_setb = dice_combos[variable][0:3]
        dice_prof, dice_abil, dice_boost = dice_combos[variable][3:6]
        desc = dice_combos[variable][-1]
        graph["dice_key"] = str()
        if dice_chall:
            graph["dice_key"] = "%s%s" % (graph["dice_key"], "c" * dice_chall)
            graph["color_list"].append("#ff0000")
        if dice_diff:
            graph["dice_key"] = "%s%s" % (graph["dice_key"], "d" * dice_diff)
        if dice_setb:
            graph["dice_key"] = "%s%s" % (graph["dice_key"], "b" * dice_setb)
        if dice_prof:
            graph["dice_key"] = "%s%s" % (graph["dice_key"], "C" * dice_prof)
            graph["color_list"].append("#ffff00")
        if dice_abil:
            graph["dice_key"] = "%s%s" % (graph["dice_key"], "D" * dice_abil)
        if dice_boost:
            graph["dice_key"] = "%s%s" % (graph["dice_key"], "B" * dice_boost)
        graph["file_suffix"] = "_%s" % desc.lower().replace(" ", "_")
        graph["title"] = "%s\n%s" % (title, desc)
        if args.limit:
            graph["limits"] = (limits[0], args.limit)
    if custom_combo:
        graphs[0]["file_prefix"] = "%s__" % ruleset


def simulate_rolls(variable):
    dice_chall, dice_diff, dice_setb = dice_combos[variable][0:3]
    dice_prof, dice_abil, dice_boost = dice_combos[variable][3:6]
    # Outcomes
    outcomes = dict()
    for group in buckets:
        for symbol in buckets[group]:
            outcomes[symbol] = dict()
    # Simulate rolls
    for roll in xrange(args.rolls):
        results = dict()
        for group in buckets:
            results[group] = 0
        # Dice - Proficiency
        for d in xrange(dice_chall):
            failure, threat, despair = d12_chall[srand.randint(1, 12)]
            results["fs"] -= failure
            results["ta"] -= threat
            results["d"] -= despair
        # Dice - Difficulty
        for d in xrange(dice_diff):
            failure, threat = d8_diff[srand.randint(1, 8)]
            results["fs"] -= failure
            results["ta"] -= threat
        # Dice - Difficulty
        for d in xrange(dice_setb):
            failure, threat = d6_setb[srand.randint(1, 6)]
            results["fs"] -= failure
            results["ta"] -= threat
        # Dice - Proficiency
        for d in xrange(dice_prof):
            success, advantage, triumph = d12_prof[srand.randint(1, 12)]
            results["fs"] += success
            results["ta"] += advantage
            results["t"] += triumph
        # Dice - Ability
        for d in xrange(dice_abil):
            success, advantage = d8_abil[srand.randint(1, 8)]
            results["fs"] += success
            results["ta"] += advantage
        # Dice - Ability
        for d in xrange(dice_boost):
            success, advantage = d6_boost[srand.randint(1, 6)]
            results["fs"] += success
            results["ta"] += advantage
        # Update outcomes
        for group in buckets:
            result = results[group]
            for symbol in buckets[group]:
                # Massage results
                if symbol.endswith("Failure") and result > 0:
                    continue
                if symbol.endswith("Success") and result < 0:
                    continue
                if symbol.endswith("Threat") and result > 0:
                    continue
                if symbol.endswith("Advantage") and result < 0:
                    continue
                if symbol.endswith("Despair") and result == 0:
                    continue
                if symbol.endswith("Triumphs") and result == 0:
                    continue
                # Update
                if result not in outcomes[symbol]:
                    outcomes[symbol][result] = 1
                else:
                    outcomes[symbol][result] += 1
    # Organize data
    data = list()
    for group in buckets:
        for symbol in buckets[group]:
            for result in outcomes[symbol]:
                count = outcomes[symbol][result]
                percent = round((float(count) / float(args.rolls)) * 100, 1)
                # Round up miniscule percentages for Despair and Triumph
                if percent < 0.5 and (symbol.endswith("Despair") or
                                      symbol.endswith("Triumphs")):
                    percent = 0.5
                # Ignore miniscule percentages
                if percent >= 0.5:
                    data.append((variable, symbol, result, count, percent))
    return sorted(data)


def update_plot(gkey, graph_conf, plot, plot_data):
    """Determine x axis breaks and add rolled dice symbols to plot."""
    # Determine x axis breaks
    x_breaks = plot_data.copy()
    x_breaks = x_breaks[graph_conf["xlab"]].drop_duplicates().tolist()
    x_breaks.sort()
    x_labels = [" ", ] + [abs(x) for x in x_breaks] + [" ", ]
    x_breaks = [x_breaks[0] - 0.5, ] + x_breaks + [x_breaks[-1] + 0.5, ]
    plot += ggplot.scale_x_discrete(breaks=x_breaks, labels=x_labels)
    # Add rolled dice symbols
    top0 = graph_conf["limits"][1] - 1
    top1 = top0 - 1.2
    left0 = x_breaks[1]
    left1 = left0
    colors = {"b": "#000000", "B": "#87CEFA", "c": "#ff0000", "d": "#4B0082",
              "C": "#ffff00", "D": "#008000"}
    pad = len(x_breaks) * 0.0235
    for letter in graphs[gkey]["dice_key"]:
        if letter in "CDB":
            color = colors[letter]
            plot += ggplot.geom_text(label=[letter.lower(), ],
                                     x=[left0, left0 + 1],
                                     y=[top0, top0 - 1], color=color,
                                     family="EotE Symbol")
            left0 += pad
        else:
            color = colors[letter]
            plot += ggplot.geom_text(label=[letter.lower(), ],
                                     x=[left1, left1 + 1],
                                     y=[top1, top1 - 1], color=color,
                                     family="EotE Symbol")
            left1 += pad
    return plot
