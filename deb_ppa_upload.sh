#!/bin/sh
# build a debian sourcepackage and upload it to the launchpad ppa
export GPGKEY=DA94BB53
export DEBEMAIL="richi@paraeasy.ch"
export DEBFULLNAME="Richard Ulrich"

for DISTRIBUTION in precise oneiric natty maverick 
do
	PRINTRUNVERSIONSTR=0.0.8~${DISTRIBUTION}
	sed -i  -e "s/maverick/${DISTRIBUTION}/g" -e "s/natty/${DISTRIBUTION}/g" -e "s/oneiric/${DISTRIBUTION}/g" -e "s/precise/${DISTRIBUTION}/g" debian/changelog
	dpkg-buildpackage -rfakeroot -S
	dput ppa:richi-paraeasy/ppa ../printrun_${PRINTRUNVERSIONSTR}_source.changes
done
