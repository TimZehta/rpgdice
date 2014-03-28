#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
import os.path

args = None
batches = dict()
ruleset = os.path.basename(__file__).split(".")[0]
srand = None

title = "Star Wars: Edge of the Empire"
symbols = { "fs": ("1 Failure", "2 Success"), "d": ("5 Despair", ),
            "ta": ("3 Threat", "4 Advantage"), "t": ("6 Triumphs", )}
# (failure, threat, despair)
die_chal = {1: (0, 0, 0), 2: (1, 0, 0), 3: (1, 0, 0), 4: (2, 0, 0),
            5: (2, 0, 0), 6: (0, 1, 0), 7: (0, 1, 0), 8: (0, 1, 0),
            9: (1, 1, 0), 10: (0, 2, 0), 11: (0, 2, 0), 12: (0, 0, 1)}
# (failure, threat)
die_diff = {1: (0, 0), 2: (1, 0), 3: (2, 0), 4: (0, 1), 5: (0, 1), 6: (0, 1),
            7: (1, 1), 8: (0, 2)}
# (success, advantage, triumph)
die_prof = {1: (0, 0, 0), 2: (1, 0, 0), 3: (1, 0, 0), 4: (2, 0, 0),
            5: (2, 0, 0), 6: (0, 1, 0), 7: (1, 1, 0), 8: (0, 1, 0),
            9: (1, 1, 0), 10: (0, 2, 0), 11: (0, 2, 0), 12: (0, 0, 1)}
# (success, advantage)
die_abil = {1: (0, 0), 2: (1, 0), 3: (1, 0), 4: (2, 0), 5: (0, 1), 6: (0, 1),
            7: (0, 2), 8: (1, 1)}
# (challenge, difficulty, proficiency, ability, title)
dice_combos = {0: (2, 1, 0, 2, "Advesary vs Novice"),
               1: (2, 1, 0, 4, "Advesary vs Talented"),
               2: (2, 1, 3, 1, "Advesary vs Pro"),
               3: (0, 3, 0, 2, "Hard vs Novice"),
               4: (0, 3, 0, 4, "Hard vs Talented"),
               5: (0, 3, 3, 1, "Hard vs Pro"),
               6: (0, 1, 0, 2, "Easy vs Novice"),
               7: (0, 1, 0, 4, "Easy vs Talented"),
               8: (0, 1, 3, 1, "Easy vs Pro")}
variables = dice_combos.keys()
for variable in dice_combos:
    batches[variable] = dict()
    batch = batches[variable]
    batch["color_list"] = ["#4B0082", "#008000", "#000000", "#87CEFA"]
    dice_chal, dice_diff, dice_prof, dice_abil, desc = dice_combos[variable]
    dice = str()
    if dice_chal:
        dice = "%s, %d Challenge" % (dice, dice_chal)
        batches[variable]["color_list"].append("#ff0000")
    if dice_diff:
        dice = "%s, %d Difficulty" % (dice, dice_diff)
    if dice_prof:
        dice = "%s, %d Proficiency" % (dice, dice_prof)
        batches[variable]["color_list"].append("#ffff00")
    if dice_abil:
        dice = "%s, %d Ability" % (dice, dice_abil)
    dice = dice.strip(", ")
    batch["file_suffix"] = "_%s" % desc.lower().replace(" ", "_")
    batch["title"] = "%s\n%s\n%s" % (title, dice, desc)
    bottom = (-2 * dice_chal) + (-2 * dice_diff)
    top = (2 * dice_prof) + (2 * dice_abil) + 1
    batch["scale_breaks"] = range(bottom, 0) + [0, ] + range(1, top)
    batch["scale_labels"] = [abs(x) for x in batch["scale_breaks"]]
variables_label = "Symbol"
limits = (-1, 35)
outcomes_label = "Outcomes"


def setup(subparser):
    """Set up the sub-command parser"""
    subcommand = subparser.add_parser(ruleset, help="%s ruleset" % title)


def prepare(parent_args, parent_srand):
    global args, srand
    args = parent_args
    srand = parent_srand


def simulate_rolls(variable):
    dice_chal, dice_diff, dice_prof, dice_abil, desc = dice_combos[variable]
    # Outcomes = {dice_combo: {batch: {symbol: {result: count}}}}
    outcomes = dict()
    for group in symbols:
        for s in symbols[group]:
            outcomes[s] = dict()
    # Simulate rolls
    for roll in xrange(args.rolls):
        results = dict()
        for group in symbols:
            results[group] = 0
        # Dice - Proficiency
        for d in xrange(dice_chal):
            failure, threat, despair = die_chal[srand.randint(1, 12)]
            results["fs"] -= failure
            results["ta"] -= threat
            results["d"] -= despair
        # Dice - Difficulty
        for d in xrange(dice_diff):
            failure, threat = die_diff[srand.randint(1, 8)]
            results["fs"] -= failure
            results["ta"] -= threat
        # Dice - Proficiency
        for d in xrange(dice_prof):
            success, advantage, triumph = die_prof[srand.randint(1, 12)]
            results["fs"] += success
            results["ta"] += advantage
            results["t"] += triumph
        # Dice - Ability
        for d in xrange(dice_abil):
            success, advantage = die_abil[srand.randint(1, 8)]
            results["fs"] += success
            results["ta"] += advantage
        # Update outcomes
        for group in symbols:
            result = results[group]
            for s in symbols[group]:
                # Massage results
                if s.endswith("Failure") and result > 0:
                    continue
                if s.endswith("Success") and result < 0:
                    continue
                if s.endswith("Threat") and result > 0:
                    continue
                if s.endswith("Advantage") and result < 0:
                    continue
                if s.endswith("Despair") and result == 0:
                    continue
                if s.endswith("Triumphs") and result == 0:
                    continue
                # Update
                if result not in outcomes[s]:
                    outcomes[s][result] = 1
                else:
                    outcomes[s][result] += 1
    # Organize data
    data = list()
    for group in symbols:
        for s in symbols[group]:
            for result in outcomes[s]:
                count = outcomes[s][result]
                percent = round((float(count) / float(args.rolls)) * 100, 1)
                data.append((variable, s, result, count, percent))
    return sorted(data)
