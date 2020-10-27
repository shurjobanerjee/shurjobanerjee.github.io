#!/usr/bin/env python
__author__ = 'shurjo'

import argparse
import json


def main(args):

    # Read news, pubs, and hotlinks into data structures.
    with open(args.news_fn, 'r') as f:
        news = json.load(f)
    with open(args.pubs_fn, 'r') as f:
        pubs = json.load(f)
    with open(args.coauthors_fn, 'r') as f:
        coauthors = json.load(f)

    # Prepare HTML and TeX outputs for data.

    # News output.
    aux_data = ["website", "slides", "video"]
    news_html_out = '<table class="table-sm"><tr><td colspan="4"><h4>News</h4></td></tr>'
    visible_news_items = 4
    for idx in range(len(news)):

        if idx > 0 and idx % visible_news_items == 0:
            jdx = idx // visible_news_items
            news_html_out += '</table>'
            news_html_out += ('<button type="button" class="btn btn-default" ' +
                              'data-toggle="collapse" data-target="#news' + str(jdx) +
                              '" onclick="$(this).hide()">Show more...</button>' +
                              '<div id="news' + str(jdx) + '" class="collapse"><table class="table-sm">')
            if jdx > 1:
                news_html_out += '</div>'

        nidx = str(len(news) - idx - 1)
        news_html_out += ('<tr><td class="col-md-3"><b>%s</b><br/>&nbsp;&nbsp;%s<td class="col-md-5">%s</td>' %
                          (news[nidx]["type"], news[nidx]["org"], news[nidx]["desc"]))
        news_html_out += '<td class="col-md-2">'
        aux = {}
        for aux_name in aux_data:
            if aux_name in news[nidx]:
                aux[aux_name] = news[nidx][aux_name]
        for aux_name in aux_data:
            if aux_name in aux:
                news_html_out += ('<a class="btn btn-default" style="padding:5px;" ' +
                                  'target="_blank" href="%s" onclick="captureOutboundLink(\'%s\');">%s</a>'
                                  % (aux[aux_name], aux[aux_name], aux_name))
        news_html_out += '</td><td class="col-md-2">%s</td></tr>' % news[nidx]["date"]
        news_html_out += "<tr><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td><td>&nbsp;</td></tr>"

    news_html_out += '</table>'
    if len(news) > visible_news_items:
        news_html_out += '</div>'

    # Publications outputs.
    pubs_html_out = ''
    pubs_tex_out = ''
    aux_data = ["paper", "website", "video", "demo", "source", "poster", "slides", "coverage"]
    bib_data = ["title", "author", "booktitle", "journal", "volume", "issue",
                "publisher", "school", "year", "doi", "paper"]  #"pages", month"
    bib_meta_rewrite = {"paper": "url"}
    for idx in range(len(pubs)):
        # Skip paperless headers (e.g., if we don't currently have preprints).
        if len(pubs[idx]['entries']) == 0:
            continue

        pubs_html_out += ('<div class="row"><div class="col-md-12"><table class="table-sm">' +
                          '<tr><td><h4>' + pubs[idx]["header"] + '</h4></td></tr>')
        pubs_tex_out += "{\sl " + pubs[idx]["header"] + "}\n\\begin{itemize}"

        papers_html_by_year = {}
        papers = pubs[idx]["entries"]
        for jdx in range(len(papers)):

            # Required fields.
            short = papers[jdx]["short"]
            bibtype = papers[jdx]["bibtype"]
            title = papers[jdx]["title"]
            bib_author = papers[jdx]["author"]
            year = papers[jdx]["year"]

            # Format author list.
            authors_html = bib_author.split(' and ')
            authors_tex = authors_html[:]
            for kdx in range(len(authors_html)):
                if authors_html[kdx] != "Shurjo Banerjee":
                    if authors_html[kdx] not in coauthors:
                        print("WARNING: author '%s' missing website link" % authors_html[kdx])
                    else:
                        authors_html[kdx] = '<a href="%s" style="color:#000000;" target="_blank" onclick="captureOutboundLink(\'%s\');">%s</a>' % (
                            coauthors[authors_html[kdx]]['website'], coauthors[authors_html[kdx]]['website'], authors_html[kdx])
            if len(authors_html) > 2:
                authorlist_html = ', '.join(authors_html[:-1])
                authorlist_html += ', and ' + authors_html[-1]
                authorlist_tex = ', '.join(authors_tex[:-1])
                authorlist_tex += ', and ' + authors_tex[-1]
            else:
                authorlist_html = ' and '.join(authors_html)
                authorlist_tex = ' and '.join(authors_tex)
            authorlist_html = authorlist_html.replace("Shurjo Banerjee", '<b style="color:RoyalBlue;">Shurjo Banerjee</b>')
            authorlist_tex = authorlist_tex.replace("Shurjo Banerjee", "{\\bf Shurjo Banerjee}")

            # Get bibtype-specific info.
            appearedin = None
            if bibtype == "inproceedings":
                appearedin = papers[jdx]["booktitle"]
            elif bibtype == "phdthesis":
                appearedin = papers[jdx]["school"]
            elif bibtype == "article":
                appearedin = papers[jdx]["journal"]
                if "volume" in papers[jdx]:
                    appearedin += " " + papers[jdx]["volume"]
                    if "issue" in papers[jdx]:
                        appearedin += "(" + papers[jdx]["issue"] + ")"

            # Get optional info.
            # pages = papers[njdx]["pages"] if "pages" in papers[njdx] else None
            # location = papers[njdx]["location"] if "location" in papers[njdx] else None
            # month = papers[njdx]["month"] if "month" in papers[njdx] else None
            pages = location = month = None  # no longer include pages, location, month

            # Get auxiliary links.
            aux = {}
            for aux_name in aux_data:
                if aux_name in papers[jdx]:
                    aux[aux_name] = papers[jdx][aux_name]

            # Create HTML entry.
            # Main entry.
            title_cleaned = title.replace("``", '"').replace("''", '"').replace("{", "").replace("}", "")
            html_title = title_cleaned.replace("&", "&amp;")
            paper_html = ('<tr><td style="padding:10px;">' +
                          '<b>' + html_title + '</b><br/>' + authorlist_html + '.<br/>' +
                          '<i>' + appearedin + '</i>, ')
            if pages is not None:
                paper_html += "pages " + pages + ", "
            if location is not None:
                paper_html += location + ", "
            if month is not None:
                paper_html += month + ' ' + year + '.<br/>'
            else:
                paper_html += year + '.<br/>'

            # Earlier appearances.
            early_aux = []
            if "early" in papers[jdx]:
                paper_html += "<span style=\"font-size:12px\">&mdash;<br/>"
                for early in papers[jdx]["early"]:
                    paper_html += "<span><i>Also presented at the</i> %s (%s), %s.<br/>" % \
                                  (early["title"], early["acronym"], early["year"])
                    for aux_name in aux_data:
                        if aux_name in early:
                            early_aux.append('<a class="btn btn-default" style="padding:5px;" ' +
                                             'target="_blank" href="%s" ' % early[aux_name] +
                                             'onclick="captureOutboundLink(\'%s\');">%s %s</a>' %
                                             (early[aux_name], early["acronym"], aux_name))
                paper_html += "</span>";

            # Publication attachments (paper, video, etc., followed by bib, then early pub links)
            for aux_name in aux_data:
                if aux_name in aux:
                    paper_html += ('<a class="btn btn-default" style="padding:5px;" ' +
                                   'target="_blank" href="%s" onclick="captureOutboundLink(\'%s\');">%s</a>'
                                   % (aux[aux_name], aux[aux_name], aux_name))

            # Add bib entry to HTML.
            bib_pieces = []
            for bib_name in bib_data:
                if bib_name in papers[jdx]:
                    if bib_name in bib_meta_rewrite:
                        bib_meta_name = bib_meta_rewrite[bib_name]
                    else:
                        bib_meta_name = bib_name 
                    bib_pieces.append('&nbsp;&nbsp;' + bib_meta_name + '={' + papers[jdx][bib_name].replace("&", "\&") + '}')
            bibshort = short.replace(":", "_")  # illegal as data-target?
            paper_html += ('<button type="button" class="btn btn-default" style="padding:5px;" ' +
                           'data-toggle="collapse" data-target="#' + bibshort + '">bib</button>' +
                           '<div id="' + bibshort +
                           '" class="collapse bib">' +
                           '@' + bibtype + '{' + short + ',<br/>')
            paper_html += ',<br/>'.join(bib_pieces) + '<br/>}</div>'

            # Publication attachments from earlier appearances.
            if len(early_aux) > 0:
                paper_html += " | "
                paper_html += ''.join(early_aux)

            # Close up entry.
            paper_html += "</td></tr>"

            # Add paper entry to year structure.
            if year not in papers_html_by_year:
                papers_html_by_year[year] = []
            papers_html_by_year[year].append(paper_html)

            # Create Tex entry.
            tex_title = title_cleaned.replace("&", "\&")
            if 'paper' in papers[jdx]:
                pubs_tex_out += "\item \citehref{%s}{%s}\\\\%s.\\\\\\textit{%s}, %s.\n" % \
                                    (papers[jdx]['paper'], tex_title, authorlist_tex, appearedin, year)
            else:
                pubs_tex_out += "\item %s\\\\%s.\\\\\\textit{%s}, %s.\n" % \
                                    (tex_title, authorlist_tex, appearedin, year)

        # Build HTML output sorted by year.
        sorted_years = sorted(list(papers_html_by_year.keys()), reverse=True)
        for year in sorted_years:
            pubs_html_out += "<tr><td><b>%s</b></td></tr>" % year
            for paper_html in papers_html_by_year[year]:
                pubs_html_out += paper_html

        pubs_html_out += "</table></div></div>"
        pubs_tex_out += "\end{itemize}"

    # Write HTML and TeX outputs.
    with open(args.target_html, 'w') as f_out:
        with open(args.base_html, 'r') as f_in:
            for line in f_in.readlines():
                if line.strip() == "#NEWS#":
                    f_out.write(news_html_out + '\n')
                elif line.strip() == "#PUBS#":
                    f_out.write(pubs_html_out + '\n')
                else:
                    f_out.write(line)
    with open(args.target_tex, 'w') as f_out:
        with open(args.base_tex, 'r') as f_in:
            for line in f_in.readlines():
                if line.strip() == "#PUBS#":
                    f_out.write(pubs_tex_out + '\n')
                else:
                    f_out.write(line)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--news_fn', type=str, required=True,
                        help="news source file")
    parser.add_argument('--pubs_fn', type=str, required=True,
                        help="publications source file")
    parser.add_argument('--coauthors_fn', type=str, required=True,
                        help="links source file")
    parser.add_argument('--base_html', type=str, required=True,
                        help="the base html file")
    parser.add_argument('--base_tex', type=str, required=True,
                        help="the base tex file")
    parser.add_argument('--target_html', type=str, required=True,
                        help="the output html file")
    parser.add_argument('--target_tex', type=str, required=True,
                        help="the output tex file")
    main(parser.parse_args())
