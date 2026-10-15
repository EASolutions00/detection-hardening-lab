# tools/word

Scripts that turn the Markdown proposal into the files the panel receives. Written in chat 27d2595d
(2026-10-07 to 2026-10-12) and moved here from that chat's temporary scratchpad on 2026-10-15, so they
are not lost.

None of them touches the code or the data. Python standard library only (no python-docx, no lxml).
The thesis folder path is written in each script (`E:\Elijah MASTER COPY DO NOT DELETE\Documents\New
folder (5)`, called DOCS below). Change it there if the folder moves.

| Script | Reads | Writes | Use again? |
|---|---|---|---|
| `final_to_html_v2.py` | `DOCS\proposal-form-FINAL.md` | `DOCS\proposal-form-FINAL-for-Word.html` | Yes, after every FINAL edit |
| `revisions_to_html.py` | `DOCS\T1-REVISIONS-LIST.md` | `DOCS\T1-REVISIONS-LIST-for-Word.html` | Yes, after every revisions-list edit |
| `diff_docx_md.py` | a `.docx` and a `.md` given as arguments | nothing (prints) | Yes, to check a Word file against FINAL |
| `pdf_pages.ps1` | a PDF | `page<N>.png` in the folder you give | Yes, to look at PDF pages |
| `build_docx.py` | the student's formatted `.docx`, FINAL, four figures | `DOCS\FINAL … (updated 2026-10-12).docx` | No. A record of how that file was made |

## The two HTML converters

Each one converts the Markdown to a plain HTML page. Open the page in a browser, select all, copy, and
paste into Word. Each script then checks that every word of the source appears in the HTML, in the
same order, and prints the count. A mismatch stops the script.

`final_to_html_v2.py` also requires exactly four `[INSERT FIGURE: <file>]` lines in FINAL (Figures 1 to
4). Version 1 of this script, in chat 5e235b74, had two built-in markers and is superseded.

```bash
.venv/Scripts/python.exe tools/word/final_to_html_v2.py
.venv/Scripts/python.exe tools/word/revisions_to_html.py
```

Correct result: one line each, starting `Wrote proposal-form-FINAL-for-Word.html:` or
`Wrote T1-REVISIONS-LIST-for-Word.html:`, with the counts of headings, paragraphs and words. They
overwrite the old HTML file, which is safe because the HTML is always made from the Markdown.

## diff_docx_md.py

Read-only. Prints every word that differs between a Word file and FINAL.

```bash
.venv/Scripts/python.exe tools/word/diff_docx_md.py "<file>.docx" "<folder>/proposal-form-FINAL.md"
```

## pdf_pages.ps1

The assistant's file reader cannot show PDF pages on this machine (no pdftoppm). This script uses the PDF renderer
built into Windows (Windows.Data.Pdf). It reads the PDF and writes PNG files only into the output
folder. The output folder must already exist. Run it inside Windows PowerShell, from the repo folder:

```
& .\tools\word\pdf_pages.ps1 -Pdf "<file>.pdf" -OutDir "<scratch folder>" -Pages (1..30)
```

Correct result: `PDF pages: 30`, then one `wrote page<N>.png` line per page. Do not start it through
`powershell -File`: that passes the page list as separate words, and only the first page is rendered
(found 2026-10-15).

## build_docx.py (one-off record)

Built the updated Word file of 2026-10-12 from a copy of the student's own formatted Word file, so the
student's formatting stayed. It replaced changed sentences inside their paragraphs, added the missing
sections in the student's paragraph format, and embedded the four figures as SVG with a PNG fallback.
Details are in its opening comment and in WORKLOG 2026-10-12 (second).

It refuses to run if the output file already exists, so it cannot overwrite the student's work. It
also needs a `docx_build` folder beside it holding each figure as `.svg` and `.png`. That folder is
not committed (`.gitignore`). To make it again:

1. Copy the four SVGs from `thesis/T1/figures/`.
2. Render each to PNG at its own size with Microsoft Edge in headless mode (DECISIONS 2026-09-14,
   "Correction to 2026-09-09"):
   `msedge.exe --headless=new --disable-gpu --hide-scrollbars --user-data-dir=<scratch> --screenshot=<name>.png --window-size=W,H file:///<path>.svg`
   Sizes used: Sheet 1 1800 x 2588, Sheet 2 1800 x 2304, pipeline 1020 x 878, noise floor 1060 x 400
   (each equals the SVG's own `viewBox`).

The student opened and saved the built file in Word after 2026-10-12 (Word renamed its pictures to
`image2.svg` and so on), and on 2026-10-15 saved it as `Detecting … Algorithm.docx`, the submitted
file. So **that Word file in DOCS is now the source**, and running this script again would lose any
hand edits. Checked 2026-10-15: the four pictures inside it are identical to the four SVGs in
`thesis/T1/figures/`.

**The template's hidden properties.** The school's blank template carries another thesis's title in
its Title property and "MaryASoriano" as Author, and the student's formatted file kept both, so the
built file did too. This script does not change `docProps/core.xml`. Set Title and Author in Word
(File, Info) before making a PDF; the PDF copies them into its metadata (found 2026-10-15).
