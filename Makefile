all: build/s4f-regionalgruppen-logos.zip


build/bars.pdf: plot_bars.py | build
	python plot_bars.py


build/s4f_logo_dortmund.pdf: regionalgruppen.txt build/bars.pdf logo.tex create_logos.py
	python create_logos.py


build/s4f-regionalgruppen-logos.zip: build/s4f_logo_dortmund.pdf
	rm -rf build/s4f-regionalgruppen-logos
	rm -rf build/s4f-regionalgruppen-logos.zip
	mkdir build/s4f-regionalgruppen-logos
	cp build/*.pdf build/s4f-regionalgruppen-logos
	cp build/*.svg build/s4f-regionalgruppen-logos
	cp build/*.png build/s4f-regionalgruppen-logos

	cd build && zip -r s4f-regionalgruppen-logos.zip s4f-regionalgruppen-logos



build:
	mkdir -p build

clean:
	rm -rf build

