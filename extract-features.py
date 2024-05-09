#! /usr/bin/python3

import sys, os
from xml.dom.minidom import parse

# folder where this file is located
THISDIR = os.path.abspath(os.path.dirname(__file__))
# go two folders up and locate "util" folder there
LABDIR = os.path.dirname(os.path.dirname(THISDIR))
UTILDIR = os.path.join(LABDIR, "util")
# add "util" to search path so python can find "deptree"
sys.path.append(UTILDIR)

from util.deptree import *
import patterns


## -------------------
## -- Convert a pair of drugs and their context in a feature vector


def extract_features(tree, entities, e1, e2):
    feats = set()

    # get head token for each gold entity
    tkE1 = tree.get_fragment_head(entities[e1]["start"], entities[e1]["end"])
    tkE2 = tree.get_fragment_head(entities[e2]["start"], entities[e2]["end"])

    if tkE1 is not None and tkE2 is not None:

        # features for tokens in between E1 and E2
        for tk in range(tkE1 + 1, tkE2):
            if not tree.is_stopword(tk):
                word = tree.get_word(tk)
                lemma = tree.get_lemma(tk).lower()
                tag = tree.get_tag(tk)
                feats.add("lib=" + lemma)
                feats.add("wib=" + word)
                feats.add("lpib=" + lemma + "_" + tag)

                # feature indicating the presence of an entity in between E1 and E2
                if tree.is_entity(tk, entities):
                    feats.add("eib")

        # features about paths in the tree
        lcs = tree.get_LCS(tkE1, tkE2)

        path1 = tree.get_up_path(tkE1, lcs)
        path1 = "<".join([tree.get_lemma(x) + "_" + tree.get_rel(x) for x in path1])
        feats.add("path1=" + path1)

        path2 = tree.get_down_path(lcs, tkE2)
        path2 = ">".join([tree.get_lemma(x) + "_" + tree.get_rel(x) for x in path2])
        feats.add("path2=" + path2)

        path = path1 + "<" + tree.get_lemma(lcs) + "_" + tree.get_rel(lcs) + ">" + path2
        feats.add("path=" + path)

        lemma = patterns.check_LCS_svo(tree, tkE1, tkE2)
        if lemma is not None:
            feats.add("LCS_svo=" + lemma)

        # New Features

        # v1
        # Words before E1 and after E2
        nodes = tree.get_nodes()
        for tk in nodes:
            if tk < tkE1 and not tree.is_stopword(tk):
                feats.add("beforeE1=" + tree.get_lemma(tk).lower())
            if tk > tkE2 and not tree.is_stopword(tk):
                feats.add("afterE2=" + tree.get_lemma(tk).lower())

        # v2
        # LCS information
        lcs_lemma = tree.get_lemma(lcs).lower()
        lcs_pos = tree.get_tag(lcs)
        feats.add("lcs_lemma=" + lcs_lemma)
        feats.add("lcs_pos=" + lcs_pos)

        # v3
        # Feature for the parent node of E1 and E2
        if tkE1 is not None:
            parentE1 = tree.get_parent(tkE1)
            if parentE1 is not None:
                feats.add("parentE1_lemma=" + tree.get_lemma(parentE1))
                feats.add("parentE1_rel=" + tree.get_rel(parentE1))
                feats.add("parentE1_pos=" + tree.get_tag(parentE1))

        if tkE2 is not None:
            parentE2 = tree.get_parent(tkE2)
            if parentE2 is not None:
                feats.add("parentE2_lemma=" + tree.get_lemma(parentE2))
                feats.add("parentE2_rel=" + tree.get_rel(parentE2))
                feats.add("parentE2_pos=" + tree.get_tag(parentE2))

        # v4
        # different paths

        path1 = tree.get_up_path(tkE1, lcs)
        path2 = tree.get_down_path(lcs, tkE2)

        # path with just lemmas
        # This simplifies the path features by only including the lemmas of the nodes in the paths, excluding syntactic relations or POS tags. This can provide a clearer focus on the lexical content of the paths:

        lemma_path1 = "<".join([tree.get_lemma(x) for x in path1])
        feats.add("lemma_path1=" + lemma_path1)

        lemma_path2 = ">".join([tree.get_lemma(x) for x in path2])
        feats.add("lemma_path2=" + lemma_path2)

        # Combined path without syntactic relations or POS tags
        if path1 and path2:
            lemma_full_path = (
                lemma_path1 + "<" + tree.get_lemma(lcs) + ">" + lemma_path2
            )
            feats.add("lemma_full_path=" + lemma_full_path)

        # detailed path with pos
        # Including POS tags along with lemmas in the path can provide syntactic context that may be critical for understanding the nature of the interaction. This is more detailed than the base path feature:

        detailed_path1 = "<".join(
            [tree.get_lemma(x) + "_" + tree.get_tag(x) for x in path1]
        )
        feats.add("detailed_path1=" + detailed_path1)

        detailed_path2 = ">".join(
            [tree.get_lemma(x) + "_" + tree.get_tag(x) for x in path2]
        )
        feats.add("detailed_path2=" + detailed_path2)

        # Combined path with POS tags
        if path1 and path2:
            detailed_full_path = (
                detailed_path1
                + "<"
                + tree.get_lemma(lcs)
                + "_"
                + tree.get_tag(lcs)
                + ">"
                + detailed_path2
            )
            feats.add("detailed_full_path=" + detailed_full_path)

    return feats


## --------- MAIN PROGRAM -----------
## --
## -- Usage:  extract_features targetdir
## --
## -- Extracts feature vectors for DD interaction pairs from all XML files in target-dir
## --

# directory with files to process
datadir = sys.argv[1]

# process each file in directory
for f in os.listdir(datadir):

    # parse XML file, obtaining a DOM tree
    tree = parse(datadir + "/" + f)

    # process each sentence in the file
    sentences = tree.getElementsByTagName("sentence")
    for s in sentences:
        sid = s.attributes["id"].value  # get sentence id
        stext = s.attributes["text"].value  # get sentence text
        # load sentence entities
        entities = {}
        ents = s.getElementsByTagName("entity")
        for e in ents:
            id = e.attributes["id"].value
            offs = e.attributes["charOffset"].value.split("-")
            entities[id] = {"start": int(offs[0]), "end": int(offs[-1])}

        # there are no entity pairs, skip sentence
        if len(entities) <= 1:
            continue

        # analyze sentence
        analysis = deptree(stext)

        # for each pair in the sentence, decide whether it is DDI and its type
        pairs = s.getElementsByTagName("pair")
        for p in pairs:
            # ground truth
            ddi = p.attributes["ddi"].value
            if ddi == "true":
                dditype = p.attributes["type"].value
            else:
                dditype = "null"
            # target entities
            id_e1 = p.attributes["e1"].value
            id_e2 = p.attributes["e2"].value
            # feature extraction

            feats = extract_features(analysis, entities, id_e1, id_e2)
            # resulting vector
            print(sid, id_e1, id_e2, dditype, "\t".join(feats), sep="\t")
