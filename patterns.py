## -------------------
## -- check pattern:  LCS is a verb, one entity is under its "nsubj" and the other under its "obj"


# added 'include' as a lemma for class 'effect'
def check_LCS_svo(tree, tkE1, tkE2):

    if tkE1 is not None and tkE2 is not None:
        lcs = tree.get_LCS(tkE1, tkE2)

        if tree.get_tag(lcs)[0:2] == "VB":
            path1 = tree.get_up_path(tkE1, lcs)
            path2 = tree.get_up_path(tkE2, lcs)
            func1 = tree.get_rel(path1[-1]) if path1 else None
            func2 = tree.get_rel(path2[-1]) if path2 else None

            if (func1 == "nsubj" and func2 == "obj") or (
                func1 == "obj" and func2 == "nsubj"
            ):
                lemma = tree.get_lemma(lcs).lower()
                if lemma in [
                    "diminish",
                    "augment",
                    "exhibit",
                    "experience",
                    "counteract",
                    "potentiate",
                    "enhance",
                    "reduce",
                    "antagonize",
                    "include",
                ]:
                    return "effect"
                if lemma in [
                    "impair",
                    "inhibit",
                    "displace",
                    "accelerate",
                    "bind",
                    "induce",
                    "decrease",
                    "elevate",
                    "delay",
                ]:
                    return "mechanism"
                if lemma in ["exceed"]:
                    return "advise"
                if lemma in ["suggest"]:
                    return "int"

    return None


## -------------------
## -- check pattern:  A word in between both entities belongs to certain list


# added 'increase' as a wib lemma for class 'mechanism'
def check_wib(tree, tkE1, tkE2, entities, e1, e2):

    if tkE1 is not None and tkE2 is not None:
        # get actual start/end of both entities
        l1, r1 = entities[e1]["start"], entities[e1]["end"]
        l2, r2 = entities[e2]["start"], entities[e2]["end"]

        p = []
        for t in range(tkE1 + 1, tkE2):
            # get token span
            l, r = tree.get_offset_span(t)
            # if the token is in between both entities
            if r1 < l and r < l2:
                lemma = tree.get_lemma(t).lower()
                if lemma in [
                    "tendency",
                    "stimulate",
                    "regulate",
                    "prostate",
                    "modification",
                    "augment",
                    "accentuate",
                    "exacerbate",
                ]:
                    return "effect"
                if lemma in [
                    "react",
                    "faster",
                    "presumably",
                    "induction",
                    "substantially",
                    "minimally",
                    "increase",
                ]:
                    return "mechanism"
                if lemma in ["exceed", "extreme", "cautiously"]:
                    return "advise"
                if lemma in ["interact"]:
                    return "int"

    return None


# -----------------
# check pattern - SUGGESTION 1:  LCS is a verb with child being "should"
def check_LCS_verb_with_should_child(tree, tkE1, tkE2):
    if tkE1 is not None and tkE2 is not None:
        lcs = tree.get_LCS(tkE1, tkE2)

        # Ensure the LCS is a verb
        if tree.get_tag(lcs)[0:2] == "VB":
            # Check all children of LCS for a 'should' modifier
            for child in tree.get_children(lcs):
                if tree.get_lemma(child).lower() == "should":
                    return "advise"

    return None


# Refined should_child pattern for class 'advise'
def check_LCS_verb_with_should_child_refined(tree, tkE1, tkE2):

    advise_verbs = {
        "administer",
        "adjust",
        "use",
        "take",
        "avoid",
        "discontinue",
        "prescribe",
        "exceed",
        "consider",
        "withdraw",
        "defer",
        "observe",
        "allow",
        "reduce",
        "treat",
        "titrate",
        "interrupt",
        "advise",
        "give",
        "warn",
        "combine",
        "evaluate",
    }

    if tkE1 is not None and tkE2 is not None:
        lcs = tree.get_LCS(tkE1, tkE2)

        if tree.get_tag(lcs).startswith("VB"):
            for child in tree.get_children(lcs):
                if tree.get_lemma(child).lower() == "should":
                    verb_lemma = tree.get_lemma(lcs).lower()
                    if verb_lemma in advise_verbs:
                        return "advise"

    return None
