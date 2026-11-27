# Supervisor meeting of 27 November 2026: the documents as given

Committed on 27 November 2026 at Jessica's request ("commit everything"), as a snapshot of what was prepared for
the meeting. Until now the reading copies were not committed; this folder is the first. Nothing here is edited
after this commit: a later version goes into a new folder.

Every number in these documents is drawn from the results repository at commit `173668c6` (the D60 result).
Where they say that D60 NOTE 1 was "sent for commit on 26 November", the note was committed before this folder
(`phase2.2/cs_stage6/STAGE6_DIAGNOSTIC60_NOTE1_20261126.txt`).

## The documents

| file | what it is |
|---|---|
| `Charge_design_work_status_November_2026.pdf` | The November document for the supervisor: a Claude Doc at revision 100, exported to A4 PDF (24 pages). |
| `Charge_design_work_status_November_2026.md` | The same revision exported as markdown, for reading as text and for the checks. Its pictures are only in the PDF. |
| `chorismate_work_status_november_2026.pptx` | The deck (12 slides), built with pptxgenjs; it passed the deck validator. The speech is in its speaker notes. |
| `chorismate_work_status_november_2026.pdf` | The deck converted to PDF by LibreOffice. |
| `speech_work_status_november_2026.md` | The speech: the same text as the speaker notes, with a time per slide at 130 words a minute (about 10 min 49 s). |
| `WHERE_THE_WORK_STANDS_20261126_v11.pdf` | The short document, version 11 (35 pages): Jessica's reading copy, with run names. |
| `WHERE_THE_WORK_STANDS_20261126_v11.md` | Its markdown source. |

## The checks (`checks/`)

| file | what it shows |
|---|---|
| `check_short_on_november_doc_rev100.txt` | The November document before its Appendix C: 7 of 7 quotations found word for word in a committed file; 170 of 170 decimal numbers traced to a committed file or to a figure script's printed output. |
| `check_short_on_short_doc_v11.txt` | The short document: 65 of 65 quotations; 741 of 741 decimal numbers (82 named files). |
| `verify_v8_on_v11_output.txt`, `verify_v7_on_v11_output.txt` | The short document's statements recomputed from the one committed file each rests on: 51 of 51 and 58 of 58. |
| `verify_lit_on_v11_output.txt` | Each sentence that cites a paper set against words in that paper's text in the library `chorismate-refs` at `cd287bb`: 34 of 34. |
| `indep_check_d60.py`, `indep_check_d60_output.txt` | D60 recomputed from its committed outputs with its own parsing and none of the committed reader's functions: 46 of 46. |
| `make_fig7.py`, `make_fig7_output.txt` | The script that draws Figure 7 of the November document (Figure 8 of the short document) from `d60_designs.tsv` and `d60_null.tsv`, and its printed output, which holds the derived numbers. |
| `patch_v11.py` | The changes from version 10.1 to version 11 of the short document. |
| `gen_speech.py` | Writes the speech file from the deck's speaker notes. |

`check_short.py`, `verify_v7.py`, `verify_v8.py` and `verify_lit_v10.py` are the scripts kept with the short
document's source since version 7; they are not repeated here. All the checks are Claude's; no second person has read
the documents.

`SHA256SUMS` lists the sha256 of every other file in this folder.
