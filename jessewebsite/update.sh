python source/generate.py --news_fn source/news.json --pubs_fn source/publications.json --coauthors_fn source/coauthors.json --base_html source/base.html --base_tex source/base.tex --target_html www/index.html --target_tex cv/cv.tex
cp -r www/* .. 
#cd cv/
#pdflatex cv.tex
#mv cv.pdf ../www/jesse_thomason_cv.pdf
