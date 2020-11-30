Name:       {{{ git_dir_name }}}
# The git_dir_version macro is quite a mis-match for our use-case
# since using a 3-component version number requires updating
# the 'lead' parameter, anyways
# cf. https://pagure.io/rpkg-util/issue/21#comment-601077
#Version:    {{{ git_dir_version }}}
Version:    1.5.11
Release:    1%{?dist}
Summary:    Photo and video sorting tool
URL:        https://github.com/ivandokov/phockup
License:    MIT
VCS:        {{{ git_dir_vcs }}}
Source:     {{{ git_dir_pack }}}
BuildArch:  noarch
Requires:   perl-Image-ExifTool

%description
Media sorting tool to organize photos and videos from your camera in folders by year, month and day.
The software will collect all files from the input directory and copy them to the output directory without
changing the files content. It will only rename the files and place them in the proper directory for year, month and day.

%prep
{{{ git_dir_setup_macro }}}

%build
# nothing to do here

%install
install -D phockup.py %{buildroot}/usr/lib/phockup/phockup.py
install -D src/__init__.py %{buildroot}/usr/lib/phockup/src/__init__.py
install -D src/date.py %{buildroot}/usr/lib/phockup/src/date.py
install -D src/dependency.py %{buildroot}/usr/lib/phockup/src/dependency.py
install -D src/exif.py %{buildroot}/usr/lib/phockup/src/exif.py
install -D src/help.py %{buildroot}/usr/lib/phockup/src/help.py
install -D src/phockup.py %{buildroot}/usr/lib/phockup/src/phockup.py
install -D src/printer.py %{buildroot}/usr/lib/phockup/src/printer.py
install -D license %{buildroot}/usr/lib/phockup/license
install -D phockup-rpm.sh %{buildroot}/usr/bin/phockup

%files
/usr/lib/phockup/*
/usr/bin/phockup
%doc readme.md

%changelog
* Sun Nov 29 2020 Akos Balla <akos.balla@sirc.hu> - 1.5.11-1
- create RPM spec file
