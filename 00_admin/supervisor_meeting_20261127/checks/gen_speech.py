import json, re, sys
deck = sys.argv[1]; out = sys.argv[2]
s = json.load(open(deck + "/speech.json"))
src = open(deck + "/build_deck.js").read()
titles = {int(m.group(1)): m.group(2) for m in re.finditer(r'// (\d+) .*?\n.*?s\.addText\("([^"]+)", \{ placeholder: "title" \}\)', src, re.S)}
words = {i: len(s["s%d" % i].split()) for i in titles}
tot = sum(words.values()); secs = tot / 130 * 60
L = ["# Speech: work status, November 2026", "",
     "To go with the deck chorismate_work_status_november_2026.pptx (the same text is in its speaker notes). About %d words: roughly %d minutes at an easy pace, leaving time for questions. Every number is the document's." % (round(tot, -2), round(secs / 60)),
     "Total at 130 words a minute: about %d min %02d s." % divmod(round(secs), 60), ""]
for i in sorted(titles):
    L += ["## Slide %d. %s (about %d s)" % (i, titles[i], round(words[i] / 130 * 60)), "", s["s%d" % i], ""]
open(out, "w").write("\n".join(L))
print(tot, divmod(round(secs), 60))
