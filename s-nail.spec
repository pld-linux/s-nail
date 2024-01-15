%bcond_without	tests
Summary:	Environment for sending and receiving mail, providing functionality of POSIX mailx
Name:		s-nail
Version:	14.9.24
Release:	1
# Everything is ISC except parts coming from the original Heirloom mailx which are BSD
License:	ISC AND BSD-4-Clause-UC AND BSD-3-Clause AND RSA-MD AND HPND-sell-variant
URL:		https://www.sdaoden.eu/code.html
Source0:	https://www.sdaoden.eu/downloads/%{name}-%{version}.tar.xz
# Source0-md5:	85dd87e5cbae851c4d7714b9fcc6a5d4
Source1:	https://www.sdaoden.eu/downloads/%{name}-%{version}.tar.xz.asc
# Source1-md5:	7d6ed6c0bf7aef83e4406c47efdca778
# https://bugzilla.redhat.com/show_bug.cgi?id=2171723
Patch0:		%{name}-makeflags.patch
BuildRequires:	heimdal-devel
BuildRequires:	libidn2-devel
BuildRequires:	ncurses-devel
BuildRequires:	openssl
BuildRequires:	openssl-devel
Provides:	mailx = %{version}-%{release}
Obsoletes:	mailx < 12.6
# For backwards compatibility
Provides:	/bin/mail
Provides:	/bin/mailx

%description
S-nail provides a simple and friendly environment for sending and
receiving mail. It is intended to provide the functionality of the
POSIX mailx(1) command, but is MIME capable and optionally offers
extensions for line editing, S/MIME, SMTP and POP3, among others.
S-nail divides incoming mail into its constituent messages and allows
the user to deal with them in any order. It offers many commands and
internal variables for manipulating messages and sending mail. It
provides the user simple editing capabilities to ease the composition
of outgoing messages, and increasingly powerful and reliable
non-interactive scripting capabilities.

%prep
%setup -q

cat <<EOF >>nail.rc
set bsdcompat
set noemptystart
set prompt='& '
EOF

%build
%{__make} \
	CFLAGS="%{rpmcppflags} %{rpmcflags}" \
	LDFLAGS="%{rpmldflags}" \
	OPT_AUTOCC=no \
	OPT_DEBUG=yes \
	OPT_NOMEMDBG=yes \
	OPT_DOTLOCK=no \
	VAL_PREFIX=%{_prefix} \
	VAL_SYSCONFDIR=%{_sysconfdir} \
	VAL_MAIL=%{_localstatedir}/mail \
	config

%{__make} build

%if %{with tests}
#export OPENSSL_ENABLE_SHA1_SIGNATURES=yes
%{__make} test
%endif



%install
rm -rf $RPM_BUILD_ROOT

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# s-nail binary is installed with 0555 permissions, fix that
chmod 0755 $RPM_BUILD_ROOT%{_bindir}/%{name}

# compatibility symlinks
for f in Mail mail mailx nail; do
    ln -s %{name} $RPM_BUILD_ROOT%{_bindir}/$f
    echo ".so %{name}.1" > $RPM_BUILD_ROOT%{_mandir}/man1/$f.1
done


%check
%if %{defined rhel}
# SHA-1 is disabled as insecure by RHEL default policies, but used in tests
export OPENSSL_ENABLE_SHA1_SIGNATURES=yes
%endif
make test

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(644,root,root,755)
%doc README
%attr(755,root,root) %{_bindir}/Mail
%attr(755,root,root) %{_bindir}/mail
%attr(755,root,root) %{_bindir}/nail
%attr(755,root,root) %{_bindir}/mailx
%attr(755,root,root) %{_bindir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}.rc
%{_mandir}/man1/Mail.1*
%{_mandir}/man1/mail.1*
%{_mandir}/man1/nail.1*
%{_mandir}/man1/mailx.1*
%{_mandir}/man1/%{name}.1*
