paper:  kawakami_qe.tex  tex tex/**/*.tex *.bib
	pdflatex kawakami_qe.tex
	bibtex  kawakami_qe
	pdflatex kawakami_qe.tex
	pdflatex kawakami_qe.tex

clean:
	rm -f *.aux *.bbl *.blg *.log *.out *.toc *.pdf
