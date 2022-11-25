#%%
import markdown
import argparse as ap
from pathlib import Path
import re
from html.parser import HTMLParser
from html.entities import name2codepoint
#%%
ags = ap.ArgumentParser("md2tex")
ags.add_argument("-f", help="Full file path", required=True)
ags.add_argument("-d", help="Insert default formatting code", action='store_true')
aps = ags.parse_args()

f_name = Path(aps.f)
#%%
class MyHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.attrs = []
    def handle_starttag(self, tag, attrs):
        for attr in attrs:
            self.attrs.append(attr)
    def get_attrs(self):
        return self.attrs
    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        print("Data     :", data)

    def handle_comment(self, data):
        print("Comment  :", data)

    def handle_entityref(self, name):
        c = chr(name2codepoint[name])
        print("Named ent:", c)

    def handle_charref(self, name):
        if name.startswith('x'):
            c = chr(int(name[1:], 16))
        else:
            c = chr(int(name))
        print("Num ent  :", c)

    def handle_decl(self, data):
        print("Decl     :", data)

default_template = """
\\documentclass[12pt]{article}
\\usepackage[a4paper, total={6in, 8in}]{geometry}
\\usepackage[utf8]{inputenc}
\\usepackage[T1]{fontenc}
\\usepackage[english]{babel}
\\usepackage{graphicx}
\\usepackage[dvipsnames]{xcolor}
\\usepackage{hyperref}
\\usepackage{listings}

\\newcommand\myshade{85}
\\colorlet{mylinkcolor}{violet}
\\colorlet{mycitecolor}{YellowOrange}
\\colorlet{myurlcolor}{Aquamarine}

\\hypersetup{
  linkcolor  = mylinkcolor!\\myshade!black,
  citecolor  = mycitecolor!\\myshade!black,
  urlcolor   = myurlcolor!\\myshade!black,
  colorlinks = true,
}
\\author{}
"""
#%%
def add_end_brace(list_of_vals, replacer_dict):
    list_of_vals = [x.strip() for x in list_of_vals.split(",")]
    for i in list_of_vals:
        replacer_dict[i.replace("<", "</")] = "}\n"

replacer_dict = {
    "<head>" : "",
    "</head>" : "",
    "<html>" : "",
    "</html>" : "",
    "<p>" : "",
    "</p>" : "",
    "<h1>" : "\\begin{document}\n\\title{",
    "</h1>" : "}\n\\maketitle{}\n",
    "<h2>" : "\\section{",
    "<h3>" : "\\subsection{",
    "<h4>" : "\\subsubsection{",
    # "<body>" : "\\begin{document}\n",
    "</body>" : "\\end{document}\n",
    "<ul>" : "\\begin{itemize}\n",
    "</ul>" : "\\end{itemize}\n",
    "<il>" : "\\begin{enumerate}\n",
    "</il>" : "\\end{enumerate}\n",
    "<code>" : "\\begin{lstlisting}[language=Python]\n",
    "</code>" : "\\end{lstlisting}\n",
    "<li>" : "\\item ",
    "</li>" : "",
    "%": "\%",
    "&": "\&",
}
add_end_brace(
    list_of_vals="<h2>, <h3>, <h4>", 
    replacer_dict=replacer_dict
)

def get_html_attributes(text):
    parser = MyHTMLParser()
    parser.feed(text)
    return parser.get_attrs()

#%%
def figure_code(text):
    found_links = re.findall('\<img .* \/>' , text)
    for link in found_links:
        attrs = get_html_attributes(link)
        caption_data = ""
        file_path = ""
        for i in attrs:
            if i[0] == "alt":
                caption_data = i[1]
            if i[0] == "src":
                file_path = i[1]
        gen_latex = "\\begin{figure}[!htbp]\n\centering\n\includegraphics[width=.75\columnwidth]{"+file_path+"}\n\caption{"+caption_data+"}\n\label{}\n\end{figure}"
        text = text.replace(link, gen_latex)
    return text
#%%
with open(f_name, 'r') as f:
    text = f.read()
    html = markdown.markdown(text)
#%%
# Replacing things
text = figure_code(html)
for key in replacer_dict.keys():
    text = text.replace(key, replacer_dict[key])

#%%
with open(f_name.parent/f"{f_name.stem}.tex", 'w') as f:
    if aps.d:
        f.write(default_template)
    f.write(text)
    if aps.d:
        f.write("\\end{document}")

# %%
