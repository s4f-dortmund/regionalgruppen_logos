all: build/s4f-regionalgruppen-logos.zip


s4f-regionalgruppen-logos/dortmund/s4f_logo_dortmund.pdf: regionalgruppen.txt logo.tex create_logos.py
	python create_logos.py


build/s4f-regionalgruppen-logos.zip: s4f-regionalgruppen-logos/dortmund/s4f_logo_dortmund.pdf
	zip -r s4f-regionalgruppen-logos.zip s4f-regionalgruppen-logos

clean:
	rm -rf s4f-regionalgruppen-logos s4f-regionalgruppen-logos.zip

